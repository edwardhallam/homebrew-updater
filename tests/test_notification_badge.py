#!/usr/bin/env python3
"""
Test Discord badge notifications
Tests different message formats to determine which trigger badge notifications
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
import os
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater

WEBHOOK_URL = homebrew_updater.DISCORD_WEBHOOK_URL


def send_raw_webhook(payload_name: str, payload: dict, pause: int = 3) -> bool:
    """Send raw payload to webhook and return success status"""
    print(f"\n{'='*60}")
    print(f"Test: {payload_name}")
    print(f"{'='*60}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))
    print(f"{'='*60}")

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0 (Test)'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                print(f"✅ Sent successfully")
                print(f"⏳ Pausing {pause} seconds...")
                time.sleep(pause)
                return True
            else:
                print(f"⚠️  Status: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_embed_only():
    """Test 1: Embed only (current behavior - may not trigger notification)"""
    payload = {
        "embeds": [{
            "title": "Test 1: Embed Only",
            "description": "This message has ONLY an embed, no content field.",
            "color": 0x0099FF,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }
    return send_raw_webhook("Embed Only (No Badge Expected)", payload)


def test_content_only():
    """Test 2: Content only (should trigger notification)"""
    payload = {
        "content": "🔔 Test 2: Content Only - This should trigger a badge notification!"
    }
    return send_raw_webhook("Content Only (Badge Expected)", payload)


def test_content_and_embed():
    """Test 3: Content + Embed (recommended - should trigger notification)"""
    payload = {
        "content": "🔔 Test 3: Content + Embed - Badge notification expected!",
        "embeds": [{
            "title": "Test 3: Content + Embed",
            "description": "This message has BOTH content and embed.\n\nThe content triggers the notification, the embed provides rich formatting.",
            "color": 0x00FF00,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }
    return send_raw_webhook("Content + Embed (Badge Expected)", payload)


def test_realistic_update():
    """Test 4: Realistic update notification with new format"""
    payload = {
        "content": "✅ **Homebrew Update Complete!**",
        "embeds": [{
            "title": "Homebrew Updater",
            "description": "✅ **Homebrew Update Complete!**\n\n📦 **Formulae Upgraded (3):**\n  • python@3.12\n  • git\n  • wget\n\n🍺 **Casks:** None to upgrade\n\n🧹 **Cleanup:** Complete",
            "color": 0x00FF00,
            "timestamp": datetime.now().astimezone().isoformat(),
            "footer": {"text": os.uname().nodename}
        }]
    }
    return send_raw_webhook("Realistic Update (Badge Expected)", payload)


def test_with_username_avatar():
    """Test 5: Content + Embed + Username/Avatar (may improve notification)"""
    payload = {
        "content": "🍺 Test 5: With username/avatar",
        "username": "Homebrew Updater",
        "avatar_url": "https://brew.sh/assets/img/homebrew-256x256.png",
        "embeds": [{
            "title": "Enhanced Notification",
            "description": "This message includes username and avatar_url for better visibility.",
            "color": 0xFFA500,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }
    return send_raw_webhook("With Username/Avatar (Badge Expected)", payload)


def test_priority_message():
    """Test 6: High-priority error message"""
    payload = {
        "content": "❌ URGENT: Homebrew update FAILED!",
        "embeds": [{
            "title": "⚠️ Error - Homebrew Updater",
            "description": "❌ **Homebrew update failed**\n\nError: Test error message\n\nPlease check the logs.",
            "color": 0xFF0000,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }
    return send_raw_webhook("Error Message (Badge Expected)", payload)


def main():
    """Run all notification badge tests"""
    print("="*60)
    print("Discord Badge Notification Test Suite")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Webhook: {WEBHOOK_URL[:50]}...")
    print("="*60)
    print()
    print("INSTRUCTIONS:")
    print("1. Watch your Discord app/phone for badge notifications")
    print("2. Note which tests trigger the red badge number")
    print("3. Tests are sent 3 seconds apart")
    print()
    input("Press ENTER to start testing...")

    tests = [
        ("Embed Only", test_embed_only),
        ("Content Only", test_content_only),
        ("Content + Embed", test_content_and_embed),
        ("Realistic Update", test_realistic_update),
        ("With Username/Avatar", test_with_username_avatar),
        ("Error Message", test_priority_message),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, success in results.items():
        status = "✅ SENT" if success else "❌ FAILED"
        print(f"{test_name:30s} {status}")

    print("="*60)
    print()
    print("📱 NOW CHECK YOUR DISCORD:")
    print()
    print("Expected badge notifications:")
    print("  ❌ Test 1 (Embed Only) - NO badge expected")
    print("  ✅ Test 2 (Content Only) - BADGE expected")
    print("  ✅ Test 3 (Content + Embed) - BADGE expected")
    print("  ✅ Test 4 (Realistic Update) - BADGE expected")
    print("  ✅ Test 5 (Username/Avatar) - BADGE expected")
    print("  ✅ Test 6 (Error Message) - BADGE expected")
    print()
    print("If badges appeared for tests 2-6, the fix is working!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
