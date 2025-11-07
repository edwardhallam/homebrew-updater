# Troubleshooting Guide

This guide helps you resolve issues with the Homebrew Updater, particularly post-upgrade cleanup warnings.

## Understanding Cleanup Warnings

### What They Mean

When you see "⚠️ Post-Upgrade Cleanup Warnings" in notifications, it means:

✅ **The cask upgraded successfully** - Your application was updated correctly
⚠️ **Post-upgrade cleanup had issues** - Empty directories or old files weren't removed automatically
💡 **Usually harmless** - These are cosmetic issues, not functional problems

### Why They Occur

Some casks (like `logi-options+`, custom installers, etc.) use installation scripts that require specific sudo permissions. While the passwordless sudo configuration allows the main installation, some cleanup operations may fail if they:

1. Use dynamic paths (version-specific installer scripts)
2. Try to remove system directories that aren't in the sudoers whitelist
3. Attempt rollbacks when cleanup fails

## Manual Cleanup Procedures

### Quick Cleanup (Recommended)

Run this command to clean up specific casks that had warnings:

```bash
brew cleanup logi-options+ microsoft-teams  # Replace with your cask names
```

Or clean up everything at once:

```bash
brew cleanup --prune=all
```

**Note:** This may prompt for your password interactively.

### Targeted Directory Cleanup

If brew cleanup doesn't resolve the issue, you can manually remove empty directories:

```bash
# Check if directory is empty
ls -la "/Library/Application Support/Logitech.localized"

# Remove empty directory (requires password)
sudo rmdir "/Library/Application Support/Logitech.localized"
```

Common directories that may need manual cleanup:

| Cask | Common Leftover Directories |
|------|----------------------------|
| `logi-options+` | `/Library/Application Support/Logitech.localized` |
| `microsoft-*` | `/Library/Application Support/Microsoft/` subdirectories |
| `google-*` | `/Library/Application Support/Google/` subdirectories |

### Deep Cleanup (When All Else Fails)

If a cask is completely broken after a failed cleanup:

```bash
# Forcefully uninstall (requires password)
brew uninstall --cask --force --zap CASK_NAME

# Clean up any remaining files
brew cleanup --prune=all

# Reinstall fresh
brew install --cask CASK_NAME
```

## Common Issues

### Issue: "sudo: sorry, you are not allowed to preserve the environment"

**Cause:** The sudoers configuration is missing `SETENV:` for specific commands.

**Solution:**

1. Check sudoers configuration:
```bash
sudo cat /etc/sudoers.d/homebrew-updater
```

2. Verify these lines include `SETENV:`:
```
%admin ALL=(root) SETENV: NOPASSWD: /usr/bin/rmdir *
%admin ALL=(root) SETENV: NOPASSWD: /bin/rm *
```

3. If missing, reinstall sudoers:
```bash
cd ~/projects/homebrew-updater
./scripts/install_sudoers.sh
```

### Issue: "sudo: a password is required"

**Cause:** The command path doesn't match what's in your sudoers file.

**Common path mismatches:**

| Incorrect Path | Correct Path |
|---------------|-------------|
| `/bin/rmdir` | `/usr/bin/rmdir` |
| `/bin/rm` | Usually correct, but verify with `which rm` |

**Solution:**

1. Find the correct path:
```bash
which rmdir  # Should show /usr/bin/rmdir
```

2. Update sudoers configuration in `config/homebrew-updater.sudoers`

3. Reinstall:
```bash
./scripts/install_sudoers.sh
```

### Issue: Casks repeatedly fail with custom installer errors

**Cause:** Some casks have proprietary installers with dynamic paths that can't be pre-authorized.

**Options:**

1. **Accept the warnings** - The cask upgraded successfully; cleanup is cosmetic
2. **Manual cleanup** - Run `brew cleanup CASK_NAME` after each update
3. **Broader sudo permissions** - (Not recommended) Allow all Caskroom executables

**To allow Caskroom executables (reduces security):**

Add to `/etc/sudoers.d/homebrew-updater`:
```
%admin ALL=(root) SETENV: NOPASSWD: /opt/homebrew/Caskroom/*/*/*.app/Contents/MacOS/* *
```

⚠️ **Security Warning:** This allows ANY executable in Caskroom to run as root.

### Issue: LaunchAgent runs but nothing happens

**Diagnostics:**

1. Check if LaunchAgent is loaded:
```bash
launchctl list | grep homebrew-updater
```

2. View recent logs:
```bash
tail -50 ~/Library/Logs/homebrew-updater/homebrew-updater-*.log
```

3. Test manually:
```bash
python3 ~/projects/homebrew-updater/scripts/homebrew_updater.py
```

4. Check LaunchAgent output:
```bash
cat ~/Library/Logs/homebrew-updater.stdout.log
cat ~/Library/Logs/homebrew-updater.stderr.log
```

## Prevention Tips

### Minimize Cleanup Warnings

1. **Keep sudoers updated** - Ensure all paths match your system
2. **Run manual cleanup monthly** - `brew cleanup --prune=all`
3. **Monitor notifications** - Address warnings before they accumulate

### Monthly Maintenance

Set a calendar reminder to run:

```bash
# Clean up old cask versions and downloads
brew cleanup --prune=all

# Check for brew issues
brew doctor

# View outdated packages
brew outdated
```

## Getting Help

### Log Files

When reporting issues, include:

```bash
# Most recent log
ls -lt ~/Library/Logs/homebrew-updater/ | head -5

# View specific log
cat ~/Library/Logs/homebrew-updater/homebrew-updater-YYYYMMDD-HHMMSS.log
```

### Debug Mode

Run manually with verbose output:

```bash
python3 ~/projects/homebrew-updater/scripts/homebrew_updater.py 2>&1 | tee debug.log
```

### Check Sudoers Permissions

Test if passwordless sudo is working:

```bash
# Should work without password prompt
sudo -n /usr/bin/rmdir --version

# Should work without password prompt
sudo -n brew upgrade --cask --dry-run
```

## Environment Variables

Useful for debugging:

| Variable | Purpose | Example |
|----------|---------|---------|
| `HOMEBREW_DEBUG` | Show debug output | `export HOMEBREW_DEBUG=1` |
| `HOMEBREW_VERBOSE` | Verbose mode | `export HOMEBREW_VERBOSE=1` |
| `HOMEBREW_NO_INSTALL_CLEANUP` | Disable auto-cleanup | `export HOMEBREW_NO_INSTALL_CLEANUP=1` |

## Related Documentation

- [Passwordless Sudo Setup](PASSWORDLESS_SUDO_SETUP.md) - Initial sudo configuration
- [README.md](../README.md) - General usage and setup
- [Homebrew Cask Documentation](https://docs.brew.sh/Cask-Cookbook) - Official cask docs
