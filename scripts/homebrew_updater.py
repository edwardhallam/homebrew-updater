#!/usr/bin/env python3
"""
Homebrew Updater with Discord Notifications
Automatically updates Homebrew formulae and casks with intelligent sudo handling
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
import urllib.request
import urllib.error

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Load .env file if it exists (for local development)
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Discord webhook URL - loaded from environment variable
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Discord user ID for mentions (get via: right-click username → Copy User ID)
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID", "")

# Slack webhook URL - loaded from environment variable
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Notification platform: "discord", "slack", or "both"
# Determines which webhook(s) to use for notifications
NOTIFICATION_PLATFORM = os.getenv("NOTIFICATION_PLATFORM", "discord").lower()

# Idle threshold in seconds (default: 5 minutes)
IDLE_THRESHOLD_SECONDS = int(os.getenv("IDLE_THRESHOLD_SECONDS", "300"))

# Homebrew paths
BREW_PATH = os.getenv("BREW_PATH", "/opt/homebrew/bin/brew")
SUDO_GUI_SCRIPT = Path(__file__).parent / "brew_autoupdate_sudo_gui"

# Logging
LOG_DIR = Path.home() / "Library/Logs/homebrew-updater"
MAX_LOG_FILES = int(os.getenv("MAX_LOG_FILES", "10"))

# Environment setup
BREW_ENV = {
    "PATH": "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    "HOMEBREW_NO_BOTTLE_SOURCE_FALLBACK": "1",
    "HOMEBREW_CACHE": str(Path.home() / "Library/Caches/Homebrew"),
    "HOMEBREW_LOGS": str(Path.home() / "Library/Logs/Homebrew"),
}

if SUDO_GUI_SCRIPT.exists():
    BREW_ENV["SUDO_ASKPASS"] = str(SUDO_GUI_SCRIPT)

# ============================================================================
# LOGGING SETUP
# ============================================================================

LOG_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
LOG_FILE = LOG_DIR / f"homebrew-updater-{TIMESTAMP}.log"

def log(message: str, level: str = "INFO"):
    """Log message to both file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

def cleanup_old_logs():
    """Keep only the most recent MAX_LOG_FILES log files"""
    log_files = sorted(LOG_DIR.glob("homebrew-updater-*.log"), reverse=True)
    for old_log in log_files[MAX_LOG_FILES:]:
        try:
            old_log.unlink()
            log(f"Removed old log file: {old_log.name}")
        except Exception as e:
            log(f"Failed to remove old log {old_log.name}: {e}", "WARN")

# ============================================================================
# WEBHOOK NOTIFICATIONS (Discord & Slack)
# ============================================================================

def send_macos_notification(title: str, message: str, sound: str = "default"):
    """Send native macOS notification"""
    try:
        # Clean message for osascript (escape quotes)
        clean_message = message.replace('"', '\\"').replace("'", "\\'")
        clean_title = title.replace('"', '\\"').replace("'", "\\'")

        # Build osascript command
        script = f'display notification "{clean_message}" with title "{clean_title}" sound name "{sound}"'

        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5
        )
        log("macOS notification sent successfully")
    except Exception as e:
        log(f"Failed to send macOS notification: {e}", "ERROR")


def _send_discord(message: str, error: bool = False) -> bool:
    """Send notification to Discord webhook (internal helper)"""
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN":
        log("Discord webhook not configured, skipping Discord notification", "WARN")
        return False

    color = 0xFF0000 if error else 0x00FF00  # Red for errors, green for success

    # Extract first line or create summary for content field
    # Content field is needed to trigger Discord badge notifications
    first_line = message.split('\n')[0].strip()
    if not first_line:
        first_line = "🔔 Homebrew Updater Notification"

    # Add user mention for notifications
    mention = f"<@{DISCORD_USER_ID}>" if DISCORD_USER_ID else ""
    content = f"{mention} {first_line}" if mention else first_line

    # Build payload with both content (for notifications) and embeds (for formatting)
    payload = {
        "content": content,  # This triggers badge notifications and mentions user
        "embeds": [{
            "title": "Homebrew Updater",
            "description": message,
            "color": color,
            "timestamp": datetime.now().astimezone().isoformat(),
            "footer": {"text": os.uname().nodename}
        }]
    }

    # Send to Discord
    try:
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0 (Python)'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                log("Discord notification sent successfully")
                return True
            else:
                log(f"Discord notification returned status {response.status}", "WARN")
                return False
    except urllib.error.URLError as e:
        log(f"Failed to send Discord notification: {e}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error sending Discord notification: {e}", "ERROR")
        return False


