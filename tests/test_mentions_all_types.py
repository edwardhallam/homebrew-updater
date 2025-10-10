#!/usr/bin/env python3
"""
Test all notification types with user mentions
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


def main():
    """Send test notifications of all types with mentions"""
    print("="*60)
    print("Testing All Notification Types with Mentions")
    print("="*60)
    print(f"Mentioning user: <@{homebrew_updater.DISCORD_USER_ID}>")
    print()
    print("Sending 4 test messages...")
    print("-" * 60)

    tests = [
        ("Start", "🚀 Starting Homebrew update...", False),
        ("Success", "✅ **Homebrew Update Complete!**\n\n📦 **Formulae Upgraded (3):**\n  • python@3.12\n  • git\n  • wget\n\n🍺 **Casks:** None to upgrade\n\n🧹 **Cleanup:** Complete", False),
        ("Error", "❌ Homebrew update FAILED!\n\nError: Test error message\n\nCheck the logs for details.", True),
        ("Idle", "⏸️ User idle - running formulae updates only", False),
    ]

    for test_name, message, is_error in tests:
        print(f"\n{test_name}: Sending...")
        homebrew_updater.send_discord_notification(message, error=is_error)
        print(f"  ✅ Sent with mention")
        time.sleep(2)

    print("\n" + "="*60)
    print("✅ All test messages sent!")
    print("="*60)
    print()
    print("📱 CHECK YOUR DISCORD:")
    print()
    print("You should see 4 messages, each with:")
    print("  • Your username mentioned and highlighted")
    print("  • Discord notification/ping for each")
    print("  • Badge notification showing unread count")
    print()
    print("Did you get notifications for all 4 messages?")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
