# Homebrew Auto-Updater

**Automated Homebrew package management for macOS with intelligent scheduling and dual notifications.**

Keep your Homebrew packages and casks up-to-date automatically with smart idle detection, Slack/Discord webhooks, native macOS notifications, and automatic ghost cask healing.

## ✨ Features

- **🔔 Dual Notification System**: Slack/Discord webhooks + native macOS notifications for reliable alerts
- **🌐 Flexible Platform Support**: Choose Discord, Slack, or both for webhook notifications
- **🖱️ Intelligent Idle Detection**: Skips sudo-requiring operations when system is idle
- **👻 Ghost Cask Healing**: Automatically removes broken cask installations
- **📦 Complete Package Management**: Updates formulae, casks, and cleans up old files
- **🏥 Health Checks**: Runs `brew doctor` after updates
- **📊 Detailed Reporting**: Shows exactly which packages were upgraded
- **🔐 Secure Configuration**: Environment variables for sensitive data
- **⏰ Scheduled Execution**: LaunchAgent runs daily at configurable time
- **🚀 Performance Optimized**: Batch operations for speed

## 📋 Requirements

- macOS (tested on macOS 10.15+)
- Homebrew installed
- Python 3.7+
- Slack or Discord webhook (optional, for remote notifications)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/homebrew-updater.git
cd homebrew-updater
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your details:

```bash
cp .env.example .env
```

#### Choose Your Notification Platform

You can use **Slack**, **Discord**, or **both**. Edit `.env` with your configuration:

**For Slack notifications:**

```bash
# Choose notification platform
NOTIFICATION_PLATFORM=slack

# Slack webhook URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Optional: Customize these if needed
BREW_PATH=/opt/homebrew/bin/brew
IDLE_THRESHOLD_SECONDS=300
MAX_LOG_FILES=10
```

**For Discord notifications:**

```bash
# Choose notification platform
NOTIFICATION_PLATFORM=discord

# Discord webhook URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# Optional: Your Discord user ID for @mentions
DISCORD_USER_ID=YOUR_USER_ID_HERE

# Optional: Customize these if needed
BREW_PATH=/opt/homebrew/bin/brew
IDLE_THRESHOLD_SECONDS=300
MAX_LOG_FILES=10
```

**For both platforms:**

```bash
# Choose notification platform
NOTIFICATION_PLATFORM=both

# Both webhook URLs
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
DISCORD_USER_ID=YOUR_USER_ID_HERE
```

#### Setting Up Slack Webhook

1. Go to https://api.slack.com/apps
2. Create a new app (or use existing)
3. Navigate to "Incoming Webhooks"
4. Activate Incoming Webhooks
5. Click "Add New Webhook to Workspace"
6. Select the channel for notifications
7. Copy the webhook URL

#### Setting Up Discord Webhook

1. Open Discord → Server Settings → Integrations → Webhooks
2. Create a new webhook
3. Copy the webhook URL

**Optional - Getting your Discord User ID (for @mentions):**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your username → Copy User ID

### 3. Test the Script

Run manually to verify everything works:

```bash
python3 scripts/homebrew_updater.py
```

Check the logs:

```bash
tail -f ~/Library/Logs/homebrew-updater/homebrew-updater-*.log
```

### 4. Install LaunchAgent (Optional)

To run automatically every day at 10:00 AM:

```bash
# Copy the plist file
cp launchd/com.homebrew-updater.plist ~/Library/LaunchAgents/

# Edit the plist to update the script path
# Replace /path/to/homebrew-updater with your actual installation path
nano ~/Library/LaunchAgents/com.homebrew-updater.plist

# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.homebrew-updater.plist

# Verify it's loaded
launchctl list | grep homebrew-updater
```

