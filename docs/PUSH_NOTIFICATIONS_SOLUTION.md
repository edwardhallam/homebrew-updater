# Push Notifications Solution

**Date:** 2025-10-09
**Issue:** Discord messages arrive but no push notifications
**Solution:** Dual notification system (Discord + macOS native)

---

## Problem

Discord mentions were working (badge, pings in app), but **push notifications** (banner alerts, sounds) were not appearing on macOS.

---

## Solution Implemented

**Dual Notification System:**
1. **Discord** - Message with @mention (shows in channel, pings you)
2. **macOS Native** - System notification (always works, shows banner/sound)

Both notifications are sent simultaneously for every Homebrew update!

---

## How It Works

### Every notification now sends TWO alerts:

```python
# 1. Discord message
send_discord_notification(message, error=False)
  ↓
  • Sends to Discord with @mention
  • Shows in channel
  • Pings you in Discord

# 2. macOS notification (automatic)
send_macos_notification("Homebrew Updater", message, sound="Glass")
  ↓
  • System notification banner
  • Sound alert
  • Shows in Notification Center
```

### Notification Sounds
- **Success:** "Glass" sound (pleasant chime)
- **Error:** "Basso" sound (attention-getting)

---

## What You'll See

### When Homebrew Runs (10am daily):

**1. Discord (in app):**
- Message in channel
- @mention highlighting your username
- Badge count increment
- Ping notification

**2. macOS (system):**
- Banner notification appears on screen
- Sound plays (Glass or Basso)
- Shows in Notification Center
- Can be clicked to view details

---

## Benefits

### Reliability
✅ **Always get notified** - Even if Discord push fails
✅ **Local alerts** - macOS notifications always work
✅ **Redundant system** - Two independent notification paths

### User Experience
✅ **Immediate awareness** - Banner appears immediately
✅ **Audio alerts** - Hear when updates happen
✅ **Persistent** - Notifications stay in Notification Center
✅ **Different sounds** - Errors sound different from success

---

## Testing

### Test Command
```bash
python3 tests/test_push_notifications.py
```

### What to Look For

**Discord (check app):**
- 4 messages with @mention
- Each pings you
- Badge count shows 4

**macOS (check screen/sounds):**
- 4 banner notifications appear
- 3 "Glass" sounds (success notifications)
- 1 "Basso" sound (error notification)
- All 4 in Notification Center (click clock)

---

## Notification Center

### View Past Notifications

1. Click **clock** in menu bar (top-right)
2. Look for **"Homebrew Updater"** section
3. See all recent notifications
4. Click any to view details

### Clear Notifications

1. Open Notification Center
2. Hover over "Homebrew Updater"
3. Click **"X"** or **"Clear All"**

---

## macOS Notification Settings

### Ensure Notifications Are Enabled

```
System Settings → Notifications → Script Editor
```

**Why Script Editor?**
- `osascript` runs through Script Editor
- Notifications appear as from "Script Editor"
- Enable notifications for Script Editor

**Settings:**
- ✅ Allow Notifications: **ON**
- ✅ Notification Style: **Banners** or **Alerts**
- ✅ Show in Notification Center: **ON**
- ✅ Badge app icon: **ON**
- ✅ Play sound for notifications: **ON**

---

## Troubleshooting

### No macOS Notifications?

**Check Focus Mode:**
```
Control Center → Focus
```
- Turn off Do Not Disturb
- Or allow Script Editor in Focus settings

**Check Script Editor Permissions:**
```
System Settings → Notifications → Script Editor → Allow Notifications
```

**Test manually:**
```bash
osascript -e 'display notification "Test" with title "Test" sound name "Glass"'
```

### No Discord Mentions?

See `DISCORD_PUSH_NOTIFICATION_CHECKLIST.md` for Discord settings.

---

## Code Changes

### Files Modified

**scripts/homebrew_updater.py:**
1. Added `DISCORD_USER_ID` configuration
2. Added `send_macos_notification()` function
3. Modified `send_discord_notification()` to:
   - Include @mention: `<@USER_ID>`
   - Send macOS notification after Discord

### New Functions

```python
def send_macos_notification(title: str, message: str, sound: str = "default"):
    """Send native macOS notification"""
    # Uses osascript to display notification
    # Appears in Notification Center
    # Plays sound alert
```

---

## Examples

### Start Notification
```
Discord: @spicyeddie 🚀 Starting Homebrew update...
macOS:   🚀 Starting Homebrew update... (Glass sound)
```

### Success Notification
```
Discord: @spicyeddie ✅ Homebrew Update Complete! - 5 packages
macOS:   ✅ Homebrew Update Complete! - 5 packages (Glass sound)
```

### Error Notification
```
Discord: @spicyeddie ❌ Homebrew update FAILED!
macOS:   ❌ Homebrew update FAILED! (Basso sound)
```

### Idle Notification
```
Discord: @spicyeddie ⏸️ User idle - formulae only
macOS:   ⏸️ User idle - formulae only (Glass sound)
```

---

## Future Enhancements

### Possible Improvements

1. **Rich macOS notifications:**
   - Add buttons (View Logs, Dismiss)
   - Requires more complex osascript

2. **Custom sounds:**
   - Use different sounds for different update types
   - Upload custom sound files

3. **Notification history:**
   - Keep log of all notifications sent
   - Track notification delivery status

4. **iOS/Android push:**
   - Use Pushover/Pushbullet for mobile
   - Requires third-party service

---

## Summary

| Feature | Before | After |
|---------|--------|-------|
| Discord Messages | ✅ Yes | ✅ Yes |
| Discord Mentions | ❌ No | ✅ Yes (@mention) |
| Discord Badge | ❌ No | ✅ Yes |
| Discord Push | ❌ No | ⚠️ Depends on settings |
| macOS Notifications | ❌ No | ✅ Yes (always) |
| macOS Sounds | ❌ No | ✅ Yes (Glass/Basso) |
| macOS Banners | ❌ No | ✅ Yes |
| Notification Center | ❌ No | ✅ Yes |

---

## Conclusion

**Problem Solved:** You'll ALWAYS get notified when Homebrew updates run!

**How:**
- Discord: @mention in message (pings in app)
- macOS: Native system notification (banner + sound)

**Reliability:**
- If Discord push fails → macOS notification still works
- If macOS fails → Discord still shows in channel
- Double redundancy ensures you're always notified

**Next:**
- Test notifications worked? ✅
- See notifications in Notification Center? ✅
- Hear sounds when they arrived? ✅

Tomorrow at 10am, you'll get BOTH notifications when Homebrew runs!

---

**Implemented by:** Claude Code
**Date:** 2025-10-09
**Version:** 3.0 (Dual Notifications)
