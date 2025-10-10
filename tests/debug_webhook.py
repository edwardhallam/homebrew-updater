#!/usr/bin/env python3
"""
Debug Discord webhook 403 error
Test different payload formats and configurations
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

WEBHOOK_URL = "https://discord.com/api/webhooks/1426005567666917427/V2IBIHkXf5hTprsOLEBW02HC5ZD4yZlz-_pm-vSF17Gm2GE_uR2Cz56weOjvEe0I0y1n"

def test_simple_message():
    """Test 1: Simplest possible message"""
    print("\n" + "="*60)
    print("Test 1: Simple message (no embeds)")
    print("="*60)

    payload = {"content": "Test message"}

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_simple_message_with_user_agent():
    """Test 2: Simple message with User-Agent header"""
    print("\n" + "="*60)
    print("Test 2: Simple message + User-Agent")
    print("="*60)

    payload = {"content": "Test with User-Agent"}

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_embed_no_timestamp():
    """Test 3: Embed without timestamp"""
    print("\n" + "="*60)
    print("Test 3: Embed without timestamp")
    print("="*60)

    payload = {
        "embeds": [{
            "title": "Test Title",
            "description": "Test Description",
            "color": 0x00FF00
        }]
    }

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_embed_with_utc_timestamp():
    """Test 4: Embed with UTC timezone-aware timestamp"""
    print("\n" + "="*60)
    print("Test 4: Embed with UTC timezone-aware timestamp")
    print("="*60)

    payload = {
        "embeds": [{
            "title": "Test Title",
            "description": "Test Description",
            "color": 0x00FF00,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_embed_with_utcnow_timestamp():
    """Test 5: Embed with utcnow() timestamp (original format)"""
    print("\n" + "="*60)
    print("Test 5: Embed with utcnow() timestamp (original)")
    print("="*60)

    payload = {
        "embeds": [{
            "title": "Test Title",
            "description": "Test Description",
            "color": 0x00FF00,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_full_payload_original():
    """Test 6: Full payload as in original code"""
    print("\n" + "="*60)
    print("Test 6: Full payload (original format)")
    print("="*60)

    import os

    payload = {
        "embeds": [{
            "title": "Homebrew Updater",
            "description": "Test message",
            "color": 0x00FF00,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": os.uname().nodename}
        }]
    }

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ SUCCESS: Status {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED: HTTP {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8', errors='ignore')}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_curl_equivalent():
    """Test 7: Using curl command (subprocess)"""
    print("\n" + "="*60)
    print("Test 7: Using curl command")
    print("="*60)

    import subprocess

    payload = {"content": "Test via curl"}

    try:
        result = subprocess.run([
            'curl', '-X', 'POST',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps(payload),
            WEBHOOK_URL
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print(f"✅ SUCCESS: curl returned 0")
            print(f"   Output: {result.stdout}")
            return True
        else:
            print(f"❌ FAILED: curl returned {result.returncode}")
            print(f"   stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_webhook_url_format():
    """Test 8: Verify webhook URL format"""
    print("\n" + "="*60)
    print("Test 8: Webhook URL validation")
    print("="*60)

    import re

    # Discord webhook URL pattern
    pattern = r'^https://discord\.com/api/webhooks/\d+/[\w-]+$'

    if re.match(pattern, WEBHOOK_URL):
        print(f"✅ URL format is valid")
        print(f"   URL: {WEBHOOK_URL[:50]}...")
        return True
    else:
        print(f"❌ URL format is INVALID")
        print(f"   Expected: https://discord.com/api/webhooks/ID/TOKEN")
        print(f"   Got: {WEBHOOK_URL[:50]}...")
        return False


def main():
    """Run all diagnostic tests"""
    print("="*60)
    print("Discord Webhook Diagnostic Tool")
    print("="*60)
    print(f"Testing webhook: {WEBHOOK_URL[:50]}...")
    print("")

    tests = [
        ("URL Format Validation", test_webhook_url_format),
        ("Simple Message", test_simple_message),
        ("With User-Agent", test_simple_message_with_user_agent),
        ("Embed No Timestamp", test_embed_no_timestamp),
        ("Embed UTC Timestamp", test_embed_with_utc_timestamp),
        ("Embed utcnow Timestamp", test_embed_with_utcnow_timestamp),
        ("Full Original Payload", test_full_payload_original),
        ("Curl Command", test_curl_equivalent),
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
    print("DIAGNOSTIC SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:30s} {status}")

    print("="*60)

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if passed_count == 0:
        print("\n⚠️  All tests failed! Webhook URL may be invalid or revoked.")
    elif passed_count < total_count:
        print("\n⚠️  Some tests passed. Issue may be with specific payload format.")
    else:
        print("\n✅ All tests passed! Webhook is working correctly.")

    return 0 if passed_count > 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
