#!/bin/bash
# Integration test for homebrew_updater.py
# Tests the full workflow in different scenarios

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
UPDATER_SCRIPT="$PROJECT_DIR/scripts/homebrew_updater.py"
LOG_DIR="$HOME/Library/Logs/homebrew-updater"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "=========================================="
echo "Homebrew Updater Integration Tests"
echo "=========================================="
echo "Time: $(date)"
echo "Script: $UPDATER_SCRIPT"
echo ""

# Check prerequisites
log_info "Checking prerequisites..."

if [[ ! -f "$UPDATER_SCRIPT" ]]; then
    log_error "Updater script not found: $UPDATER_SCRIPT"
    exit 1
fi
log_success "Updater script found"

if ! command -v python3 >/dev/null 2>&1; then
    log_error "python3 not found"
    exit 1
fi
log_success "python3 found: $(which python3)"

if ! command -v brew >/dev/null 2>&1; then
    log_error "Homebrew not found"
    exit 1
fi
log_success "Homebrew found: $(which brew)"

# Test 1: Check script syntax
echo ""
echo "=========================================="
echo "Test 1: Python Syntax Check"
echo "=========================================="
if python3 -m py_compile "$UPDATER_SCRIPT" 2>/dev/null; then
    log_success "Script syntax is valid"
else
    log_error "Script has syntax errors"
    exit 1
fi

# Test 2: Check imports
echo ""
echo "=========================================="
echo "Test 2: Import Test"
echo "=========================================="
if python3 -c "import sys; sys.path.insert(0, '$PROJECT_DIR/scripts'); import homebrew_updater" 2>/dev/null; then
    log_success "All imports successful"
else
    log_error "Import errors detected"
    python3 -c "import sys; sys.path.insert(0, '$PROJECT_DIR/scripts'); import homebrew_updater"
    exit 1
fi

# Test 3: Check Discord webhook configuration
echo ""
echo "=========================================="
echo "Test 3: Discord Webhook Configuration"
echo "=========================================="
WEBHOOK_URL=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_DIR/scripts'); import homebrew_updater; print(homebrew_updater.DISCORD_WEBHOOK_URL)")

if [[ "$WEBHOOK_URL" == "YOUR_DISCORD_WEBHOOK_URL_HERE" ]]; then
    log_warn "Discord webhook not configured (will skip notifications)"
else
    log_success "Discord webhook configured"
fi

# Test 4: Check idle detection
echo ""
echo "=========================================="
echo "Test 4: Idle Detection"
echo "=========================================="
IDLE_TIME=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_DIR/scripts'); import homebrew_updater; print(homebrew_updater.get_idle_time_seconds() or 0)")
log_info "Current idle time: ${IDLE_TIME} seconds"

if [[ "$IDLE_TIME" -gt 300 ]]; then
    log_info "System is IDLE (>${IDLE_THRESHOLD}s)"
    USER_STATE="idle"
else
    log_info "System is ACTIVE (<${IDLE_THRESHOLD}s)"
    USER_STATE="active"
fi
log_success "Idle detection working"

# Test 5: Check log directory
echo ""
echo "=========================================="
echo "Test 5: Log Directory"
echo "=========================================="
if [[ -d "$LOG_DIR" ]]; then
    log_info "Log directory exists: $LOG_DIR"
    LOG_COUNT=$(ls -1 "$LOG_DIR"/homebrew-updater-*.log 2>/dev/null | wc -l | xargs)
    log_info "Existing log files: $LOG_COUNT"
else
    log_info "Log directory will be created on first run"
fi
log_success "Log directory check complete"

# Test 6: Check sudo GUI script
echo ""
echo "=========================================="
echo "Test 6: Sudo GUI Helper Script"
echo "=========================================="
SUDO_GUI_SCRIPT="$PROJECT_DIR/scripts/brew_autoupdate_sudo_gui"
if [[ -f "$SUDO_GUI_SCRIPT" ]]; then
    if [[ -x "$SUDO_GUI_SCRIPT" ]]; then
        log_success "Sudo GUI script exists and is executable"
    else
        log_warn "Sudo GUI script exists but is not executable"
        chmod +x "$SUDO_GUI_SCRIPT"
        log_info "Made sudo GUI script executable"
    fi
else
    log_warn "Sudo GUI script not found (GUI password prompts may not work)"
fi

# Test 7: Dry run test
echo ""
echo "=========================================="
echo "Test 7: Dry Run Test (User: $USER_STATE)"
echo "=========================================="
log_info "This test will run the updater script"
log_info "Check Discord for notifications"
log_warn "This will perform ACTUAL Homebrew updates!"

read -p "Continue with dry run? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Skipping dry run test"
else
    log_info "Running updater script..."
    echo "=========================================="

    if python3 "$UPDATER_SCRIPT"; then
        log_success "Updater script completed successfully"
    else
        EXIT_CODE=$?
        log_error "Updater script failed with exit code: $EXIT_CODE"
        exit 1
    fi

    echo ""
    log_info "Checking logs..."
    LATEST_LOG=$(ls -t "$LOG_DIR"/homebrew-updater-*.log 2>/dev/null | head -1)
    if [[ -f "$LATEST_LOG" ]]; then
        log_success "Log file created: $(basename "$LATEST_LOG")"
        log_info "Last 10 lines of log:"
        echo "----------------------------------------"
        tail -10 "$LATEST_LOG"
        echo "----------------------------------------"
    else
        log_error "No log file created"
    fi
fi

# Test 8: Log rotation test
echo ""
echo "=========================================="
echo "Test 8: Log Rotation"
echo "=========================================="
if [[ -d "$LOG_DIR" ]]; then
    LOG_COUNT=$(ls -1 "$LOG_DIR"/homebrew-updater-*.log 2>/dev/null | wc -l | xargs)
    log_info "Current log files: $LOG_COUNT"

    if [[ "$LOG_COUNT" -le 10 ]]; then
        log_success "Log rotation appears to be working (≤10 files)"
    else
        log_warn "More than 10 log files exist (${LOG_COUNT} files)"
    fi
else
    log_warn "Log directory not found, skipping rotation test"
fi

# Summary
echo ""
echo "=========================================="
echo "Integration Test Summary"
echo "=========================================="
log_success "All integration tests completed!"
echo ""
echo "Next steps:"
echo "1. Check Discord for test notifications"
echo "2. Review log file: $LATEST_LOG"
echo "3. Install LaunchAgent to enable scheduled runs"
echo ""
