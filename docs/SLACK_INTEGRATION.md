# Slack Integration Guide

This document provides comprehensive guidance on integrating Slack webhooks with the Homebrew Auto-Updater.

## Overview

The Homebrew Auto-Updater supports Slack webhooks using the **Slack Blocks API** for rich, formatted notifications. Slack notifications work alongside or instead of Discord, with automatic fallback to native macOS notifications.

## Quick Start

### 1. Create a Slack Webhook

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Homebrew Updater") and select your workspace
4. In the left sidebar, click "Incoming Webhooks"
5. Toggle "Activate Incoming Webhooks" to ON
6. Click "Add New Webhook to Workspace"
7. Select the channel where you want notifications
8. Click "Allow"
9. Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

### 2. Configure Environment

Edit your `.env` file:

```bash
# Set platform to Slack
NOTIFICATION_PLATFORM=slack

# Add your Slack webhook URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Other settings
BREW_PATH=/opt/homebrew/bin/brew
IDLE_THRESHOLD_SECONDS=300
MAX_LOG_FILES=10
```

### 3. Test the Integration

```bash
# Test Slack webhook connectivity
python3 tests/test_slack_webhook.py

# Test full notification system (Slack + macOS)
python3 tests/test_push_notifications.py

# Run a manual update to see live notifications
python3 scripts/homebrew_updater.py
```

## Architecture

### Message Flow

```
send_notification(message, error=False)
    │
    ├─→ _send_slack(message, error)
    │   │
    │   ├─ Parse message into sections
    │   ├─ Build Slack blocks (header, sections, context)
    │   ├─ Add color-coded attachments
    │   ├─ Send HTTP POST to Slack webhook
    │   └─ Return success/failure (expects HTTP 200)
    │
    └─→ send_macos_notification(title, message, sound)
        └─ Always sent for local reliability
```

### Slack Blocks Format

The integration uses Slack's **Block Kit** for rich formatting:

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ Homebrew Update Complete!",
        "emoji": true
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "📦 **Formulae Upgraded (3):**\n  • python@3.12\n  • git\n  • wget"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "_MacBook-Pro.local_ • 2025-01-15 10:30:45"
        }
      ]
    }
  ],
  "attachments": [
    {
      "color": "#36a64f"
    }
  ]
}
```

### Block Types Used

| Block Type | Purpose | Example |
|------------|---------|---------|
| `header` | Large title with emoji | "✅ Homebrew Update Complete!" |
| `section` | Body content with markdown | Package lists, status messages |
| `context` | Footer metadata | Hostname and timestamp |
| `attachments` | Color sidebar | Green (#36a64f) for success, Red (#FF0000) for errors |

## Notification Examples

### Success Notification

**Appears in Slack as:**

> # ✅ Homebrew Update Complete!
>
> 📦 **Formulae Upgraded (3):**
> • python@3.12
> • git
> • wget
>
> 🍺 **Casks Upgraded (2):**
> • google-chrome
> • visual-studio-code
>
> 👻 **Ghost Casks Removed (1):**
> • broken-app
>
> 🧹 **Cleanup:** Complete
> 🔐 **Sudo Operations:** Executed (casks & ghost healing)
>
> _MacBook-Pro.local • 2025-01-15 10:30:45_

**Color:** Green sidebar

### Error Notification

**Appears in Slack as:**

> # ❌ Homebrew update FAILED!
>
> **Error:** Failed to upgrade casks
>
> 🔐 Sudo operations were executed for ghost healing & some casks
>
> _MacBook-Pro.local • 2025-01-15 10:30:45_

**Color:** Red sidebar

### Idle Notification

> # ⏸️ User idle - running formulae updates only
>
> _MacBook-Pro.local • 2025-01-15 10:30:45_

**Color:** Green sidebar

## Configuration Options

### Platform Selection

Choose your notification destination via `NOTIFICATION_PLATFORM`:

| Value | Behavior |
|-------|----------|
| `slack` | Slack webhooks only (recommended for Slack users) |
| `discord` | Discord webhooks only (default for backwards compatibility) |
| `both` | Send to both Slack AND Discord simultaneously |

**Example - Slack only:**
```bash
NOTIFICATION_PLATFORM=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Example - Both platforms:**
```bash
NOTIFICATION_PLATFORM=both
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
DISCORD_USER_ID=YOUR_DISCORD_USER_ID
```

### Webhook URL Format

Slack webhook URLs follow this pattern:
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

- **T-prefix**: Workspace/Team ID
- **B-prefix**: Bot/App ID
- **Final segment**: Secret token

**Security:** The webhook URL is sensitive - keep it in `.env` (gitignored) and never commit it.

## Advanced Features

### Custom Notification Channels

To send notifications to different channels:

1. Create multiple webhooks in Slack (one per channel)
2. Use different `.env` files or environment variables per deployment
3. Or create multiple Slack apps with different webhook destinations

### Emoji Support

Slack automatically renders emoji codes:
- ✅ Success checkmark
- ❌ Error cross
- 🚀 Start rocket
- ⏸️ Pause symbol
- 👻 Ghost (for broken casks)
- 🧹 Broom (for cleanup)
- 🔐 Lock (for sudo operations)

