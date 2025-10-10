# Manual Test Checklist for Homebrew Updater

## Pre-Test Setup

- [ ] Discord webhook URL configured in `scripts/homebrew_updater.py`
- [ ] Python 3 installed and accessible
- [ ] Homebrew installed and functioning
- [ ] `brew_autoupdate_sudo_gui` script exists and is executable
- [ ] Old LaunchAgent (`com.github.domt4.homebrew-autoupdate`) is unloaded

## Test 1: Unit Tests

**Objective:** Verify all functions work correctly in isolation

```bash
python3 tests/test_homebrew_updater.py
```

**Expected Results:**
- [ ] All unit tests pass (0 failures)
- [ ] Idle detection tests pass
- [ ] Discord notification tests pass
- [ ] Brew command tests pass
- [ ] Main flow tests pass

**Actual Results:**
```
[Record test output here]
```

---

## Test 2: Discord Webhook Test

**Objective:** Verify Discord notifications are sent correctly

```bash
python3 tests/test_discord_webhook.py
```

**Expected Results:**
- [ ] Connectivity test passes
- [ ] Start notification appears in Discord
- [ ] Success notification appears in Discord
- [ ] Error notification appears in Discord (red color)
- [ ] Formatted message appears in Discord

**Actual Results:**
```
[Record test output and Discord messages here]
```

**Discord Channel Screenshots:**
- [ ] Attach screenshots of Discord messages

---

## Test 3: Idle Detection Test

**Objective:** Verify idle detection works correctly

### Test 3A: Active State (< 5 minutes idle)

**Steps:**
1. Move mouse/type on keyboard
2. Immediately run: `python3 -c "import sys; sys.path.insert(0, 'scripts'); import homebrew_updater; print(f'Idle: {homebrew_updater.get_idle_time_seconds()}s')"`

**Expected Results:**
- [ ] Idle time is < 300 seconds
- [ ] `is_user_idle()` returns False

**Actual Results:**
```
Idle time: ___ seconds
is_user_idle: ___
```

### Test 3B: Idle State (> 5 minutes idle)

**Steps:**
1. Don't touch keyboard/mouse for 6+ minutes
2. Run: `python3 -c "import sys; sys.path.insert(0, 'scripts'); import homebrew_updater; print(f'Idle: {homebrew_updater.get_idle_time_seconds()}s')"`

**Expected Results:**
- [ ] Idle time is > 300 seconds
- [ ] `is_user_idle()` returns True

**Actual Results:**
```
Idle time: ___ seconds
is_user_idle: ___
```

---

## Test 4: Full Update - Active User

**Objective:** Test full update when user is active (not idle)

**Steps:**
1. Ensure you're not idle (move mouse)
2. Run: `python3 scripts/homebrew_updater.py`
3. Observe behavior

**Expected Results:**
- [ ] Script detects user as active
- [ ] Discord "Starting" notification sent
- [ ] `brew update` runs successfully
- [ ] Ghost cask healing runs
- [ ] Formulae upgrade runs
- [ ] Casks upgrade runs (may prompt for sudo password via GUI)
- [ ] `brew cleanup -s` runs
- [ ] `brew doctor` runs
- [ ] Discord success notification sent with counts
- [ ] Log file created in `~/Library/Logs/homebrew-updater/`
- [ ] Exit code is 0

**Actual Results:**
```
User state: ___
Formulae upgraded: ___
Casks upgraded: ___
Ghost casks removed: ___
Exit code: ___
Log file: ___
```

**Discord Notifications Received:**
- [ ] Start notification
- [ ] Success notification with upgrade counts

---

## Test 5: Full Update - Idle User

**Objective:** Test update behavior when user is idle (skips sudo)

**Steps:**
1. Wait until idle (> 5 minutes without activity)
2. Remotely trigger: `python3 scripts/homebrew_updater.py`
3. Observe behavior

**Expected Results:**
- [ ] Script detects user as idle
- [ ] Discord "idle" notification sent
- [ ] `brew update` runs successfully
- [ ] Ghost cask healing SKIPPED (skip_sudo=True)
- [ ] Formulae upgrade runs
- [ ] Casks upgrade SKIPPED
- [ ] `brew cleanup` runs
- [ ] Discord success notification mentions "casks skipped"
- [ ] Log file created
- [ ] Exit code is 0

**Actual Results:**
```
User state: ___
Formulae upgraded: ___
Casks upgraded: ___ (should be 0)
Ghost casks healing: ___ (should be skipped)
Exit code: ___
```

**Discord Notifications Received:**
- [ ] Idle notification
- [ ] Success notification with "skipped" message

---

## Test 6: Error Handling

**Objective:** Verify error handling and notifications

### Test 6A: Brew Update Failure

**Steps:**
1. Temporarily make brew inaccessible: `sudo chmod -x /opt/homebrew/bin/brew`
2. Run: `python3 scripts/homebrew_updater.py`
3. Restore: `sudo chmod +x /opt/homebrew/bin/brew`

**Expected Results:**
- [ ] Script fails gracefully
- [ ] Error logged
- [ ] Discord error notification (red) sent
- [ ] Exit code is 1

**Actual Results:**
```
Exit code: ___
Error message: ___
```

---

## Test 7: Log Management

**Objective:** Verify log creation and rotation

**Steps:**
1. Check existing logs: `ls -la ~/Library/Logs/homebrew-updater/`
2. Run updater 3 times
3. Check log count again

