# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains an automated Homebrew updater for macOS that runs daily via LaunchAgent. The system features a **dual notification architecture** (Slack/Discord webhooks + macOS native notifications), flexible platform support, automatic ghost cask healing, and **passwordless sudo** configuration for unattended cask upgrades.

**Active Script:** `scripts/homebrew_updater.py` (Python 3)
**Scheduled Via:** `launchd/com.homebrew-updater.plist` (daily at 10:00 AM)
**Supported Platforms:** Slack, Discord, or both
**Sudo Configuration:** `/etc/sudoers.d/homebrew-updater` (for unattended operation)

## Testing Commands

### Run All Tests
```bash
# Unit tests (23 tests)
python3 tests/test_homebrew_updater.py

# Integration tests (7 checks)
bash tests/integration_test.sh

# View comprehensive test report
cat docs/TEST_REPORT.md
```

### Run Specific Test Categories
```bash
# Test Slack webhook connectivity (sends real notifications)
python3 tests/test_slack_webhook.py

# Test Discord webhook connectivity (sends real notifications)
python3 tests/test_discord_webhook.py

# Test dual notification system (sends 4 test notifications)
python3 tests/test_push_notifications.py
```

### Manual Execution
```bash
# Run updater manually (performs ACTUAL brew updates)
python3 scripts/homebrew_updater.py

# View latest log
tail -f ~/Library/Logs/homebrew-updater/homebrew-updater-*.log

# Clean up old log files
python3 -c "import sys; sys.path.insert(0, 'scripts'); import homebrew_updater; homebrew_updater.cleanup_old_logs()"
```

### LaunchAgent Management
```bash
# Install LaunchAgent
cp launchd/com.homebrew-updater.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.homebrew-updater.plist

# Verify it's loaded
launchctl list | grep homebrew-updater

# Reload after changes
launchctl unload ~/Library/LaunchAgents/com.homebrew-updater.plist
launchctl load ~/Library/LaunchAgents/com.homebrew-updater.plist
```

### Passwordless Sudo Setup (Required for Unattended Operation)

**Problem:** LaunchAgent background processes cannot display GUI password prompts, causing cask upgrades to fail when sudo is required.

**Solution:** Configure `/etc/sudoers.d/homebrew-updater` to allow specific brew-related operations without password.

```bash
# One-time setup (requires your password)
./scripts/install_sudoers.sh

# Verify installation
sudo -n /usr/bin/xargs --help  # Should work without password prompt
ls -la /etc/sudoers.d/homebrew-updater  # Should show: -r--r----- root wheel

# Test with actual updater
python3 scripts/homebrew_updater.py
```

**What operations are allowed passwordless:**
- File removal operations (`xargs`, `rm`) used by brew cask cleanup
- Package operations (`pkgutil`, `installer`) for cask installation/removal
- LaunchAgent management (`launchctl`) for cask services

**Security:** Limited to admin group, specific commands only. See `docs/PASSWORDLESS_SUDO_SETUP.md` for detailed security analysis.

**Troubleshooting:** If cask upgrades still fail with "sudo: a password is required", re-run `./scripts/install_sudoers.sh` and check logs.

## Architecture

### Dual Notification System

The updater sends **two independent notifications** for every event to ensure reliability:

```
send_notification(message, error=False)
    ├─→ Webhook Platform(s) (based on NOTIFICATION_PLATFORM)
    │   ├─ Slack (_send_slack)
    │   │   ├─ blocks: Rich formatted blocks with sections
    │   │   ├─ attachments: Color-coded sidebar (green/red)
    │   │   └─ Returns HTTP 200 on success
    │   │
    │   └─ Discord (_send_discord)
    │       ├─ content field: "@mention + first line" (triggers badge notifications)
    │       ├─ embeds field: Full formatted message with package lists
    │       └─ Returns HTTP 204 on success
    │
    └─→ macOS Native (via osascript) - ALWAYS sent
        ├─ Notification Center banner
        └─ Sound alert (Glass = success, Basso = error)
```