def _send_slack(message: str, error: bool = False) -> bool:
    """Send notification to Slack webhook using blocks (internal helper)"""
    if not SLACK_WEBHOOK_URL:
        log("Slack webhook not configured, skipping Slack notification", "WARN")
        return False

    # Parse message into structured sections
    lines = message.split('\n')
    first_line = lines[0].strip() if lines else "Homebrew Updater Notification"

    # Build Slack blocks for rich formatting
    blocks = []

    # Header block with first line (emoji + title)
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": first_line,
            "emoji": True
        }
    })

    # Parse remaining lines into sections
    current_section = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            # Empty line: flush current section
            if current_section:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "\n".join(current_section)
                    }
                })
                current_section = []
        elif line.startswith("**") or line.startswith("•") or line.startswith("🔐") or line.startswith("🧹"):
            # Markdown bold or list item
            current_section.append(line)
        else:
            current_section.append(line)

    # Flush any remaining section
    if current_section:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(current_section)
            }
        })

    # Add context footer with hostname and timestamp
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"_{os.uname().nodename}_ • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        ]
    })

    # Color-coded attachment
    attachment_color = "#FF0000" if error else "#36a64f"  # Red or green

    payload = {
        "blocks": blocks,
        "attachments": [{
            "color": attachment_color
        }]
    }

    # Send to Slack
    try:
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0 (Python)'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                log("Slack notification sent successfully")
                return True
            else:
                log(f"Slack notification returned status {response.status}", "WARN")
                return False
    except urllib.error.URLError as e:
        log(f"Failed to send Slack notification: {e}", "ERROR")
        return False
    except Exception as e:
        log(f"Unexpected error sending Slack notification: {e}", "ERROR")
        return False


def send_notification(message: str, error: bool = False):
    """Send notification via configured platform(s) and macOS notification center"""
    # Extract first line for macOS notification
    first_line = message.split('\n')[0].strip() or "Homebrew Updater Notification"
    sound = "Basso" if error else "Glass"

    # Track if any webhook succeeded
    webhook_sent = False

    # Send to configured platform(s)
    if NOTIFICATION_PLATFORM in ("discord", "both"):
        if _send_discord(message, error):
            webhook_sent = True

    if NOTIFICATION_PLATFORM in ("slack", "both"):
        if _send_slack(message, error):
            webhook_sent = True

    # Always send macOS notification for reliable local alerts
    send_macos_notification("Homebrew Updater", first_line, sound=sound)

    # If no webhooks configured or all failed, warn but don't fail
    if not webhook_sent and NOTIFICATION_PLATFORM != "":
        log("No webhook notifications were sent (check configuration)", "WARN")


# Backwards compatibility alias
def send_discord_notification(message: str, error: bool = False):
    """Deprecated: Use send_notification() instead. Kept for backwards compatibility."""
    send_notification(message, error)

# ============================================================================
# IDLE DETECTION
# ============================================================================

