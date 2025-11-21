# Fixing Browser Cache Issues

If you're seeing errors like:
- `GET http://127.0.0.1:8000/churchcoursetracker/getting-started/ 404 (Not Found)`
- Links trying to use `/churchcoursetracker/` path prefix

This is because your browser has cached the old HTML with the production URL structure.

## Solution: Clear Browser Cache

### Option 1: Hard Refresh (Recommended)
- **Chrome/Edge (Windows/Linux)**: `Ctrl + Shift + R` or `Ctrl + F5`
- **Chrome/Edge (Mac)**: `Cmd + Shift + R`
- **Firefox (Windows/Linux)**: `Ctrl + Shift + R` or `Ctrl + F5`
- **Firefox (Mac)**: `Cmd + Shift + R`
- **Safari (Mac)**: `Cmd + Option + R`

### Option 2: Clear Cache Completely
1. Open Developer Tools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Clear Site Data
1. Open Developer Tools (F12)
2. Go to Application tab (Chrome) or Storage tab (Firefox)
3. Click "Clear site data" or "Clear storage"
4. Refresh the page

### Option 4: Use Incognito/Private Mode
- Open a new incognito/private window
- Navigate to `http://127.0.0.1:8000`
- This will bypass all cache

## What Was Fixed

1. **OG URL Meta Tag**: Now uses dynamic `site_url` from config instead of hardcoded production URL
2. **GitHub API Calls**: Disabled version selector to prevent GitHub API 404 errors
3. **Dev Configuration**: Created `mkdocs.dev.yml` for local development without path prefix

After clearing cache, the site should work correctly!