**Why Dual?** Webhook push notifications can be unreliable, so the system always sends native macOS notifications which work locally.

**Platform Selection:** Configure via `NOTIFICATION_PLATFORM` environment variable:
- `slack` - Slack webhooks only
- `discord` - Discord webhooks only
- `both` - Send to both Slack AND Discord

### Execution Flow

The script runs all operations unattended with passwordless sudo:

```
main()
  ↓
  ├─ brew update
  ├─ heal_ghost_casks() (passwordless sudo)
  ├─ brew upgrade --formula
  ├─ brew upgrade --cask --greedy (passwordless sudo)
  └─ brew cleanup -s
```

**Note:** All operations run unattended using passwordless sudo configuration in `/etc/sudoers.d/homebrew-updater`. No user interaction or password prompts are required.

### Return Type Conventions

**Critical:** Functions that perform upgrades return **lists of package names**, not counts:

```python
# CORRECT
def brew_upgrade_formulae() -> Tuple[bool, List[str]]:
    # Returns: (success, ["python@3.12", "git", "wget"])

def heal_ghost_casks() -> List[str]:
    # Returns: ["broken-app", "missing-cask"]

# INCORRECT (old pattern)
def brew_upgrade_formulae() -> Tuple[bool, int]:
    # This was changed to support detailed notifications
```

This allows Discord notifications to show **every upgraded package by name** rather than just counts.

### Configuration Variables

**Environment-based configuration** - All sensitive data and configuration options are loaded from environment variables:

```python
# Load from .env file or environment
NOTIFICATION_PLATFORM = os.getenv("NOTIFICATION_PLATFORM", "discord").lower()  # Platform selection
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")  # Required for Slack
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")  # Required for Discord
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID", "")  # For @mentions (numeric ID, not username)
BREW_PATH = os.getenv("BREW_PATH", "/opt/homebrew/bin/brew")
MAX_LOG_FILES = int(os.getenv("MAX_LOG_FILES", "10"))  # Auto-rotation

# Fixed paths
LOG_DIR = Path.home() / "Library/Logs/homebrew-updater"
```

**Configuration sources** (in priority order):
1. Environment variables (set in shell or LaunchAgent plist)
2. `.env` file in project root (loaded automatically if present)
3. Default values (hardcoded fallbacks)

**Security:** The `.env` file is gitignored. Use `.env.example` as a template.

## Key Implementation Details

### Discord Webhook Requirements

**Must include both fields** to trigger notifications:
```python
payload = {
    "content": f"<@{DISCORD_USER_ID}> {first_line}",  # Badge + @mention
    "embeds": [{...}]  # Rich formatting
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Homebrew-Updater/1.0 (Python)'  # Required: Cloudflare bot protection
}
```

**User Mention Format:** Must use `<@NUMERIC_ID>`, not `@username`. Get ID via: right-click username → Copy User ID in Discord.

### Slack Webhook Requirements

**Must use blocks** for rich formatting:
```python
payload = {
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": first_line, "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": message_body}
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"_{hostname}_ • {timestamp}"}]
        }
    ],
    "attachments": [{"color": "#36a64f"}]  # Green for success, "#FF0000" for error
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Homebrew-Updater/1.0 (Python)'
}
```

**Block Types Used:**
- `header` - Large title text with emoji support
- `section` - Body content with mrkdwn formatting
- `context` - Footer with hostname and timestamp
- `attachments` - Color-coded sidebar (green/red)

**Response Code:** Slack webhooks return HTTP 200 (not 204 like Discord).

### Ghost Cask Detection Logic

A cask is considered "ghost" if:
1. Listed in `brew list --cask` but directory missing in Caskroom, OR
2. Directory exists but contains no version subdirectories, OR
3. Has `.app` artifacts defined but none exist in `/Applications` or `~/Applications`

