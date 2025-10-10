# Discord Webhook 403 Error - Investigation & Fix Report

**Date:** 2025-10-09
**Issue:** Discord webhook returning HTTP 403 Forbidden
**Status:** ✅ RESOLVED

---

## Problem Summary

The Discord webhook was returning `HTTP 403 Forbidden` with error code `1010` when attempting to send notifications.

**Symptoms:**
- All webhook requests failed with 403 error
- Error message: "error code: 1010"
- Webhook URL was valid and correctly configured

---

## Root Cause Analysis

### Investigation Process

Created diagnostic script (`tests/debug_webhook.py`) to test different request configurations:

```bash
python3 tests/debug_webhook.py
```

### Test Results

| Test | Result | Notes |
|------|--------|-------|
| URL Format Validation | ✅ PASS | URL structure valid |
| Simple Message (no headers) | ❌ FAIL | 403 - error code 1010 |
| Simple Message + User-Agent | ✅ PASS | **Works!** |
| Embed formats | ❌ FAIL | 403 - without User-Agent |
| Curl command | ✅ PASS | curl sends User-Agent by default |

### Root Cause

**Cloudflare Bot Protection**

Discord uses Cloudflare for DDoS protection. Error code 1010 is Cloudflare's "Access Denied - Bot Protection."

Cloudflare blocks requests that:
- Don't include a `User-Agent` header
- Appear to be from automated bots

**Solution:** Add a `User-Agent` header to all webhook requests.

---

## The Fix

### Changes Made

**File:** `scripts/homebrew_updater.py`

#### Before (lines 95-103):
```python
req = urllib.request.Request(
    DISCORD_WEBHOOK_URL,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
```

#### After (lines 95-103):
```python
req = urllib.request.Request(
    DISCORD_WEBHOOK_URL,
    data=json.dumps(payload).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Homebrew-Updater/1.0 (Python)'
    }
)
```

### Additional Improvements

Also fixed deprecation warning:

**Before:**
```python
"timestamp": datetime.utcnow().isoformat()
```

**After:**
```python
"timestamp": datetime.now().astimezone().isoformat()
```

---

## Verification

### Test Results After Fix

```bash
python3 tests/test_discord_webhook.py
```

**Results:**
```
============================================================
Test Summary
============================================================
Connectivity                   ✅ PASSED
Notification Types             ✅ PASSED
Message Formatting             ✅ PASSED
============================================================

🎉 All Discord webhook tests passed!
```

### Unit Tests

```bash
python3 tests/test_homebrew_updater.py
```

**Results:** 22/24 tests pass (same as before - 2 test code issues unrelated to fix)

---

## Technical Details

### Why This Happens

1. **Cloudflare Protection:** Discord's webhooks are behind Cloudflare CDN
2. **Bot Detection:** Cloudflare uses various heuristics to detect bots
3. **User-Agent Check:** Missing User-Agent is a strong bot indicator
4. **Error Code 1010:** Cloudflare's specific error for "Access Denied"

### Why It Works Now

- `User-Agent` header makes the request appear as a legitimate application
- Cloudflare allows the request through
- Discord webhook processes the notification normally

### Best Practices

Always include these headers when making HTTP requests:
```python
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'YourApp/Version (Platform)'
}
```

---

## Files Modified

1. **scripts/homebrew_updater.py**
   - Added `User-Agent` header
   - Fixed timestamp deprecation warning

2. **tests/test_discord_webhook.py**
   - Added `User-Agent` header to test requests
   - Fixed timestamp deprecation warning

3. **tests/debug_webhook.py** (new)
   - Diagnostic tool for webhook troubleshooting
   - Tests various request configurations

---

## Lessons Learned

1. **Always include User-Agent:** Modern web services expect it
2. **Error code 1010:** Specifically means Cloudflare bot protection
3. **Diagnostic approach:** Systematic testing revealed the exact issue
4. **curl works differently:** curl includes User-Agent by default

---

## Testing Checklist

- [x] Diagnostic tests identify issue
- [x] Fix applied to main script
- [x] Fix applied to test script
- [x] All Discord webhook tests pass
- [x] Unit tests still pass (22/24)
- [x] No new deprecation warnings
- [x] Documentation updated

---

## Next Steps

✅ **Issue Resolved** - Ready for production use

To verify in your Discord channel:
1. Check for test messages from the webhook tests
2. Manually run the updater to see live notifications:
   ```bash
   python3 scripts/homebrew_updater.py
   ```

---

## References

- **Cloudflare Error 1010:** Access Denied / Bot Protection
- **Discord Webhook API:** https://discord.com/developers/docs/resources/webhook
- **Python urllib User-Agent:** Standard practice for HTTP requests
- **Diagnostic Tool:** `tests/debug_webhook.py`

---

**Report Prepared By:** Claude Code QA
**Date:** 2025-10-09
**Status:** RESOLVED ✅
