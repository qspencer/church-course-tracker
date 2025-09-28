# End-to-End Testing with Playwright

This directory contains comprehensive end-to-end tests for the Church Course Tracker application using Playwright.

## Test Structure

### Test Files

- **`auth.spec.ts`** - Authentication tests (login, logout, error handling)
- **`navigation.spec.ts`** - Navigation and routing tests
- **`courses.spec.ts`** - Course management functionality tests
- **`api.spec.ts`** - API integration and backend tests
- **`performance.spec.ts`** - Performance and load testing

### Test Categories

#### 1. Authentication Tests (`auth.spec.ts`)
- ✅ Login form display
- ✅ Invalid credentials handling
- ✅ Valid login flow
- ✅ Auto-redirect for authenticated users
- ✅ Logout functionality

#### 2. Navigation Tests (`navigation.spec.ts`)
- ✅ Dashboard navigation
- ✅ Courses page navigation
- ✅ Members page navigation
- ✅ Users page navigation (admin only)
- ✅ Reports page navigation
- ✅ Mobile responsive navigation

#### 3. Course Management Tests (`courses.spec.ts`)
- ✅ Courses page display
- ✅ Add course dialog
- ✅ Create new course
- ✅ Edit existing course
- ✅ Delete course
- ✅ Search functionality

#### 4. API Integration Tests (`api.spec.ts`)
- ✅ Health endpoint
- ✅ Authentication API
- ✅ Courses API
- ✅ Members API
- ✅ Users API (admin only)
- ✅ Error handling
- ✅ CORS configuration

#### 5. Performance Tests (`performance.spec.ts`)
- ✅ Page load times
- ✅ Large dataset handling
- ✅ Core Web Vitals
- ✅ Concurrent user sessions
- ✅ Network interruption handling

## Running Tests

### Prerequisites

1. Install Node.js (version 18 or higher)
2. Install dependencies: `npm install`
3. Install Playwright browsers: `npx playwright install`

### Test Commands

```bash
# Run all tests
npm test

# Run tests in headed mode (visible browser)
npm run test:headed

# Run tests with UI mode (interactive)
npm run test:ui

# Run tests in debug mode
npm run test:debug

# Run specific test suites
npm run test:auth
npm run test:navigation
npm run test:courses
npm run test:api
npm run test:performance

# View test report
npm run test:report
```

### Test Configuration

The tests are configured in `playwright.config.ts` with the following settings:

- **Base URL**: `https://apps.quentinspencer.com`
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile Testing**: Pixel 5, iPhone 12
- **Retries**: 2 retries on CI, 0 locally
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

## Test Data

### Default Test Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Test Environment
- **Frontend**: https://apps.quentinspencer.com
- **Backend API**: https://api.quentinspencer.com

## Writing New Tests

### Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup code
  });

  test('should do something', async ({ page }) => {
    // Test implementation
  });
});
```

### Best Practices

1. **Use descriptive test names** that explain what the test does
2. **Group related tests** using `test.describe()`
3. **Use `beforeEach`** for common setup
4. **Wait for elements** using `expect().toBeVisible()`
5. **Use data-testid attributes** for reliable element selection
6. **Handle async operations** properly
7. **Clean up after tests** if needed

### Element Selection

```typescript
// Good: Specific and reliable
await page.locator('[data-testid="submit-button"]').click();

// Good: Text-based selection
await page.locator('text=Submit').click();

// Good: Role-based selection
await page.locator('button:has-text("Submit")').click();

// Avoid: Fragile CSS selectors
await page.locator('.btn-primary').click();
```

### Waiting for Elements

```typescript
// Wait for element to be visible
await expect(page.locator('text=Success')).toBeVisible();

// Wait for URL change
await expect(page).toHaveURL(/.*\/dashboard/);

// Wait for text content
await expect(page.locator('h1')).toHaveText('Dashboard');

// Wait for attribute
await expect(page.locator('input')).toHaveAttribute('value', 'expected');
```

## CI/CD Integration

Tests are automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Daily at 2 AM UTC
- Manual trigger

### GitHub Actions

The `.github/workflows/e2e-tests.yml` file contains:
- Full test suite execution
- Matrix testing for individual test suites
- Artifact upload for test reports
- 60-minute timeout for full tests
- 30-minute timeout for individual suites

## Debugging Tests

### Local Debugging
```bash
# Run with debug mode
npm run test:debug

# Run specific test with debug
npx playwright test tests/auth.spec.ts --debug

# Run with UI mode for interactive debugging
npm run test:ui
```

### Debugging Tips

1. **Use `page.pause()`** to pause execution
2. **Use `console.log()`** for debugging
3. **Take screenshots** on failure
4. **Use `--headed` mode** to see browser
5. **Check network tab** for API issues
6. **Use `page.waitForTimeout()`** for debugging timing issues

### Common Issues

1. **Timing issues**: Use `expect().toBeVisible()` instead of `waitForTimeout()`
2. **Element not found**: Check if element is in iframe or shadow DOM
3. **Network issues**: Check CORS and API endpoints
4. **Authentication**: Ensure test credentials are correct
5. **Environment**: Verify base URL and API endpoints

## Test Reports

After running tests, you can view detailed reports:

```bash
# Open HTML report
npm run test:report

# Or directly
npx playwright show-report
```

The report includes:
- Test results overview
- Screenshots on failure
- Videos on failure
- Traces for debugging
- Performance metrics
- Timeline view

## Maintenance

### Regular Tasks

1. **Update test data** when application changes
2. **Review test failures** and update selectors
3. **Add new tests** for new features
4. **Update dependencies** regularly
5. **Monitor test performance** and optimize slow tests

### Test Maintenance

- Keep tests independent and isolated
- Use meaningful test data
- Clean up test data after tests
- Update selectors when UI changes
- Remove obsolete tests
- Document test dependencies

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Add appropriate assertions
4. Handle edge cases
5. Update this documentation
6. Test your tests locally first

## Support

For issues with tests:
1. Check the test report for details
2. Run tests locally to reproduce
3. Check browser console for errors
4. Verify application is running
5. Check network connectivity
6. Review test configuration