**Skips:** Fonts (`font-*`) and QuickLook plugins (`ql*`) which often have no `.app` artifacts.

### Test Mocking Patterns

When writing tests for functions with new return types:

```python
# Mock return values must match actual signatures
mock_heal_ghost_casks.return_value = ["ghost-cask"]  # List[str]
mock_brew_upgrade_formulae.return_value = (True, ["pkg1", "pkg2"])  # Tuple[bool, List[str]]

# Test assertions
success, packages = homebrew_updater.brew_upgrade_formulae()
self.assertEqual(len(packages), 2)  # NOT: self.assertEqual(packages, 2)
self.assertIn("pkg1", packages)
```

### Log Rotation

Automatic log cleanup keeps only the 10 most recent log files:

```python
def cleanup_old_logs():
    log_files = sorted(LOG_DIR.glob("homebrew-updater-*.log"), reverse=True)
    for old_log in log_files[MAX_LOG_FILES:]:  # Delete 11th onward
        old_log.unlink()
```

Called at start of `main()` before any operations.

## Common Modifications

### Adding New Notification Types

1. Send notifications to configured platform(s):
```python
message = "🔔 New event type"
send_notification(message, error=False)
# Automatically sends to webhook platform(s) based on NOTIFICATION_PLATFORM
# macOS notification always sent regardless of platform
```

2. Use emojis for visual categorization (🚀 start, ✅ success, ❌ error, 👻 ghost, 🧹 cleanup)

### Switching Notification Platforms

Change `NOTIFICATION_PLATFORM` in `.env` file or environment:
- `slack` - Slack webhooks only
- `discord` - Discord webhooks only
- `both` - Send to both platforms

**Note:** Backwards compatibility maintained - `send_discord_notification()` still works but now routes through `send_notification()`.

### Modifying Schedule

Edit `launchd/com.homebrew-updater.plist`:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>10</integer>  <!-- Change hour here -->
    <key>Minute</key>
    <integer>0</integer>   <!-- Change minute here -->
</dict>
```

Then reload LaunchAgent.

### Adding New Brew Operations

Follow the pattern:
```python
def brew_new_operation() -> Tuple[bool, List[str]]:
    """Description"""
    log("Running new operation...")
    success, output = run_brew_command(["new", "command"])

    # Extract package names
    packages = [line.split()[0] for line in output.splitlines() if line.strip()]

    return success, packages if success else []
```

## Documentation Files

- `README.md` - User-facing setup and usage instructions for public GitHub
- `.env.example` - Environment variable template
- `docs/PASSWORDLESS_SUDO_SETUP.md` - **Passwordless sudo configuration guide** (required for unattended operation)
- `docs/SLACK_INTEGRATION.md` - Slack webhook integration guide
- `docs/TEST_REPORT.md` - Comprehensive test results and coverage
- `docs/PUSH_NOTIFICATIONS_SOLUTION.md` - Dual notification system details
- `docs/DETAILED_NOTIFICATIONS_UPDATE.md` - Package list format documentation
- `docs/WEBHOOK_FIX_REPORT.md` - Cloudflare bot protection fix
- `docs/BADGE_NOTIFICATION_FIX.md` - Content field requirement explanation
- `docs/DISCORD_PUSH_NOTIFICATION_CHECKLIST.md` - Troubleshooting guide

## Configuration Files

- `config/homebrew-updater.sudoers` - Sudoers template for passwordless sudo
- `scripts/install_sudoers.sh` - Automated sudoers installation script
- `launchd/com.homebrew-updater.plist` - LaunchAgent configuration template

## Legacy Scripts

Located in `scripts/` directory but **not actively used**:
- `brew_autoupdate` - Original autoupdate script (replaced)
- `brew_autoupdate_sudo_gui` - SUDO_ASKPASS GUI script (replaced by passwordless sudo)
- `brew-upgrade-all.sh` - Reference implementation (not scheduled)

These are kept for reference but `homebrew_updater.py` is the active solution.
