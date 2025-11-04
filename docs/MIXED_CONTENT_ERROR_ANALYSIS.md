# Mixed Content Error Analysis

## Console Error Details

```
Mixed Content: The page at 'https://apps.quentinspencer.com/dashboard' was loaded 
over HTTPS, but requested an insecure XMLHttpRequest endpoint 
'http://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses/?limit=5&sort=created_at&order=desc'. 
This request has been blocked; the content must be served over HTTPS.
```

## Problem Summary

### What's Happening
- **Frontend**: Running over HTTPS (`https://apps.quentinspencer.com`)
- **API Requests**: Attempting to use HTTP (`http://tinev5iszf.execute-api.us-east-1.amazonaws.com`)
- **Browser Action**: **BLOCKING all requests** due to mixed content security policy

### Root Cause
The deployed frontend build is using an **old configuration** that was created before we updated `environment.prod.ts` to use the HTTPS custom domain.

### Current Configuration Status

✅ **`environment.prod.ts`** (Source Code):
```typescript
apiUrl: 'https://api.quentinspencer.com/api/v1'  // ✅ CORRECT
```

❌ **Deployed Build** (Currently Live):
```
apiUrl: 'http://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1'  // ❌ OLD/INCORRECT
```

## Impact

### Critical Issues
1. **All API requests are blocked** - Browser security policy prevents HTTP requests from HTTPS pages
2. **Application appears broken** - Users see errors instead of data
3. **Dashboard cannot load** - Courses, enrollments, and other data fail to load
4. **User experience degraded** - Application is non-functional

### Affected Endpoints
- `/api/v1/courses/` - Course listings
- `/api/v1/enrollments/` - Enrollment data
- All other API endpoints

## Solution

### Required Actions

1. **Rebuild Frontend** (Production Configuration)
   ```bash
   cd frontend/church-course-tracker
   npm run build -- --configuration=production
   ```

2. **Redeploy to S3**
   - Upload new build to S3 bucket
   - Ensure CloudFront is configured to serve from S3

3. **Invalidate CloudFront Cache**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <DISTRIBUTION_ID> \
     --paths "/*"
   ```

4. **Verify Deployment**
   - Check browser console - should see HTTPS requests
   - Verify API calls go to `https://api.quentinspencer.com`
   - Test all major features

## Verification Steps

After redeployment:

1. **Check Browser Console**
   - Should see: `https://api.quentinspencer.com/api/v1/...`
   - Should NOT see: `http://tinev5iszf.execute-api...`

2. **Test API Calls**
   - Dashboard loads courses ✅
   - Dashboard loads enrollments ✅
   - No mixed content errors ✅

3. **Network Tab**
   - All requests should be HTTPS
   - All requests should go to `api.quentinspencer.com`

## Prevention

### Best Practices
1. **Always rebuild after environment changes** - Environment files are baked into build
2. **Use CI/CD pipeline** - Automate builds and deployments
3. **Version control deployments** - Track which build is deployed
4. **Cache invalidation** - Always invalidate CDN cache after deployment

### Configuration Management
- Environment files are **compile-time** replacements
- Changes to `environment.prod.ts` require a **new build**
- Old builds continue to use old configuration until replaced

## Current Status

- ❌ **Deployed frontend**: Using old HTTP configuration
- ✅ **Source code**: Correct HTTPS configuration
- ⚠️ **Action required**: Rebuild and redeploy frontend

## Next Steps

1. Identify deployment process (CI/CD or manual)
2. Rebuild frontend with production configuration
3. Deploy new build to S3
4. Invalidate CloudFront cache
5. Verify fix in browser


