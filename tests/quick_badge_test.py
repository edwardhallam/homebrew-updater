#!/usr/bin/env python3
"""
Quick test of new badge notification format
Sends test messages using the updated notification function
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


def main():
    """Send test notifications with new format"""
    print("="*60)
    print("Quick Badge Notification Test")
    print("="*60)
    print()
    print("Sending 4 test messages with CONTENT + EMBED format...")
    print("These should trigger badge notifications!")
    print()

    tests = [
        ("Start", "🚀 Starting Homebrew update...", False),
        ("Success", "✅ **Homebrew Update Complete!**\n\n📦 Formulae: 3 upgraded\n🍺 Casks: 2 upgraded", False),
        ("Error", "❌ Homebrew update FAILED!\n\nCheck the logs for details.", True),
        ("Idle", "⏸️ User idle - running formulae updates only", False),
    ]

    print("Sending test messages...")
    print("-" * 60)

    for test_name, message, is_error in tests:
        print(f"\n{test_name}: {message.split(chr(10))[0]}...")
        homebrew_updater.send_discord_notification(message, error=is_error)
        time.sleep(2)  # Pause between messages

    print("\n" + "="*60)
    print("✅ Test messages sent!")
    print("="*60)
    print()
    print("📱 CHECK YOUR DISCORD NOW:")
    print()
    print("You should see:")
    print("  • 4 new messages")
    print("  • RED BADGE with number 4 (or +4 if you had unread)")
    print("  • Each message has:")
    print("    - Content text at the top (triggers notification)")
    print("    - Rich embed below (formatting)")
    print()
    print("If you see the badge, the fix is working! 🎉")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
