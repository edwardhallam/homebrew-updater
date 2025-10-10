#!/usr/bin/env bash
# Homebrew: upgrade everything (formulae + casks), auto-heal ghost casks,
# keep sudo alive for passworded helper installs, and log everything.
#
# Usage:
#   ./brew-upgrade-all.sh                # normal run
#   ./brew-upgrade-all.sh --dry-run      # show what would update and what would be healed
#   ./brew-upgrade-all.sh --no-greedy    # skip forcing auto-updating casks
#   ./brew-upgrade-all.sh --no-cleanup   # skip cleanup at the end
#   ./brew-upgrade-all.sh --no-heal      # skip ghost auto-healing preflight
#
# Notes:
# - Never run `brew` with sudo. We only warm up sudo so that casks that ask the system
#   for privilege (helpers, /Applications writes, LaunchDaemons) won't interrupt the run.
# - macOS only.

set -euo pipefail

log()  { printf "\033[1;34m[brew-upgrade]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m[error]\033[0m %s\n" "$*" >&2; }

if [[ "$(uname -s)" != "Darwin" ]]; then
  err "This script targets macOS (Darwin). Exiting."
  exit 1
fi

# Locate brew
BREW=""
if command -v brew >/dev/null 2>&1; then
  BREW="$(command -v brew)"
elif [[ -x /opt/homebrew/bin/brew ]]; then
  BREW="/opt/homebrew/bin/brew"
elif [[ -x /usr/local/bin/brew ]]; then
  BREW="/usr/local/bin/brew"
fi
[[ -n "${BREW}" ]] || { err "Homebrew not found. Install from https://brew.sh"; exit 1; }
log "Using Homebrew at: ${BREW}"

# Args
DRY_RUN=0
GREEDY=1
CLEANUP=1
HEAL=1
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --no-greedy) GREEDY=0 ;;
    --no-cleanup) CLEANUP=0 ;;
    --no-heal) HEAL=0 ;;
    -*)
      warn "Unknown flag: $arg"
      ;;
  esac
done

# Logging
LOG_DIR="${HOME}/Library/Logs"
mkdir -p "${LOG_DIR}"
STAMP="$(date +"%Y%m%d-%H%M%S")"
LOG_FILE="${LOG_DIR}/brew-upgrade-${STAMP}.log"
touch "${LOG_FILE}"
log "Logging to: ${LOG_FILE}"

run() {
  if [[ ${DRY_RUN} -eq 1 ]]; then
    log "[dry-run] $*"
  else
    log "$*"
    { eval "$@" 2>&1 | tee -a "${LOG_FILE}"; } || {
      err "Command failed: $* (see log ${LOG_FILE})"
      return 1
    }
  fi
}

# Sudo warmup (optional but nice for passworded helpers)
if command -v sudo >/dev/null 2>&1; then
  if sudo -vn >/dev/null 2>&1; then
    log "sudo already authenticated; keeping it alive during the run."
  else
    log "Requesting sudo once to allow privileged helper changes to proceed without prompts..."
    sudo -v || warn "Could not authenticate sudo. Proceeding without it (some casks may prompt)."
  fi
  if sudo -vn >/dev/null 2>&1; then
    trap 'kill "$SUDO_KEEPALIVE_PID" >/dev/null 2>&1 || true' EXIT
    ( while true; do sudo -n true >/dev/null 2>&1 || exit; sleep 60; done ) &
    SUDO_KEEPALIVE_PID=$!
  fi
fi

