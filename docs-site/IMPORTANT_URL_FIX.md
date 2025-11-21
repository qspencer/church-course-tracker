# ⚠️ IMPORTANT: Correct URL for Local Development

## The Problem

Your browser is trying to access:
```
http://127.0.0.1:8000/churchcoursetracker/getting-started/
```

**This URL is WRONG for local development!**

## The Correct URL

For local development, use:
```
http://127.0.0.1:8000/getting-started/
```

**Notice: NO `/churchcoursetracker/` prefix!**

## Why This Happens

The `/churchcoursetracker/` path prefix is only used in **production** at `https://docs.quentinspencer.com/churchcoursetracker/`.

For **local development**, the site is served directly from the root:
- ✅ `http://127.0.0.1:8000/` (correct)
- ✅ `http://127.0.0.1:8000/getting-started/` (correct)
- ❌ `http://127.0.0.1:8000/churchcoursetracker/getting-started/` (WRONG - doesn't exist locally)

## How to Fix

### Option 1: Type the Correct URL
Simply navigate to:
```
http://127.0.0.1:8000/getting-started/
```

### Option 2: Clear Browser History
1. Open a new tab
2. Type `http://127.0.0.1:8000/` (just the root)
3. Navigate from there using the site's navigation menu

### Option 3: Use Incognito/Private Mode
Open a new incognito/private window and navigate to:
```
http://127.0.0.1:8000/
```

This bypasses all cached URLs and bookmarks.

## All Correct Local URLs

- Home: `http://127.0.0.1:8000/`
- Getting Started: `http://127.0.0.1:8000/getting-started/`
- User Guide: `http://127.0.0.1:8000/user-guide/`
- Features: `http://127.0.0.1:8000/features/`
- Documentation Guide: `http://127.0.0.1:8000/DOCUMENTATION_GUIDE/`

## Production URLs (for reference)

- Home: `https://docs.quentinspencer.com/churchcoursetracker/`
- Getting Started: `https://docs.quentinspencer.com/churchcoursetracker/getting-started/`
- etc.

**Remember: Local development = NO `/churchcoursetracker/` prefix!**

