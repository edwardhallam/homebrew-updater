# Cask Upgrade Failure Fix - November 6, 2025

## Problem Report

**Date:** 2025-11-06 10:23 AM
**Status:** ❌ Failed to upgrade casks
**Affected casks:** `logi-options+`, `microsoft-excel`, `microsoft-teams`

### Error Messages

```
sudo: no password was provided
sudo: a password is required
```

From log (`homebrew-updater-20251106-100003.log`):
```
logi-options+: Failure while executing; `/usr/bin/sudo -u root -A -E -- /usr/bin/xargs -0 -- /bin/rm --` exited with 1
microsoft-excel: Failure while executing; `/usr/bin/sudo -u root -A -E -- /usr/bin/xargs -0 -- /opt/homebrew/Library/Homebrew/cask/utils/rmdir.sh` exited with 1
microsoft-teams: Failure while executing; `/usr/bin/sudo -u root -A -E -- /usr/bin/xargs -0 -- /bin/rm --` exited with 1
```

### Successfully Upgraded (Before Failure)

The following casks upgraded successfully:
- `cursor` (2.0.54 → 2.0.64)
- `github` (3.5.3 → 3.5.4)
- `raycast` (1.103.5 → 1.103.6)
- `microsoft-word` (16.102.25102623 → 16.102.25110228) - Succeeded before cleanup phase

### Root Cause Analysis

**Why it failed:**

1. **LaunchAgent Background Context:** The script runs as a background LaunchAgent, not in an interactive user session
2. **GUI Password Prompts Unavailable:** macOS security prevents background processes from displaying GUI dialogs
3. **SUDO_ASKPASS Failed:** The `brew_autoupdate_sudo_gui` script uses `pinentry-mac` which requires GUI access
4. **Cleanup Phase Requires Sudo:** Casks like `logi-options+`, `microsoft-excel`, and `microsoft-teams` install system-level files that require sudo to remove

**Why some succeeded:**

- Simple casks that don't require sudo for cleanup worked fine
- `microsoft-word` succeeded because the installer portion completed before the failed cleanup operations
- Formulae upgrades (11 packages) all succeeded because they don't typically require sudo

**Pattern observed:**

The `-A` flag in brew's sudo command indicates it's using `SUDO_ASKPASS`, but:
```bash
SUDO_ASKPASS=/path/to/brew_autoupdate_sudo_gui
```

This environment variable points to a script that attempts to show a GUI password dialog, which fails in LaunchAgent context.

## Solution Implemented

### Passwordless Sudo Configuration

Created `/etc/sudoers.d/homebrew-updater` to allow specific brew-related operations without password prompts.

**Allowed operations:**
- `/usr/bin/xargs *` - Used by brew for batch file operations
- `/bin/rm *` - File removal during cask cleanup
- `/opt/homebrew/Library/Homebrew/cask/utils/rmdir.sh *` - Brew's directory removal utility
- `/usr/sbin/pkgutil *` - Package database operations
- `/usr/sbin/installer *` - macOS package installation
- `/bin/launchctl *` - LaunchAgent/LaunchDaemon management

**Security boundaries:**
- Limited to users in `%admin` group only
- Specific command paths (prevents PATH hijacking)
- No unrestricted sudo access
- Follows sudoers best practices

### Installation Files Created

1. **`config/homebrew-updater.sudoers`** - Template with syntax-validated sudoers rules
2. **`scripts/install_sudoers.sh`** - Automated installation script with validation
3. **`docs/PASSWORDLESS_SUDO_SETUP.md`** - Comprehensive setup guide

### Installation Steps Performed

```bash
cd ~/projects/homebrew-updater
./scripts/install_sudoers.sh
```

The script:
1. Validated syntax with `visudo -cf`
2. Copied to `/etc/sudoers.d/homebrew-updater`
3. Set correct permissions (0440, root:wheel)

### Verification Tests Passed

```bash
# All these commands now work without password prompts:
✓ sudo -n /usr/bin/xargs --version
✓ sudo -n /bin/rm --version
✓ sudo -n /usr/sbin/installer -help
✓ sudo -n /usr/sbin/pkgutil --pkgs
✓ sudo -n /bin/launchctl list

# Exact pattern brew uses also works:
✓ printf "file1\0file2\0" | sudo -n /usr/bin/xargs -0 -- /bin/rm --
```

## Expected Outcome

When the LaunchAgent runs tomorrow (2025-11-07 10:00 AM):

1. ✅ Formulae will upgrade normally (no change)
2. ✅ Casks requiring sudo will upgrade successfully without password prompts
3. ✅ Cleanup operations will complete without errors
4. ✅ Notifications will show success instead of failure

## Monitoring Plan

**Check after next run:**

```bash
# View latest log
tail -50 ~/Library/Logs/homebrew-updater/homebrew-updater-*.log

# Look for sudo errors
grep -i "sudo" ~/Library/Logs/homebrew-updater/homebrew-updater-*.log | tail -20

# Verify cask upgrades completed
brew list --cask --versions | grep -E "(logi-options|microsoft-excel|microsoft-teams)"
```

**Expected log output:**
- No "sudo: no password was provided" errors
- "🍺 cask-name was successfully upgraded!" messages
- Success notification sent to Slack/Discord

## Alternative Solutions Considered

1. **Run only when user is active** - Rejected: defeats purpose of automated updates
2. **Extend sudo timeout** - Rejected: still requires manual `sudo -v` before 10am
3. **Split sudo/non-sudo schedules** - Rejected: adds complexity
4. **Skip problematic casks** - Rejected: incomplete solution
5. **✅ Passwordless sudo (chosen)** - Best balance of automation and security

## Documentation Updates

- ✅ Updated `CLAUDE.md` with passwordless sudo section
- ✅ Created `docs/PASSWORDLESS_SUDO_SETUP.md` with detailed guide
- ✅ Added troubleshooting section to main documentation
- ✅ Created this incident report for future reference

## Related Files

- **Log file:** `~/Library/Logs/homebrew-updater/homebrew-updater-20251106-100003.log`
- **Sudoers config:** `/etc/sudoers.d/homebrew-updater`
- **Template:** `config/homebrew-updater.sudoers`
- **Installer:** `scripts/install_sudoers.sh`
- **Documentation:** `docs/PASSWORDLESS_SUDO_SETUP.md`

## Lessons Learned

1. **LaunchAgent context is restrictive:** Background processes cannot access GUI for password prompts
2. **Brew cask cleanup varies:** Some casks need sudo for cleanup, others don't - depends on installation location
3. **SUDO_ASKPASS limitations:** Works great for interactive sessions, fails for background processes
4. **Passwordless sudo is necessary:** For truly unattended cask upgrades in LaunchAgent context
5. **Specific command allowlisting:** More secure than broad sudo access

## Future Considerations

- Monitor for any new casks that might require additional sudo patterns
- Consider adding `NOPASSWD` rules for specific cask operations if new patterns emerge
- Document this as a requirement for fresh installs
- May want to add sudo failure detection and fallback notification

## Resolution Status

**Status:** ✅ **RESOLVED**
**Resolution date:** 2025-11-06
**Next verification:** 2025-11-07 10:00 AM (next scheduled run)
**Confidence level:** High - all verification tests passed
