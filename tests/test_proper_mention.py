#!/usr/bin/env python3
"""
Test proper Discord user mention with User ID
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import urllib.request

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import homebrew_updater

USER_ID = "1055285176374145094"

def send_test_mention():
    """Send test message with proper user mention"""

    # Proper mention format: <@USER_ID>
    mention = f"<@{USER_ID}>"

    payload = {
        "content": f"{mention} 🔔 Homebrew notification test - you should get pinged!",
        "embeds": [{
            "title": "🧪 Mention Test",
            "description": f"{mention}\n\nThis message mentions you properly using your User ID.\n\n**Did you get a notification?**",
            "color": 0xFF6600,
            "timestamp": datetime.now().astimezone().isoformat(),
        }]
    }

    print(f"Sending test message with proper mention: {mention}")

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
                print("\n📱 CHECK YOUR DISCORD NOW!")
                print("\nYou should:")
                print("  • Get a notification/ping")
                print("  • See your username highlighted")
                print("  • Have a badge notification")
                print("\nIf this works, I'll update the updater to mention you!")
            else:
                print(f"⚠️  Status: {response.status}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    send_test_mention()