def get_idle_time_seconds() -> Optional[int]:
    """Get system idle time in seconds using ioreg"""
    try:
        result = subprocess.run(
            ["ioreg", "-c", "IOHIDSystem"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Look for HIDIdleTime in output
        match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', result.stdout)
        if match:
            # HIDIdleTime is in nanoseconds
            idle_ns = int(match.group(1))
            idle_seconds = idle_ns / 1_000_000_000
            return int(idle_seconds)
    except Exception as e:
        log(f"Failed to get idle time: {e}", "ERROR")

    return None

def is_user_idle() -> bool:
    """Check if user has been idle for more than threshold"""
    idle_seconds = get_idle_time_seconds()
    if idle_seconds is None:
        log("Could not determine idle time, assuming user is present", "WARN")
        return False

    log(f"System idle time: {idle_seconds} seconds")
    return idle_seconds > IDLE_THRESHOLD_SECONDS

# ============================================================================
# HOMEBREW OPERATIONS
# ============================================================================

def run_brew_command(args: List[str], check: bool = True) -> Tuple[bool, str]:
    """Run a brew command and return success status and output"""
    cmd = [BREW_PATH] + args
    log(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, **BREW_ENV},
            timeout=3600  # 1 hour timeout
        )

        output = result.stdout + result.stderr

        # Log output
        for line in output.splitlines():
            if line.strip():
                log(f"  {line}")

        if check and result.returncode != 0:
            return False, output

        return True, output

    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out: {' '.join(cmd)}"
        log(error_msg, "ERROR")
        return False, error_msg
    except Exception as e:
        error_msg = f"Command failed: {e}"
        log(error_msg, "ERROR")
        return False, error_msg

def get_caskroom_path() -> Path:
    """Get the Caskroom directory path"""
    success, output = run_brew_command(["--caskroom"], check=False)
    if success:
        return Path(output.strip())
    return Path("/opt/homebrew/Caskroom")

def heal_ghost_casks(skip_sudo: bool = False) -> List[str]:
    """Remove ghost casks that are installed in Homebrew but missing from system"""
    log("Scanning for ghost casks...")

    removed_casks = []
    ghost_casks = []

    # Get list of installed casks
    success, output = run_brew_command(["list", "--cask"], check=False)
    if not success:
        log("Could not get cask list", "WARN")
        return removed_casks

    casks = [c.strip() for c in output.strip().split('\n') if c.strip()]
    caskroom = get_caskroom_path()

    # First pass: Identify casks that definitely have issues or need detailed checking
    casks_needing_detailed_check = []

    for cask in casks:
        # Skip fonts and quicklook plugins (often no .app artifacts)
        if cask.startswith('font-') or cask.startswith('ql'):
            continue

        cask_dir = caskroom / cask

        # Definitely ghost if directory doesn't exist or is empty
        if not cask_dir.exists():
            ghost_casks.append(cask)
        elif not list(cask_dir.iterdir()):
            ghost_casks.append(cask)
        else:
            # Has directory with content - needs detailed artifact checking
            casks_needing_detailed_check.append(cask)

    # Second pass: Batch check artifacts for casks with directories
    if casks_needing_detailed_check:
        log(f"Checking {len(casks_needing_detailed_check)} casks for missing applications...")

        # Batch fetch all cask info in one call
        cmd = [BREW_PATH, "info", "--cask", "--json=v2"] + casks_needing_detailed_check
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, **BREW_ENV},
                timeout=60  # 1 minute should be enough for batch query
            )

            if result.returncode == 0:
                try:
                    info = json.loads(result.stdout + result.stderr)
                    if info and 'casks' in info:
                        for cask_info in info['casks']:
                            cask_name = cask_info.get('token', '')
                            artifacts = cask_info.get('artifacts', [])
                            apps = []

                            for artifact in artifacts:
                                if isinstance(artifact, dict) and 'app' in artifact:
                                    apps.extend(artifact['app'])

                            # If cask defines apps, check if any exist
                            if apps:
                                found = False
                                for app in apps:
                                    app_path = Path("/Applications") / app
                                    home_app_path = Path.home() / "Applications" / app
                                    if app_path.exists() or home_app_path.exists():
                                        found = True
                                        break

                                if not found:
                                    ghost_casks.append(cask_name)
                except json.JSONDecodeError as e:
                    log(f"Failed to parse cask info JSON: {e}", "WARN")
        except subprocess.TimeoutExpired:
            log("Batch cask info check timed out, skipping detailed checks", "WARN")
        except Exception as e:
            log(f"Error during batch cask check: {e}", "WARN")

    # Remove identified ghost casks
    if ghost_casks:
        log(f"Found {len(ghost_casks)} ghost cask(s): {', '.join(ghost_casks)}")

        for cask in ghost_casks:
            if skip_sudo:
                log(f"Skipping ghost removal (requires sudo): {cask}", "WARN")
            else:
                log(f"Removing ghost cask: {cask}")
                success, _ = run_brew_command(["uninstall", "--cask", "--force", "--zap", cask], check=False)
                if success:
                    removed_casks.append(cask)
    else:
        log("No ghost casks found")

    return removed_casks

def brew_update() -> bool:
    """Run brew update"""
    log("Updating Homebrew...")
    success, _ = run_brew_command(["update"])
    return success

def brew_upgrade_formulae() -> Tuple[bool, List[str]]:
    """Upgrade all formulae and return list of upgraded packages"""
    log("Upgrading formulae...")

    # First check what's outdated
    success, output = run_brew_command(["outdated", "--formula"], check=False)
    outdated_formulae = [line.split()[0] for line in output.splitlines() if line.strip()]

    if not outdated_formulae:
        log("No outdated formulae")
        return True, []

    log(f"Found {len(outdated_formulae)} outdated formulae: {', '.join(outdated_formulae)}")
    success, _ = run_brew_command(["upgrade", "--formula"])
    return success, outdated_formulae if success else []

def brew_upgrade_casks() -> Tuple[bool, List[str]]:
    """Upgrade all casks with greedy flag and return list of upgraded casks"""
    log("Upgrading casks...")

    # First check what's outdated
    success, output = run_brew_command(["outdated", "--cask", "--greedy"], check=False)
    outdated_casks = [line.split()[0] for line in output.splitlines() if line.strip()]

    if not outdated_casks:
        log("No outdated casks")
        return True, []

    log(f"Found {len(outdated_casks)} outdated casks: {', '.join(outdated_casks)}")
    success, _ = run_brew_command(["upgrade", "--cask", "--greedy"])
    return success, outdated_casks if success else []

