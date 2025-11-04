# Browser Cache Issue - Mixed Content Error

## Problem

Even after deploying new frontend builds with HTTPS API URLs, users are still seeing mixed content errors:
```
Mixed Content: The page at 'https://apps.quentinspencer.com/dashboard' was loaded 
over HTTPS, but requested an insecure XMLHttpRequest endpoint 
'http://api.quentinspencer.com/api/v1/courses/...'
```

## Root Cause

**Browser is using cached JavaScript files from the old build.**

### Why This Happens

1. **Angular's Content-Based Hashing**
   - Angular uses content-based hashing for chunk files
   - If component code hasn't changed, chunk hash stays the same
   - Example: `325.0c0d968fd1b204c1.js` (dashboard chunk)
   - Browser sees same filename and uses cached version

2. **Service Location**
   - Services (CourseService, EnrollmentService) are in the **main bundle**
   - Main bundle HAS been updated with HTTPS URL
   - But lazy-loaded chunks might be cached separately
   - Browser can mix old cached chunks with new main bundle

3. **Browser Cache Persistence**
   - Browsers cache JavaScript files aggressively
   - Cache can persist even after CloudFront cache clears
   - Hard refresh doesn't always clear all cached files

## Verification

### ✅ Build is Correct
- Main bundle (`main.*.js`) contains: `https://api.quentinspencer.com/api/v1`
- Source code has no HTTP URLs
- Environment.prod.ts is correctly configured
- File replacement is working

### ❌ Browser is Using Cached Files
- Browser console shows HTTP requests
- Error object shows HTTPS (after processing)
- Same chunk hash means browser thinks it's the same file

## Solution

### For Users

**Complete Browser Cache Clear Required:**

1. **Chrome/Edge:**
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Time range: "All time"
   - Click "Clear data"
   - Close and reopen browser

2. **Firefox:**
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cache"
   - Time range: "Everything"
   - Click "Clear Now"

3. **Safari:**
   - Safari > Preferences > Advanced
   - Check "Show Develop menu in menu bar"
   - Develop > Empty Caches
   - Or: `Cmd+Option+E`

4. **Alternative: Incognito/Private Window**
   - Open new incognito/private window
   - Test application there
   - This bypasses all cache

### For Developers

**Prevent Future Cache Issues:**

1. **Force Cache Invalidation After Deployment**
   ```bash
   # Always invalidate CloudFront after deployment
   aws cloudfront create-invalidation \
     --distribution-id <DIST_ID> \
     --paths "/*"
   ```

2. **Use Version Query Parameters (Future Enhancement)**
   ```html
   <!-- Add version to index.html -->
   <script src="main.js?v=1.0.1"></script>
   ```

3. **Update Angular Output Hashing**
   - Already configured: `"outputHashing": "all"`
   - This ensures all files get new hashes when content changes

4. **Consider Service Worker**
   - If using service worker, ensure it's updating correctly
   - Clear service worker cache if needed

## Technical Details

### File Structure
- **Main Bundle**: `main.*.js` - Contains services, environment, core app
- **Lazy Chunks**: `325.*.js`, `593.*.js`, etc. - Component-specific code
- **Common Chunk**: `common.*.js` - Shared code

### Environment Injection
- Environment variables are **baked into bundles at build time**
- Services read `environment.apiUrl` which is replaced during build
- Main bundle has correct HTTPS URL
- Lazy chunks don't contain environment (services are in main bundle)

### Why Chunk Hash Stays Same
- Angular uses content-based hashing
- If dashboard component code hasn't changed, hash is same
- Environment changes don't affect component code hash
- Only service code (in main bundle) gets new hash

## Prevention

### Best Practices

1. **Always Clear Dist Before Build**
   ```bash
   rm -rf dist
   npm run build -- --configuration=production
   ```

2. **Invalidate CloudFront After Every Deployment**
   ```bash
   aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"
   ```

3. **Document Cache Clear Instructions**
   - Provide clear instructions for users
   - Include in deployment notes

4. **Monitor Deployment**
   - Check browser console after deployment
   - Verify HTTPS requests in Network tab
   - Test in incognito mode first

## Current Status

- ✅ Build is correct (HTTPS in main bundle)
- ✅ Deployed to S3
- ✅ CloudFront cache invalidated
- ⚠️ Users need to clear browser cache
- ⚠️ Some browsers may need complete cache clear

## Next Steps

1. **Immediate**: Users must clear browser cache
2. **Short-term**: Document cache clear instructions
3. **Long-term**: Consider adding version query parameters or service worker


