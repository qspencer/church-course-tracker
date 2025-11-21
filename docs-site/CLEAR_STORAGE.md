# Clear Browser Storage to Fix Path Issues

The error `GET http://127.0.0.1:8000/churchcoursetracker/getting-started/ 404` is caused by cached data in your browser's localStorage.

## Quick Fix: Clear localStorage

### Option 1: Using Browser Console (Recommended)

1. Open Developer Tools (F12)
2. Go to the **Console** tab
3. Type this command and press Enter:
   ```javascript
   localStorage.clear(); location.reload();
   ```

### Option 2: Using Application/Storage Tab

**Chrome/Edge:**
1. Open Developer Tools (F12)
2. Go to **Application** tab
3. Click **Local Storage** in the left sidebar
4. Click on `http://127.0.0.1:8000`
5. Right-click and select **Clear**
6. Refresh the page

**Firefox:**
1. Open Developer Tools (F12)
2. Go to **Storage** tab
3. Expand **Local Storage**
4. Click on `http://127.0.0.1:8000`
5. Right-click and select **Delete All**
6. Refresh the page

### Option 3: Clear All Site Data

1. Open Developer Tools (F12)
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Click **Clear site data** or **Clear storage**
4. Make sure all checkboxes are selected
5. Click **Clear data**
6. Refresh the page

### Option 4: Use Incognito/Private Window

Open a new incognito/private window - this will have no cached data:
- **Chrome/Edge**: `Ctrl+Shift+N` (Windows) or `Cmd+Shift+N` (Mac)
- **Firefox**: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
- **Safari**: `Cmd+Shift+N`

Then navigate to `http://127.0.0.1:8000`

## Why This Happens

MkDocs Material theme stores configuration in localStorage using the page path as part of the key. If you previously visited the site with the `/churchcoursetracker/` path prefix, that data is still stored and the JavaScript is trying to use it.

After clearing localStorage, the site should work correctly!