# --------- Ghost auto-heal ---------
# Strategy:
# 1) Use `brew list --cask` as the ground truth of what Homebrew *thinks* is installed.
# 2) For each cask:
#    - If Caskroom dir has stale ".upgrading" or empty version dirs, purge them.
#    - If jq is present, query app artifacts via `brew info --cask --json=v2 <cask>`
#      and verify the installed .app bundles exist in /Applications or ~/Applications.
#      If all artifacts are missing, force uninstall --zap to remove the ghost.
#    - If jq is not present, fall back to heuristics: if Caskroom exists but has no
#      current version dir or the expected app symlink is missing, force uninstall.
#
heal_ghosts() {
  local CR="$("${BREW}" --caskroom 2>/dev/null || echo /opt/homebrew/Caskroom)"
  local HAVE_JQ=0
  if command -v jq >/dev/null 2>&1; then HAVE_JQ=1; fi

  log "Scanning for ghost casks (auto-heal preflight)..."
  # shellcheck disable=SC2207
  local CASKS=($("${BREW}" list --cask 2>/dev/null || true))
  for c in "${CASKS[@]:-}"; do
    # Skip fonts & quicklook plugins (often no .app artifacts)
    if [[ "$c" == font-* ]] || [[ "$c" == ql* ]]; then
      continue
    fi

    local CASK_DIR="${CR}/${c}"
    local GHOST=0

    # If Caskroom dir exists, nuke any "*.upgrading" partials and empty version dirs
    if [[ -d "$CASK_DIR" ]]; then
      # Remove partial state dirs that break future upgrades
      if compgen -G "${CASK_DIR}"/*/*.upgrading >/dev/null; then
        run "sudo rm -rf \"${CASK_DIR}\"/*/*.upgrading"
      fi
      # Remove zero-byte receipts / empty dirs
      find "$CASK_DIR" -type d -empty -maxdepth 2 -mindepth 2 -print -exec bash -lc '[[ $DRY_RUN -eq 1 ]] && echo "[dry-run] rmdir -p \"{}\"" || rmdir -p "{}" || true' \; 2>/dev/null | tee -a "${LOG_FILE}" >/dev/null || true
    fi

    if [[ ${HAVE_JQ} -eq 1 ]]; then
      # Query expected artifacts; if none exist, treat as ghost
      local APPS_JSON
      if ! APPS_JSON="$("${BREW}" info --cask --json=v2 "$c" 2>/dev/null | jq -r '.[0] | {name:.token, apps:([.artifacts[]?|objects|.app? // empty]|flatten)}')" ; then
        continue
      fi
      local APPS
      APPS=$(printf '%s\n' "${APPS_JSON}" | jq -r '.apps[]?' 2>/dev/null || true)
      if [[ -n "${APPS}" ]]; then
        local FOUND=0
        while IFS= read -r appname; do
          [[ -z "$appname" ]] && continue
          if [[ -e "/Applications/${appname}" || -e "$HOME/Applications/${appname}" ]]; then
            FOUND=1; break
          fi
        done <<< "${APPS}"
        if [[ ${FOUND} -eq 0 ]]; then
          GHOST=1
        fi
      else
        # No app artifacts reported; fall back to presence of Caskroom dir
        if [[ ! -d "$CASK_DIR" ]]; then
          GHOST=1
        fi
      fi
    else
      # Heuristic without jq: if Caskroom dir exists but there's no .app in /Applications matching token-ish patterns, we still attempt a defensive uninstall.
      # This is conservative to avoid false positives.
      if [[ -d "$CASK_DIR" ]]; then
        # If there are no version subdirs, consider it stale
        if ! find "$CASK_DIR" -mindepth 1 -maxdepth 1 -type d | read -r _; then
          GHOST=1
        fi
      else
        GHOST=1
      fi
    fi

    if [[ ${GHOST} -eq 1 ]]; then
      log "Auto-heal: found ghost cask '${c}'. Forcing uninstall with zap."
      if [[ ${DRY_RUN} -eq 1 ]]; then
        log "[dry-run] ${BREW} uninstall --cask --force --zap ${c}"
      else
        "${BREW}" uninstall --cask --force --zap "${c}" || true
        # Extra safety: remove leftover Caskroom dir if still present
        if [[ -d "$CASK_DIR" ]]; then
          run "sudo rm -rf \"${CASK_DIR}\""
        fi
      fi
    fi
  done

  # After healing, a short cleanup helps
  if [[ ${CLEANUP} -eq 1 ]]; then
    run "${BREW} cleanup -s"
  fi
}

# --------- Preflight & upgrade ---------
run "${BREW} update"

# Optionally heal ghosts before upgrades
if [[ ${HEAL} -eq 1 ]]; then
  heal_ghosts
fi

# Show what's outdated
if [[ ${DRY_RUN} -eq 1 ]]; then
  run "${BREW} outdated --formula"
  run "${BREW} outdated --cask"
else
  log "Outdated formulae:"
  "${BREW}" outdated --formula | tee -a "${LOG_FILE}" || true
  log "Outdated casks:"
  "${BREW}" outdated --cask | tee -a "${LOG_FILE}" || true
fi

# Upgrades
run "${BREW} upgrade"
if [[ ${GREEDY} -eq 1 ]]; then
  run "${BREW} upgrade --cask --greedy"
else
  run "${BREW} upgrade --cask"
fi

# Cleanup
if [[ ${CLEANUP} -eq 1 ]]; then
  run "${BREW} cleanup -s"
fi

# Doctor (non-fatal)
if [[ ${DRY_RUN} -eq 0 ]]; then
  log "Running brew doctor (informational)..."
  { "${BREW}" doctor 2>&1 | tee -a "${LOG_FILE}"; } || true
fi

log "Done."
if command -v osascript >/dev/null 2>&1 && [[ ${DRY_RUN} -eq 0 ]]; then
  osascript -e 'display notification "Homebrew upgrades complete" with title "brew-upgrade"'
fi
