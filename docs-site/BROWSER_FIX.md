# Fixing Browser Cache Issues

If you're seeing errors like `GET http://127.0.0.1:8000/churchcoursetracker/getting-started/ 404 (Not Found)` even after clearing cache, try these steps:

## 1. Unregister Service Workers

The browser might have a service worker registered that's intercepting requests:

1. Open Developer Tools (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click **Service Workers** in the left sidebar
4. If any service workers are listed, click **Unregister**
5. Refresh the page

## 2. Clear All Site Data

1. Open Developer Tools (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click **Clear storage** or **Clear site data**
4. Check **ALL** boxes:
   - Local storage
   - Session storage
   - IndexedDB
   - Service Workers
   - Cache storage
   - Cookies
5. Click **Clear data**
6. Close and reopen the browser tab

## 3. Disable Browser Prefetching

Some browsers prefetch pages, which can cause issues:

**Chrome:**
1. Go to `chrome://settings/privacy`
2. Disable "Preload pages for faster browsing and searching"
3. Restart Chrome

**Firefox:**
1. Go to `about:config`
2. Search for `network.prefetch-next`
3. Set it to `false`

## 4. Use Incognito/Private Mode

Open a new incognito/private window - this bypasses all cache and service workers:
- **Chrome/Edge**: `Ctrl+Shift+N` (Windows) or `Cmd+Shift+N` (Mac)
- **Firefox**: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)

## 5. Check Network Tab

1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Check "Disable cache"
4. Reload the page
5. Look at the failed request - check the **Initiator** column to see what's causing it

## 6. Hard Reset Browser

If nothing else works:

1. Close all browser windows
2. Clear browser cache completely (via browser settings)
3. Restart the browser
4. Open a new tab and navigate to `http://127.0.0.1:8000`

## What's Happening?

The error `GET http://127.0.0.1:8000/churchcoursetracker/getting-started/ 404` means something in your browser is trying to load that URL. This could be:

- A cached service worker
- Browser prefetch/preload
- Cached HTML with old URLs
- JavaScript constructing URLs incorrectly (though we've verified the server HTML is correct)

The server is serving the correct content - the issue is in the browser's cache or prefetching behavior.

