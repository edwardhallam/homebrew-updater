#!/usr/bin/env python3
"""
Test push notifications - Discord + macOS native
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


def main():
    """Test all notification methods"""
    print("="*60)
    print("Push Notification Test")
    print("="*60)
    print()
    print("This will send 4 test notifications:")
    print("  • Discord message (with @mention)")
    print("  • macOS Notification Center alert")
    print()
    print("You should see BOTH for each test!")
    print()
    input("Press ENTER to start...")
    print()

    tests = [
        ("Start", "🚀 Starting Homebrew update...", False),
        ("Success", "✅ Homebrew Update Complete! - 5 packages upgraded", False),
        ("Error", "❌ Homebrew update FAILED!", True),
        ("Idle", "⏸️ User idle - formulae only", False),
    ]

    for i, (test_name, message, is_error) in enumerate(tests, 1):
        print(f"\n[{i}/4] {test_name}:")
        print(f"  Message: {message}")
        print(f"  Sending...")

        homebrew_updater.send_discord_notification(message, error=is_error)

        print(f"  ✅ Discord: Sent (check channel)")
        print(f"  ✅ macOS: Sent (check Notification Center)")

        if i < len(tests):
            print(f"  ⏳ Waiting 3 seconds...")
            time.sleep(3)

    print("\n" + "="*60)
    print("✅ All notifications sent!")
    print("="*60)
    print()
    print("VERIFY:")
    print()
    print("1. 📱 DISCORD:")
    print("   • Check Discord channel")
    print("   • Should see 4 messages with @mention")
    print("   • Each should ping you")
    print()
    print("2. 💻 macOS NOTIFICATION CENTER:")
    print("   • Click the clock (top-right)")
    print("   • Look for 'Homebrew Updater' notifications")
    print("   • Should see 4 alerts")
    print("   • Different sounds for errors (Basso) vs success (Glass)")
    print()
    print("3. 🔔 PUSH NOTIFICATIONS:")
    print("   • Did you hear notification sounds?")
    print("   • Did banners appear on screen?")
    print("   • Did badge appear on any app icons?")
    print()
    print("If you saw macOS notifications, you'll ALWAYS get alerts")
    print("even if Discord push notifications don't work!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