**Expected Results:**
- [ ] Log directory exists
- [ ] New log file created for each run
- [ ] Log files have timestamp format: `homebrew-updater-YYYYMMDD-HHMMSS.log`
- [ ] If > 10 log files, oldest are removed
- [ ] Each log contains detailed output

**Actual Results:**
```
Log directory: ___
Log files before: ___
Log files after: ___
Sample log file: ___
```

---

## Test 8: Cleanup Verification

**Objective:** Verify cleanup actually removes old files

**Steps:**
1. Check Homebrew cache size before: `du -sh ~/Library/Caches/Homebrew`
2. Run updater
3. Check cache size after

**Expected Results:**
- [ ] Cache size reduced or remains small
- [ ] Old downloads removed
- [ ] `brew cleanup -s` output in log

**Actual Results:**
```
Cache size before: ___
Cache size after: ___
Files removed: ___
```

---

## Test 9: LaunchAgent Installation

**Objective:** Install and verify LaunchAgent

**Steps:**
1. Copy plist: `cp launchd/com.homebrew-updater.plist ~/Library/LaunchAgents/`
2. Load agent: `launchctl load ~/Library/LaunchAgents/com.homebrew-updater.plist`
3. Verify: `launchctl list | grep homebrew-updater`
4. Check schedule: `launchctl print gui/$(id -u)/com.homebrew-updater | grep hour`

**Expected Results:**
- [ ] Plist copied successfully
- [ ] Agent loads without errors
- [ ] Agent appears in launchctl list
- [ ] Schedule shows hour=10, minute=0

**Actual Results:**
```
launchctl list output: ___
Schedule details: ___
```

---

## Test 10: Scheduled Execution

**Objective:** Verify LaunchAgent triggers at scheduled time

### Option A: Wait for 10am

**Steps:**
1. Wait for next 10:00 AM
2. Check if script runs automatically
3. Verify log created around 10:00 AM
4. Check Discord for notification around 10:00 AM

**Expected Results:**
- [ ] Script runs automatically at 10:00 AM
- [ ] Log file timestamped around 10:00 AM
- [ ] Discord notification received around 10:00 AM

### Option B: Manual Trigger (Recommended for testing)

**Steps:**
1. Manually trigger: `launchctl start com.homebrew-updater`
2. Monitor logs: `tail -f ~/Library/Logs/homebrew-updater/launchd.out`
3. Check Discord

**Expected Results:**
- [ ] Script runs immediately
- [ ] Output appears in launchd.out
- [ ] Discord notification received
- [ ] Main log file created

**Actual Results:**
```
Trigger time: ___
Log file created: ___
Discord notification: ___
```

---

## Test 11: Ghost Cask Healing

**Objective:** Verify ghost cask detection and removal

### Setup (Optional - Only if you have ghost casks)
**Note:** Only test if you actually have ghost casks. Don't create fake ones.

**Steps:**
1. Check for ghost casks: `brew list --cask`
2. Run updater with healing enabled
3. Check if ghosts are removed

**Expected Results:**
- [ ] Ghost casks detected (if any exist)
- [ ] Ghost casks removed automatically
- [ ] Logged in output

**Actual Results:**
```
Ghost casks found: ___
Ghost casks removed: ___
```

---

## Test 12: Sudo GUI Prompt

**Objective:** Verify GUI password prompt works

**Steps:**
1. Ensure user is active (not idle)
2. Ensure you have casks that need updating
3. Run updater
4. Observe password prompt

**Expected Results:**
- [ ] GUI password prompt appears (pinentry-mac)
- [ ] Prompt mentions "homebrew-autoupdate"
- [ ] After entering password, cask updates proceed
- [ ] No terminal password prompts

**Actual Results:**
```
GUI prompt appeared: ___
Prompt type: ___
Casks updated: ___
```

---

## Post-Test Cleanup

- [ ] Verify LaunchAgent is loaded: `launchctl list | grep homebrew-updater`
- [ ] Verify old LaunchAgent is NOT loaded: `launchctl list | grep domt4`
- [ ] Check final log count: `ls ~/Library/Logs/homebrew-updater/ | wc -l`
- [ ] Verify Discord webhook is working
- [ ] Document any issues found

---

## Test Summary

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Unit Tests | ☐ Pass ☐ Fail | |
| 2 | Discord Webhook | ☐ Pass ☐ Fail | |
| 3A | Idle Detection - Active | ☐ Pass ☐ Fail | |
| 3B | Idle Detection - Idle | ☐ Pass ☐ Fail | |
| 4 | Full Update - Active | ☐ Pass ☐ Fail | |
| 5 | Full Update - Idle | ☐ Pass ☐ Fail | |
| 6 | Error Handling | ☐ Pass ☐ Fail | |
| 7 | Log Management | ☐ Pass ☐ Fail | |
| 8 | Cleanup Verification | ☐ Pass ☐ Fail | |
| 9 | LaunchAgent Install | ☐ Pass ☐ Fail | |
| 10 | Scheduled Execution | ☐ Pass ☐ Fail | |
| 11 | Ghost Cask Healing | ☐ Pass ☐ Fail ☐ N/A | |
| 12 | Sudo GUI Prompt | ☐ Pass ☐ Fail | |

**Overall Result:** ☐ PASS ☐ FAIL

**Issues Found:**
```
[List any issues discovered during testing]
```

**Recommendations:**
```
[List any improvements or changes needed]
```

---

## Sign-off

**Tester:** _______________
**Date:** _______________
**Version:** 1.0
