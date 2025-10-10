#!/usr/bin/env python3
"""
Test mentioning user in Discord notification
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.request

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater

# Test different mention formats
def send_test_mention():
    """Send test message with mention"""

    # Try mentioning by username
    payload = {
        "content": "@spicyeddie Test notification - can you see this?",
        "embeds": [{
            "title": "🧪 Mention Test",
            "description": "@spicyeddie\n\nTesting if mentioning your username triggers a notification.",
            "color": 0x0099FF,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }

    print("Sending test message with @spicyeddie mention...")

    try:
        req = urllib.request.Request(
            homebrew_updater.DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Homebrew-Updater/1.0 (Test)'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 204:
                print("✅ Message sent!")
                print("\nCheck Discord - did you get a notification with the mention?")
                print("\nNote: If @ mention doesn't ping you, I'll need your Discord User ID")
                print("(Right click your name → Copy User ID in Discord)")
            else:
                print(f"⚠️  Status: {response.status}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    send_test_mention()
