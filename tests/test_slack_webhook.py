#!/usr/bin/env python3
"""
Test Slack webhook connectivity and message formatting
Run with: python3 tests/test_slack_webhook.py
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
    """Test if Slack webhook URL is reachable"""
    print("=" * 60)
    print("Testing Slack Webhook Connectivity")
    print("=" * 60)

    webhook_url = homebrew_updater.SLACK_WEBHOOK_URL

    if not webhook_url:
        print("❌ FAILED: Slack webhook URL not configured")
        print("   Please set SLACK_WEBHOOK_URL in .env file")
        return False

    print(f"Webhook URL: {webhook_url[:50]}...")

    try:
        # Test with a simple ping message using Slack blocks
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🧪 Slack Webhook Test",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Testing webhook connectivity"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"_{os.uname().nodename}_ • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ],
            "attachments": [{
                "color": "#00BFFF"  # Blue
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
            if response.status == 200:
                print("✅ PASSED: Webhook is reachable and responding")
                print("   Check your Slack channel for the test message")
                return True
            else:
                print(f"⚠️  WARNING: Unexpected status code: {response.status}")
                return False

    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP Error {e.code}: {e.reason}")
        if e.code == 404:
            print("   The webhook URL may be invalid or deleted")
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
            # Use the internal _send_slack function directly
            success = homebrew_updater._send_slack(message, error=is_error)
            if success:
                print(f"  ✅ Sent: {message}")
                results.append(True)
            else:
                print(f"  ⚠️  Sent but got warning: {message}")
                results.append(False)
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results.append(False)

        # Small delay between messages
        import time
        time.sleep(1)

    return all(results)


def test_message_formatting():
    """Test that messages are properly formatted with Slack blocks"""
    print("\n" + "=" * 60)
    print("Testing Message Formatting (Slack Blocks)")
    print("=" * 60)

    test_message = """✅ **Homebrew Update Complete!**

📦 **Formulae Upgraded (3):**
  • python@3.12
  • git
  • wget

🍺 **Casks Upgraded (2):**
  • visual-studio-code
  • slack

👻 **Ghost Casks Removed (1):**
  • broken-app

🧹 **Cleanup:** Complete
🔐 **Sudo Operations:** Executed (casks & ghost healing)
    """.strip()

    print(f"\nSending formatted message with multiple sections:")
    print(f"  (Check Slack for rich block formatting)")

    try:
        success = homebrew_updater._send_slack(test_message, error=False)
        if success:
            print("  ✅ Formatted message sent successfully")
            print("     Verify in Slack that you see:")
            print("     - Header block with emoji")
            print("     - Sections with markdown formatting")
            print("     - Context footer with hostname")
            print("     - Green color bar on left")
            return True
        else:
            print("  ⚠️  Message sent but got warning")
            return False
    except Exception as e:
        print(f"  ❌ Failed to send formatted message: {e}")
        return False


def test_error_formatting():
    """Test error message formatting (red color)"""
    print("\n" + "=" * 60)
    print("Testing Error Message Formatting")
    print("=" * 60)

    error_message = """❌ Homebrew update FAILED!

**Error:** Failed to upgrade casks

🔐 Sudo operations were executed for ghost healing & some casks
    """.strip()

    print(f"\nSending error message:")
    print(f"  (Should appear with RED color bar in Slack)")

    try:
        success = homebrew_updater._send_slack(error_message, error=True)
        if success:
            print("  ✅ Error message sent successfully")
            print("     Verify in Slack that the color bar is RED")
            return True
        else:
            print("  ⚠️  Message sent but got warning")
            return False
    except Exception as e:
        print(f"  ❌ Failed to send error message: {e}")
        return False


def main():
    """Run all Slack webhook tests"""
    print("🧪 Slack Webhook & Notification Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check if Slack is configured
    if not homebrew_updater.SLACK_WEBHOOK_URL:
        print("\n❌ ERROR: SLACK_WEBHOOK_URL is not configured")
        print("Please set SLACK_WEBHOOK_URL in your .env file")
        print("\nExample:")
        print("  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
        return 1

    results = {
        "macOS Notification": test_macos_notification(),
        "Connectivity": test_webhook_connectivity(),
        "Notification Types": test_notification_types(),
        "Message Formatting": test_message_formatting(),
        "Error Formatting": test_error_formatting(),
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
        print("\n🎉 All Slack webhook tests passed!")
        print("Check your Slack channel for test messages.")
        print("\nExpected in Slack:")
        print("  • 6 test messages total")
        print("  • Rich formatting with blocks")
        print("  • Green color bars for success")
        print("  • Red color bar for error")
        print("  • Hostname and timestamp in footer")
        return 0
    else:
        print("\n❌ Some Slack webhook tests failed!")
        print("Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
