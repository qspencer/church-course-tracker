# Sentry Error Fix - January 17, 2026

## Issue Summary

**Sentry Error**: "Object captured as exception with keys: error, headers, message, name, ok, status, statusText, url"

**Sentry Issue**: https://individual-r7.sentry.io/issues/7195326110/

## Problem Description

Sentry was reporting uninformative errors with the message "Object captured as exception with keys..." instead of showing meaningful error messages and stack traces. This made it difficult to understand what errors users were encountering in production.

### Root Cause

The Angular error interceptor (`error.interceptor.ts`) was throwing raw `HttpErrorResponse` objects instead of proper `Error` objects:

```typescript
// BEFORE (line 97)
return throwError(() => error);  // error is HttpErrorResponse
```

When Sentry captures a non-Error object, it serializes it as "Object captured as exception with keys: [list of properties]", which provides no useful debugging information.

### Stack Trace Analysis

The original Sentry stack trace showed:
```
Error: Object captured as exception with keys: error, headers, message, name, ok, status, statusText, url
    at Object.y (/main.751db71e4bc53123.js:1:1657683)
    at ne.error (/main.751db71e4bc53123.js:1:7350)
    at Object.error (/534.e5aa820c5df70edb.js:1:5732)
    ...
    at XMLHttpRequest.ii (/main.751db71e4bc53123.js:1:838959)
```

This indicated the error originated from an HTTP request and propagated through RxJS error handling.

## Solution

Modified the error interceptor to create proper `Error` objects with meaningful messages and context:

```typescript
// AFTER (lines 97-106)
// Create a proper Error object for better error tracking in Sentry
// Instead of throwing the raw HttpErrorResponse object
const httpError = new Error(errorMessage);
httpError.name = `HttpError_${error.status}`;
(httpError as any).status = error.status;
(httpError as any).statusText = error.statusText;
(httpError as any).url = error.url;
(httpError as any).error = error.error; // Preserve response body for component error handling
(httpError as any).originalError = error;

return throwError(() => httpError);
```

### Key Improvements

1. **Proper Error Object**: Creates a standard JavaScript `Error` with the extracted error message
2. **Meaningful Error Name**: Sets error name to `HttpError_404`, `HttpError_500`, etc. for easy identification
3. **Preserved Context**: Attaches HTTP context (status, statusText, url) as properties for debugging
4. **Backward Compatibility**: Preserves `error.error` property that components rely on for error handling
5. **Full Details Available**: Keeps `originalError` with complete `HttpErrorResponse` for advanced debugging

## Impact

### Before Fix
- Sentry showed: "Object captured as exception with keys: error, headers, message, name, ok, status, statusText, url"
- No meaningful error message
- Difficult to identify what went wrong
- Hard to group similar errors

### After Fix
- Sentry will show: Clear error messages like "Resource not found", "Unauthorized. Please log in again", etc.
- Error names like `HttpError_404`, `HttpError_500` for easy filtering
- Full context (URL, status code) attached for debugging
- Proper error grouping by message and type

## Testing

### Frontend Tests
- **Status**: All 829 tests passing ✅
- **Verification**: `npm test -- --watch=false --browsers=ChromeHeadless`
- **Result**: No regressions, all error handling tests pass

### Production Build
- **Status**: Build successful ✅
- **Command**: `npx ng build --configuration=production`
- **Result**: Main bundle: 1.70 MB, all chunks generated successfully

### Backward Compatibility
Verified that components can still access error properties:
- ✅ `error.status` - HTTP status code
- ✅ `error.error` - Response body
- ✅ `error.error.detail` - Detailed error message from API
- ✅ All existing error handling logic continues to work

## Files Modified

```
frontend/church-course-tracker/src/app/interceptors/error.interceptor.ts
  - Modified error throwing logic (lines 97-106)
  - Creates proper Error objects instead of throwing raw HttpErrorResponse
  - Preserves all necessary properties for component error handling
```

## Commit

**Commit Hash**: `8bd3d14`
**Commit Message**: `fix: improve Sentry error reporting for HTTP errors`

## Next Steps

### Monitor Sentry
1. Watch for new error reports to verify they now show meaningful messages
2. Check if error grouping improves (similar errors should be grouped together)
3. Verify error names appear as `HttpError_XXX` format

### Expected Sentry Reports
After this fix, Sentry should report errors like:
- `HttpError_404: Resource not found`
- `HttpError_500: Internal server error. Please try again later.`
- `HttpError_401: Unauthorized. Please log in again.`
- `HttpError_0: Unable to connect to the server. Please check your internet connection.`

### Follow-up Actions
- ✅ None required - fix is complete and tested
- Monitor Sentry for 1-2 weeks to confirm improvement
- Consider adding Sentry tags for better filtering (e.g., HTTP status, endpoint path)

## Additional Context

### Error Message Extraction Logic

The interceptor already extracts user-friendly error messages from API responses:

1. Checks `error.error.detail` (FastAPI standard)
2. Checks `error.error.message` (generic message field)
3. Checks `error.error.error` (nested error field)
4. Falls back to status-based messages (404 → "Resource not found", etc.)

These messages are now properly propagated to Sentry with full context.

### Sentry Configuration

Sentry is initialized in `main.ts` with:
- DSN: Configured per environment
- Environment: Production/Development tracking
- Trace sampling: Performance monitoring enabled
- beforeSend hook: Filters out Authorization headers

No changes were needed to Sentry configuration - the fix works with existing setup.

## Conclusion

This fix resolves the uninformative Sentry error reports by ensuring proper Error objects are thrown from the HTTP error interceptor. All tests pass, production build succeeds, and backward compatibility is maintained. Users will continue to see appropriate error messages in the UI, while developers will now get meaningful error reports in Sentry.

---

**Date**: January 17, 2026
**Engineer**: Claude Sonnet 4.5
**Status**: ✅ Complete and Deployed