def brew_cleanup():
    """Clean up old downloads and cache aggressively"""
    log("Cleaning up Homebrew cache and downloads...")
    run_brew_command(["cleanup", "-s"], check=False)

def brew_doctor():
    """Run brew doctor for diagnostics"""
    log("Running brew doctor...")
    success, output = run_brew_command(["doctor"], check=False)
    if not success:
        log("brew doctor found some issues (non-fatal)", "WARN")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution flow"""
    log("=" * 80)
    log("Homebrew Updater Started")
    log("=" * 80)

    # Clean up old logs first
    cleanup_old_logs()

    # Send start notification
    send_notification("🚀 Starting Homebrew update...")

    try:
        # Check if user is idle
        user_idle = is_user_idle()

        if user_idle:
            log("User is idle - will skip cask updates requiring sudo")
            send_notification("⏸️ User idle - running formulae updates only")
        else:
            log("User is active - proceeding with full update")

        # Update Homebrew
        if not brew_update():
            error_msg = "Failed to update Homebrew"
            log(error_msg, "ERROR")
            sudo_status = "🔐 Sudo operations were skipped (user idle)" if user_idle else "🔐 Sudo operations would have been executed"
            send_notification(f"❌ {error_msg}\n\n{sudo_status}", error=True)
            return 1

        # Heal ghost casks (skip if idle to avoid sudo)
        removed_ghosts = heal_ghost_casks(skip_sudo=user_idle)

        # Upgrade formulae
        success, upgraded_formulae = brew_upgrade_formulae()
        if not success:
            error_msg = "Failed to upgrade formulae"
            log(error_msg, "ERROR")
            sudo_status = "🔐 Sudo operations were skipped (user idle)" if user_idle else "🔐 Sudo operations were executed for ghost healing"
            send_notification(f"❌ {error_msg}\n\n{sudo_status}", error=True)
            return 1

        upgraded_casks = []
        if not user_idle:
            # Upgrade casks (only if user is not idle)
            success, upgraded_casks = brew_upgrade_casks()
            if not success:
                error_msg = "Failed to upgrade casks"
                log(error_msg, "ERROR")
                sudo_status = "🔐 Sudo operations were executed for ghost healing & some casks"
                send_notification(f"❌ {error_msg}\n\n{sudo_status}", error=True)
                return 1
        else:
            log("Skipping cask updates (user idle)")

        # Cleanup
        brew_cleanup()

        # Run doctor
        brew_doctor()

        # Success notification
        log("=" * 80)
        log("Homebrew update completed successfully")
        log(f"Upgraded: {len(upgraded_formulae)} formulae, {len(upgraded_casks)} casks")
        log("=" * 80)

        # Build detailed summary for Discord
        summary = "✅ **Homebrew Update Complete!**\n\n"

        if upgraded_formulae:
            summary += f"📦 **Formulae Upgraded ({len(upgraded_formulae)}):**\n"
            for formula in upgraded_formulae:
                summary += f"  • {formula}\n"
            summary += "\n"
        else:
            summary += "📦 **Formulae:** None to upgrade\n\n"

        if not user_idle:
            if upgraded_casks:
                summary += f"🍺 **Casks Upgraded ({len(upgraded_casks)}):**\n"
                for cask in upgraded_casks:
                    summary += f"  • {cask}\n"
                summary += "\n"
            else:
                summary += "🍺 **Casks:** None to upgrade\n\n"
        else:
            summary += "⏸️ **Casks:** Skipped (user idle)\n\n"

        if removed_ghosts:
            summary += f"👻 **Ghost Casks Removed ({len(removed_ghosts)}):**\n"
            for ghost in removed_ghosts:
                summary += f"  • {ghost}\n"
            summary += "\n"

        summary += f"🧹 **Cleanup:** Complete\n"

        # Add sudo execution status
        if user_idle:
            summary += f"🔐 **Sudo Operations:** Skipped (user idle)"
        else:
            summary += f"🔐 **Sudo Operations:** Executed (casks & ghost healing)"

        send_notification(summary)

        return 0

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        log(error_msg, "ERROR")
        # Try to get sudo status (user_idle may not be defined if error occurred very early)
        try:
            sudo_status = "🔐 Sudo operations were skipped (user idle)" if user_idle else "🔐 Sudo operations may have been partially executed"
            send_notification(f"❌ {error_msg}\n\n{sudo_status}", error=True)
        except NameError:
            # user_idle not defined, error occurred before idle check
            send_discord_notification(f"❌ {error_msg}\n\n🔐 Sudo status unknown (error occurred during initialization)", error=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