### Markdown Formatting

Slack supports **mrkdwn** (Slack's markdown variant):

```markdown
**Bold text**
_Italic text_
• Bullet points
```

**Note:** Standard Discord markdown (`**bold**`) is automatically converted by the `_send_slack()` function.

## Troubleshooting

### No Notifications Received

**Check 1: Webhook URL**
```bash
# Verify webhook is set correctly
grep SLACK_WEBHOOK_URL .env

# Should output:
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

**Check 2: Platform Setting**
```bash
# Verify platform is set to slack or both
grep NOTIFICATION_PLATFORM .env

# Should output:
# NOTIFICATION_PLATFORM=slack
# OR
# NOTIFICATION_PLATFORM=both
```

**Check 3: Test Webhook Directly**
```bash
python3 tests/test_slack_webhook.py
```

Expected output:
```
🧪 Slack Webhook & Notification Test Suite
============================================================
...
✅ PASSED: Webhook is reachable and responding
...
🎉 All Slack webhook tests passed!
```

### HTTP 404 Error

**Cause:** Webhook URL is invalid or has been deleted.

**Fix:**
1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to "Incoming Webhooks"
4. Verify the webhook still exists
5. If deleted, create a new webhook and update `.env`

### HTTP 410 Error

**Cause:** Webhook URL has been revoked.

**Fix:**
1. Create a new webhook in Slack
2. Update `SLACK_WEBHOOK_URL` in `.env`
3. Reload environment or restart LaunchAgent

### Messages Not Formatted Correctly

**Cause:** Slack blocks syntax error.

**Debug:**
1. Check logs: `tail -f ~/Library/Logs/homebrew-updater/homebrew-updater-*.log`
2. Look for "Failed to send Slack notification" errors
3. Run test: `python3 tests/test_slack_webhook.py`
4. Check Slack's Block Kit Builder: https://app.slack.com/block-kit-builder

### macOS Notifications Work But Slack Doesn't

**Cause:** Likely a webhook configuration issue.

**Check:**
```bash
# Test Slack webhook directly
curl -X POST \
  -H 'Content-Type: application/json' \
  --data '{"text":"Test from curl"}' \
  YOUR_SLACK_WEBHOOK_URL

# Should return: ok
```

If curl works but Python doesn't, check Python's SSL certificates:
```bash
/Applications/Python\ 3.*/Install\ Certificates.command
```

## Comparison: Slack vs Discord

| Feature | Slack | Discord |
|---------|-------|---------|
| **Blocks/Embeds** | Slack Blocks | Discord Embeds |
| **Formatting** | mrkdwn | Markdown |
| **User Mentions** | Not supported in webhooks | `<@USER_ID>` supported |
| **Response Code** | HTTP 200 | HTTP 204 |
| **Rate Limits** | 1 message/second | 30 messages/minute |
| **Color Sidebar** | `attachments.color` | `embeds.color` |
| **Best For** | Team/enterprise workflows | Gaming communities, personal use |

## Testing

### Unit Tests

```bash
# Run all tests including Slack integration
python3 tests/test_homebrew_updater.py

# Should see:
# test_send_slack_helper_success ... ok
# test_send_notification_slack_platform ... ok
```

### Integration Tests

```bash
# Test Slack webhook connectivity
python3 tests/test_slack_webhook.py

# Expected: 5 test messages in Slack channel
```

### Manual Testing

```bash
# Send test notification
python3 -c "
import sys
sys.path.insert(0, 'scripts')
import homebrew_updater
homebrew_updater.send_notification('🧪 Test notification from manual script')
"
```

## Security Best Practices

### Webhook URL Protection

**DO:**
- ✅ Store webhook URL in `.env` file (gitignored)
- ✅ Use environment variables in production
- ✅ Regenerate webhooks if accidentally exposed
- ✅ Use separate webhooks for development and production

**DON'T:**
- ❌ Commit `.env` to git
- ❌ Share webhook URLs in public channels
- ❌ Hardcode webhook URLs in scripts
- ❌ Log webhook URLs to files

### Webhook Rotation

To rotate a compromised webhook:

1. Go to https://api.slack.com/apps
2. Select your app → "Incoming Webhooks"
3. Delete the old webhook
4. Create a new webhook
5. Update `.env` with new URL
6. Reload LaunchAgent: `launchctl unload/load ~/Library/LaunchAgents/com.homebrew-updater.plist`

## Additional Resources

- **Slack Block Kit:** https://api.slack.com/block-kit
- **Block Kit Builder:** https://app.slack.com/block-kit-builder
- **Incoming Webhooks:** https://api.slack.com/messaging/webhooks
- **Slack API Docs:** https://api.slack.com/docs

## Support

For issues or questions:

1. Check logs: `~/Library/Logs/homebrew-updater/homebrew-updater-*.log`
2. Run tests: `python3 tests/test_slack_webhook.py`
3. Review this guide
4. Open an issue on GitHub with logs and error messages
