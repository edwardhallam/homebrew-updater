# Passwordless Sudo Setup for Homebrew Updater

## Overview

This document explains how to configure passwordless sudo for specific Homebrew operations, allowing the LaunchAgent to perform unattended cask upgrades without GUI password prompts.

## Problem Statement

When running as a LaunchAgent background process, the Homebrew updater cannot display GUI password prompts because:
- macOS security prevents background processes from accessing the user's GUI session
- `SUDO_ASKPASS` with `pinentry-mac` fails in this context
- Cask operations that require sudo (like `logi-options+`, `microsoft-excel`, etc.) will fail

## Solution

Configure `/etc/sudoers.d/` to allow specific brew operations to run without a password for admin users.

## Security Considerations

**What this allows:**
- Brew cask upgrade/reinstall operations
- File removal operations used by brew cask cleanup
- Package installation/uninstallation via brew
- LaunchAgent management for cask services

**Security boundaries:**
- Only applies to users in the `admin` group
- Limited to specific brew-related commands (no unrestricted sudo)
- Commands use full paths to prevent PATH hijacking
- Follows sudoers best practices

**Risk assessment:**
- **Low risk**: Commands are limited to package management operations
- **Acceptable for**: Personal machines, development environments
- **Consider alternatives for**: Shared machines, high-security environments

## Installation

### Automated Installation (Recommended)

Run the installation script which will validate syntax and install the configuration:

```bash
cd ~/projects/homebrew-updater
./scripts/install_sudoers.sh
```

The script will:
1. Ask for confirmation
2. Validate sudoers syntax (prevents lockouts)
3. Request your password
4. Install the configuration with correct permissions

### Manual Installation

If you prefer to install manually:

```bash
cd ~/projects/homebrew-updater

# Validate syntax first (important!)
sudo visudo -cf config/homebrew-updater.sudoers

# If validation passes, install
sudo cp config/homebrew-updater.sudoers /etc/sudoers.d/homebrew-updater
sudo chmod 0440 /etc/sudoers.d/homebrew-updater
sudo chown root:wheel /etc/sudoers.d/homebrew-updater
```

## Verification

### Test the configuration:

```bash
# This should NOT prompt for password (will show "a password is required" if not working)
sudo -n brew upgrade --cask --dry-run

# Verify the file is installed
sudo cat /etc/sudoers.d/homebrew-updater

# Check file permissions
ls -la /etc/sudoers.d/homebrew-updater
# Should show: -r--r----- 1 root wheel ... homebrew-updater
```

### Test with the updater:

```bash
# Run the updater manually to test
python3 scripts/homebrew_updater.py

# Check the log for sudo errors
tail -50 ~/Library/Logs/homebrew-updater/homebrew-updater-*.log | grep -i sudo
```

## Troubleshooting

### If you see "sudo: a password is required"

1. **Check file exists:**
   ```bash
   ls -la /etc/sudoers.d/homebrew-updater
   ```

2. **Verify syntax is valid:**
   ```bash
   sudo visudo -cf /etc/sudoers.d/homebrew-updater
   ```

3. **Check you're in admin group:**
   ```bash
   groups | grep admin
   ```

4. **Test with absolute paths:**
   ```bash
   sudo -n /opt/homebrew/bin/brew upgrade --cask --dry-run
   ```

### If brew operations still fail

1. Check LaunchAgent environment variables are set correctly
2. Verify `SUDO_ASKPASS` is NOT interfering (sudoers takes precedence)
3. Check logs for specific commands that failed
4. May need to add additional commands to sudoers file

## Uninstallation

To remove passwordless sudo configuration:

```bash
sudo rm /etc/sudoers.d/homebrew-updater
```

After removal, cask upgrades requiring sudo will fail again when running via LaunchAgent.

## Alternative Solutions

If you prefer not to use passwordless sudo:

1. **Run manually**: Run `python3 scripts/homebrew_updater.py` manually when you're at the computer
2. **Separate schedule**: Run cask upgrades separately on a weekly schedule when you can provide password
3. **Touchid for sudo**: Configure PAM to use TouchID, though this still won't work for LaunchAgent context
4. **Skip problematic casks**: Modify the script to skip casks that require sudo

## Files

- **Sudoers template**: `config/homebrew-updater.sudoers`
- **Installation script**: `scripts/install_sudoers.sh`
- **Installed location**: `/etc/sudoers.d/homebrew-updater`

## References

- [sudoers manual](https://www.sudo.ws/man/sudoers.man.html)
- [Homebrew Cask documentation](https://docs.brew.sh/Cask-Cookbook)
- [macOS LaunchAgent security](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
