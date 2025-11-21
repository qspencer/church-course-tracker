# Fix Plan for 4 Remaining Test Failures

## Summary
**4 tests still failing** in `tests/e2e/role-based-access.spec.ts`

## Failure Analysis

### 1. "Admin can access all system features" (Line 28)
**Error:** `strict mode violation: locator('text=Courses') resolved to 5 elements`

**Root Cause:** The selector `text=Courses` matches multiple elements on the dashboard:
1. Navigation link "Courses"
2. "Total Courses" text
3. "Recent Courses" heading
4. "No recent courses" text
5. "View All Courses" button

**Fix Required:**
- Use a more specific selector for navigation items
- Use `getByRole('link', { name: 'Courses' })` or `page.locator('a[routerLink*="courses"]')` or add `.first()` and filter by navigation context
- Better: Use `page.locator('mat-nav-list a:has-text("Courses")')` to target only navigation links

**Code Change:**
```typescript
// Change from:
await expect(page.locator(`text=${item}`)).toBeVisible();

// To:
const navLink = page.locator(`mat-nav-list a:has-text("${item}"), a[routerLink]:has-text("${item}")`).first();
await expect(navLink).toBeVisible();
```

---

### 2. "Users cannot access other roles features" (Line 415)
**Error:** `expect(locator).toBeVisible() failed - Locator: locator('input[formControlName="username"]') - Timeout: 10000ms`

**Root Cause:** After logging in as staff and being redirected to dashboard, when the test tries to login as viewer using `loginAs()`, the page might not be on the auth page yet. The test navigates to auth, but `loginAsRole()` is called immediately and expects the username input to be visible.

**Fix Required:**
- Ensure the page is fully on the auth page before calling `loginAs()`
- Add explicit wait for auth page to load
- Or use explicit login flow instead of `loginAs()` helper

**Code Change:**
```typescript
// After navigating to auth, wait for page to be ready
await page.goto(`${APP_BASE_URL}/auth`, { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);
await page.waitForSelector('input[formControlName="username"]', { timeout: 10000 });

// Then call loginAs
if (!(await loginAs(page, 'viewer', testInfo))) {
  return;
}
```

---

### 3. "API endpoints respect role permissions" (Line 439)
**Error:** `Test timeout of 30000ms exceeded - locator.fill: Test timeout of 30000ms exceeded - waiting for locator('input[formControlName="username"]').first()`

**Root Cause:** Similar to #2. After logging in as admin and making API calls, when trying to login as staff/viewer, the page navigation to auth might not be complete, or the form isn't ready yet. The test tries to fill the username input but it's not visible.

**Fix Required:**
- Add explicit wait for auth page to be fully loaded before attempting to fill form
- Ensure form fields are visible before interacting
- Add error handling for navigation failures

**Code Change:**
```typescript
// After navigating to auth for staff login
await page.goto(`${APP_BASE_URL}/auth`, { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);

// Wait for form to be ready
await page.waitForSelector('input[formControlName="username"]', { timeout: 10000 });
await page.waitForSelector('input[formControlName="password"]', { timeout: 10000 });

const staffUsernameInput = page.locator('input[formControlName="username"]').first();
const staffPasswordInput = page.locator('input[formControlName="password"]').first();

// Verify they're visible before filling
await expect(staffUsernameInput).toBeVisible({ timeout: 5000 });
await expect(staffPasswordInput).toBeVisible({ timeout: 5000 });

// Then fill
await staffUsernameInput.fill(staffCreds.username);
await staffPasswordInput.fill(staffCreds.password);
```

**Same fix needed for viewer login section.**

---

### 4. "Admin course management workflow" (Line 545)
**Error:** `expect(courseVisible).toBeFalsy() - Received: true`

**Root Cause:** The course "Test Admin Course" is still visible in the table after deletion. Possible causes:
- Deletion didn't actually complete (API call failed silently)
- Table isn't refreshing after deletion
- Multiple courses with same name exist
- Course name appears in success message and test is checking wrong location
- Timing issue - deletion is async and test checks too early

**Fix Required:**
- Wait for table to refresh after deletion
- Check if deletion API call succeeded
- Use more specific selector to check only table rows (not success messages)
- Add retry logic or longer wait
- Check if course actually exists before trying to delete
- Use unique course name to avoid conflicts

**Code Change:**
```typescript
// Use unique course name with timestamp
const uniqueCourseName = `Test Admin Course ${Date.now()}`;
await titleInput.fill(uniqueCourseName);

// ... after deletion ...

// Wait for deletion to complete and table to refresh
await page.waitForTimeout(3000);
await page.waitForLoadState('networkidle');

// Reload the page to ensure fresh data
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(2000);

// Check specifically in table rows only
const courseInTable = page.locator('table tr[mat-row]').filter({ hasText: uniqueCourseName }).first();
const courseInTableVisible = await courseInTable.isVisible({ timeout: 5000 }).catch(() => false);

// Also check if there's a success message that might contain the name
const successMsg = page.locator('.mat-snack-bar-container, .snackbar').first();
const successVisible = await successMsg.isVisible({ timeout: 2000 }).catch(() => false);

if (successVisible) {
  // Wait for snackbar to disappear
  await page.waitForTimeout(3000);
}

// Final check - course should not be in table
expect(courseInTableVisible).toBeFalsy();
```

---

## Implementation Priority

1. **High Priority (Quick Fixes):**
   - Fix #1: Admin navigation selector (5 minutes)
   - Fix #2: Add wait for auth page in cross-role test (5 minutes)

2. **Medium Priority:**
   - Fix #3: Add explicit waits in API test (10 minutes)
   - Fix #4: Improve course deletion verification (15 minutes)

## Expected Outcome

After these fixes:
- All 4 tests should pass
- Tests will be more robust with better selectors and timing
- Tests will handle async operations more reliably

## Testing Strategy

1. Run each test individually to verify fix
2. Run all tests in the file to ensure no regressions
3. Check for any new failures introduced by the fixes