**Important:** Edit the plist file and replace `/path/to/homebrew-updater` with your actual installation path, and add your Discord webhook URL and user ID in the `EnvironmentVariables` section.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTIFICATION_PLATFORM` | Notification platform: `discord`, `slack`, or `both` | `discord` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | _(none)_ |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for notifications | _(none)_ |
| `DISCORD_USER_ID` | Discord user ID for @mentions | _(none)_ |
| `BREW_PATH` | Path to Homebrew binary | `/opt/homebrew/bin/brew` |
| `IDLE_THRESHOLD_SECONDS` | Idle time threshold (seconds) | `300` (5 minutes) |
| `MAX_LOG_FILES` | Number of log files to retain | `10` |

### Idle Detection Behavior

The updater checks system idle time before running:

- **User Active** (< 5 minutes idle):
  - Updates all formulae
  - Updates all casks (including those requiring sudo)
  - Heals ghost casks
  - Full cleanup

- **User Idle** (> 5 minutes idle):
  - Updates formulae only
  - Skips cask updates (avoids sudo password prompts)
  - Skips ghost healing

## 📝 How It Works

1. **Scheduled Execution**: LaunchAgent triggers at configured time (default: 10:00 AM daily)
2. **Idle Check**: Determines if user is active or idle
3. **Package Updates**:
   - Updates Homebrew itself
   - Heals ghost casks (if user active)
   - Upgrades formulae
   - Upgrades casks (if user active)
4. **Cleanup**: Removes old downloads and cache files
5. **Health Check**: Runs `brew doctor` for diagnostics
6. **Notifications**: Sends detailed summary to Slack/Discord and macOS Notification Center

## 🔔 Notification Examples

**Success Notification:**
```
✅ Homebrew Update Complete!

📦 Formulae Upgraded (3):
  • python@3.12
  • git
  • wget

🍺 Casks Upgraded (2):
  • google-chrome
  • visual-studio-code

👻 Ghost Casks Removed (1):
  • broken-app

🧹 Cleanup: Complete
🔐 Sudo Operations: Executed (casks & ghost healing)
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Unit tests
python3 tests/test_homebrew_updater.py

# Integration tests
bash tests/integration_test.sh
```

## 📂 Project Structure

```
homebrew-updater/
├── scripts/
│   ├── homebrew_updater.py          # Main updater script
│   └── brew_autoupdate_sudo_gui     # Sudo GUI helper
├── launchd/
│   └── com.homebrew-updater.plist   # LaunchAgent configuration
├── tests/
│   ├── test_homebrew_updater.py     # Unit tests
│   └── integration_test.sh          # Integration tests
├── docs/                             # Development documentation
├── .env.example                      # Environment variable template
├── .gitignore
├── README.md
└── CLAUDE.md                         # Claude Code assistant instructions
```

## 🔧 Troubleshooting

### No notifications received

- **Slack**: Verify webhook URL is correct in `.env` and `NOTIFICATION_PLATFORM=slack` or `both`
- **Discord**: Verify webhook URL is correct in `.env` and `NOTIFICATION_PLATFORM=discord` or `both`
- **macOS**: Check System Preferences → Notifications → Script Editor
- **Test webhooks**: Run `python3 tests/test_slack_webhook.py` or `python3 tests/test_discord_webhook.py`

### Script not running automatically

```bash
# Check if LaunchAgent is loaded
launchctl list | grep homebrew-updater

# Check LaunchAgent logs
cat /tmp/homebrew-updater.out
cat /tmp/homebrew-updater.err

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.homebrew-updater.plist
launchctl load ~/Library/LaunchAgents/com.homebrew-updater.plist
```

### Permission errors

Ensure the script has execute permissions:

```bash
chmod +x scripts/homebrew_updater.py
chmod +x scripts/brew_autoupdate_sudo_gui
```

### View logs

```bash
# Latest log
tail -f ~/Library/Logs/homebrew-updater/homebrew-updater-*.log

# List all logs
ls -lt ~/Library/Logs/homebrew-updater/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Inspired by [homebrew-autoupdate](https://github.com/DomT4/homebrew-autoupdate)
- Ghost cask detection inspired by various Homebrew community solutions

## 📚 Additional Documentation

See the `docs/` directory for:
- Detailed notification system documentation
- Test reports
- Development notes
- Troubleshooting guides
