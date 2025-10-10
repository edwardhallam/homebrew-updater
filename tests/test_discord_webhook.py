#!/usr/bin/env python3
"""
Test Discord webhook connectivity and message formatting
Run with: python3 tests/test_discord_webhook.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater


def test_macos_notification():
    """Test 0: macOS native notification"""
    print("\n" + "="*60)
    print("Test 0: macOS Native Notification")
    print("="*60)

    try:
        homebrew_updater.send_macos_notification(
            "Test Notification",
            "Testing macOS notification system",
            sound="Glass"
        )
        print("✅ macOS notification sent")
        print("   Check for banner/sound on your Mac")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_webhook_connectivity():
    """Test if webhook URL is reachable"""
    print("=" * 60)
    print("Testing Discord Webhook Connectivity")
    print("=" * 60)

    webhook_url = homebrew_updater.DISCORD_WEBHOOK_URL

    if webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("❌ FAILED: Webhook URL not configured")
        print("   Please edit scripts/homebrew_updater.py and set DISCORD_WEBHOOK_URL")
        return False

    print(f"Webhook URL: {webhook_url[:50]}...")

    try:
        # Test with a simple ping message
        payload = {
            "embeds": [{
                "title": "🧪 Discord Webhook Test",
                "description": "Testing webhook connectivity",
                "color": 0x00BFFF,  # Blue
                "timestamp": datetime.now().astimezone().isoformat(),
                "footer": {"text": f"Test from {os.uname().nodename}"}
            }]
        }

        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0 (Test)'
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                print("✅ PASSED: Webhook is reachable and responding")
                return True
            else:
                print(f"⚠️  WARNING: Unexpected status code: {response.status}")
                return False

    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP Error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ FAILED: URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False


def test_notification_types():
    """Test different notification message types"""
    print("\n" + "=" * 60)
    print("Testing Different Notification Types")
    print("=" * 60)

    tests = [
        ("Start notification", "🚀 Starting Homebrew update test...", False),
        ("Success notification", "✅ Test completed: 5 formulae, 3 casks upgraded", False),
        ("Error notification", "❌ Test error: Simulated failure", True),
    ]

    results = []

    for test_name, message, is_error in tests:
        print(f"\nTesting: {test_name}")
        try:
            homebrew_updater.send_discord_notification(message, error=is_error)
            print(f"  ✅ Sent: {message}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append(False)

        # Small delay between messages
        import time
        time.sleep(1)

    return all(results)


def test_message_formatting():
    """Test that messages are properly formatted"""
    print("\n" + "=" * 60)
    print("Testing Message Formatting")
    print("=" * 60)

    test_message = """
📦 Homebrew Update Summary

**Formulae upgraded:** 10
**Casks upgraded:** 5
**Ghost casks removed:** 2
**Cache cleaned:** 1.5 GB

✨ All operations completed successfully!
    """.strip()

    print(f"\nSending formatted message:")
    print(f"  {test_message[:50]}...")

    try:
        homebrew_updater.send_discord_notification(test_message, error=False)
        print("  ✅ Formatted message sent successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to send formatted message: {e}")
        return False


def main():
    """Run all Discord webhook tests"""
    print("🧪 Discord Webhook & Notification Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {
        "macOS Notification": test_macos_notification(),
        "Connectivity": test_webhook_connectivity(),
        "Notification Types": test_notification_types(),
        "Message Formatting": test_message_formatting(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s} {status}")

    print("=" * 60)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All Discord webhook tests passed!")
        print("Check your Discord channel for test messages.")
        return 0
    else:
        print("\n❌ Some Discord webhook tests failed!")
        print("Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
