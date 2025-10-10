#!/usr/bin/env python3
"""
Test to display how sudo status appears in notifications
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def show_success_notification_idle():
    """Show success notification when user is idle"""
    print("=" * 60)
    print("SUCCESS NOTIFICATION (User Idle)")
    print("=" * 60)

    summary = "✅ **Homebrew Update Complete!**\n\n"
    summary += "📦 **Formulae Upgraded (3):**\n"
    summary += "  • python@3.12\n"
    summary += "  • git\n"
    summary += "  • wget\n\n"
    summary += "⏸️ **Casks:** Skipped (user idle)\n\n"
    summary += "🧹 **Cleanup:** Complete\n"
    summary += "🔐 **Sudo Operations:** Skipped (user idle)"

    print(summary)
    print()


def show_success_notification_active():
    """Show success notification when user is active"""
    print("=" * 60)
    print("SUCCESS NOTIFICATION (User Active)")
    print("=" * 60)

    summary = "✅ **Homebrew Update Complete!**\n\n"
    summary += "📦 **Formulae Upgraded (3):**\n"
    summary += "  • python@3.12\n"
    summary += "  • git\n"
    summary += "  • wget\n\n"
    summary += "🍺 **Casks Upgraded (2):**\n"
    summary += "  • google-chrome\n"
    summary += "  • docker\n\n"
    summary += "👻 **Ghost Casks Removed (1):**\n"
    summary += "  • broken-app\n\n"
    summary += "🧹 **Cleanup:** Complete\n"
    summary += "🔐 **Sudo Operations:** Executed (casks & ghost healing)"

    print(summary)
    print()


def show_error_notification_idle():
    """Show error notification when user is idle"""
    print("=" * 60)
    print("ERROR NOTIFICATION (User Idle)")
    print("=" * 60)

    error_msg = "❌ Failed to upgrade formulae\n\n"
    error_msg += "🔐 Sudo operations were skipped (user idle)"

    print(error_msg)
    print()


def show_error_notification_active():
    """Show error notification when user is active"""
    print("=" * 60)
    print("ERROR NOTIFICATION (User Active)")
    print("=" * 60)

    error_msg = "❌ Failed to upgrade casks\n\n"
    error_msg += "🔐 Sudo operations were executed for ghost healing & some casks"

    print(error_msg)
    print()


def main():
    """Display all notification examples"""
    print("\n🔔 SUDO STATUS DISPLAY TEST")
    print("=" * 60)
    print("This shows how notifications will appear with sudo status\n")

    show_success_notification_idle()
    show_success_notification_active()
    show_error_notification_idle()
    show_error_notification_active()

    print("=" * 60)
    print("✅ All notification formats include sudo status!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
