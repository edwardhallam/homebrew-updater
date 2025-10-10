#!/usr/bin/env python3
"""
Send test notification with detailed package lists
Shows what the new Discord notification format looks like
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


def send_test_notification():
    """Send a realistic test notification"""
    print("=" * 60)
    print("Sending Test Notification to Discord")
    print("=" * 60)

    # Simulate a realistic update scenario
    summary = "✅ **Homebrew Update Complete!**\n\n"

    # Example formulae
    upgraded_formulae = [
        "python@3.12",
        "git",
        "node",
        "wget",
        "ffmpeg"
    ]

    summary += f"📦 **Formulae Upgraded ({len(upgraded_formulae)}):**\n"
    for formula in upgraded_formulae:
        summary += f"  • {formula}\n"
    summary += "\n"

    # Example casks
    upgraded_casks = [
        "google-chrome",
        "visual-studio-code",
        "docker"
    ]

    summary += f"🍺 **Casks Upgraded ({len(upgraded_casks)}):**\n"
    for cask in upgraded_casks:
        summary += f"  • {cask}\n"
    summary += "\n"

    # Example ghost casks
    removed_ghosts = [
        "old-app",
        "broken-cask"
    ]

    summary += f"👻 **Ghost Casks Removed ({len(removed_ghosts)}):**\n"
    for ghost in removed_ghosts:
        summary += f"  • {ghost}\n"
    summary += "\n"

    summary += "🧹 **Cleanup:** Complete"

    print("\nMessage content:")
    print("-" * 60)
    print(summary)
    print("-" * 60)

    print("\nSending to Discord...")

    try:
        homebrew_updater.send_discord_notification(summary)
        print("✅ Test notification sent successfully!")
        print("\nCheck your Discord channel for the detailed message.")
        return 0
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return 1


def send_simple_test():
    """Send a simple test to verify webhook is working"""
    print("\n" + "=" * 60)
    print("Sending Simple Test Message")
    print("=" * 60)

    message = "🧪 **Test Message**\n\nThis is a test of the detailed notification format!"

    try:
        homebrew_updater.send_discord_notification(message)
        print("✅ Simple test sent successfully!")
        return 0
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1


def send_no_updates_test():
    """Test message when nothing needs updating"""
    print("\n" + "=" * 60)
    print("Sending No Updates Test")
    print("=" * 60)

    summary = "✅ **Homebrew Update Complete!**\n\n"
    summary += "📦 **Formulae:** None to upgrade\n\n"
    summary += "🍺 **Casks:** None to upgrade\n\n"
    summary += "🧹 **Cleanup:** Complete"

    print("\nMessage content:")
    print("-" * 60)
    print(summary)
    print("-" * 60)

    try:
        homebrew_updater.send_discord_notification(summary)
        print("✅ No updates test sent successfully!")
        return 0
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1


def send_idle_test():
    """Test message when user is idle"""
    print("\n" + "=" * 60)
    print("Sending Idle User Test")
    print("=" * 60)

    summary = "✅ **Homebrew Update Complete!**\n\n"

    upgraded_formulae = ["python@3.12", "git"]
    summary += f"📦 **Formulae Upgraded ({len(upgraded_formulae)}):**\n"
    for formula in upgraded_formulae:
        summary += f"  • {formula}\n"
    summary += "\n"

    summary += "⏸️ **Casks:** Skipped (user idle)\n\n"
    summary += "🧹 **Cleanup:** Complete"

    print("\nMessage content:")
    print("-" * 60)
    print(summary)
    print("-" * 60)

    try:
        homebrew_updater.send_discord_notification(summary)
        print("✅ Idle test sent successfully!")
        return 0
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 1


def main():
    """Run all test notifications"""
    print("🧪 Discord Notification Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Webhook: {homebrew_updater.DISCORD_WEBHOOK_URL[:50]}...")
    print("=" * 60)

    tests = [
        ("Simple Test", send_simple_test),
        ("Detailed Update", send_test_notification),
        ("No Updates", send_no_updates_test),
        ("Idle User", send_idle_test),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func() == 0
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results[test_name] = False

        # Pause between messages
        import time
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ SENT" if passed else "❌ FAILED"
        print(f"{test_name:25s} {status}")

    print("=" * 60)

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nSent: {passed_count}/{total_count} messages")
    print("\n✨ Check your Discord channel for all test messages!")

    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
