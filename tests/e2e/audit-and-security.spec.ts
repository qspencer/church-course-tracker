import { test, expect, Page } from '@playwright/test';

const testUsers = {
  admin: { username: 'admin', password: 'admin123' },
  staff: { username: 'staff', password: 'staff123' },
  viewer: { username: 'viewer', password: 'viewer123' }
};

async function loginAs(page: Page, user: typeof testUsers.admin) {
  await page.goto('https://apps.quentinspencer.com/auth');
  await page.fill('input[name="username"]', user.username);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('https://apps.quentinspencer.com/dashboard');
}

test.describe('Audit and Security Tests', () => {
  test.describe('Admin Audit Access', () => {
    test('Admin can view system audit logs', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Audit Logs');
      
      // Should see audit log interface
      await expect(page.locator('text=System Audit Logs')).toBeVisible();
      await expect(page.locator('text=Recent Activities')).toBeVisible();
      
      // Check for log entries
      await expect(page.locator('tr[data-log-entry]')).toHaveCount.greaterThan(0);
    });

    test('Admin can filter audit logs', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Audit Logs');
      
      // Filter by date range
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-12-31');
      await page.click('button:has-text("Filter")');
      
      await expect(page.locator('text=Filtered Results')).toBeVisible();
    });

    test('Admin can export audit logs', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Audit Logs');
      await page.click('button:has-text("Export Logs")');
      
      // Should see export options
      await expect(page.locator('text=Export Options')).toBeVisible();
      await expect(page.locator('button:has-text("Export CSV")')).toBeVisible();
      await expect(page.locator('button:has-text("Export PDF")')).toBeVisible();
    });

    test('Admin can view audit statistics', async ({ page }) => {
      await loginAs(page, testUsers.admin);

      await page.click('text=Audit Logs');
      await page.click('text=Statistics');
      
      // Should see audit statistics
      await expect(page.locator('text=Audit Statistics')).toBeVisible();
      await expect(page.locator('text=Total Events')).toBeVisible();
      await expect(page.locator('text=User Activities')).toBeVisible();
    });
  });

  test.describe('Staff Audit Restrictions', () => {
    test('Staff cannot access audit logs', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      // Should not see audit logs in navigation
      await expect(page.locator('text=Audit Logs')).not.toBeVisible();
      
      // Try to access audit logs directly
      await page.goto('https://apps.quentinspencer.com/audit');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/dashboard');
    });

    test('Staff can view limited activity logs', async ({ page }) => {
      await loginAs(page, testUsers.staff);

      await page.click('text=Activity Logs');
      
      // Should see limited activity information
      await expect(page.locator('text=Recent Activities')).toBeVisible();
      await expect(page.locator('text=Course Activities')).toBeVisible();
      
      // Should NOT see system audit information
      await expect(page.locator('text=System Audit')).not.toBeVisible();
    });
  });

  test.describe('Viewer Audit Restrictions', () => {
    test('Viewer cannot access any audit information', async ({ page }) => {
      await loginAs(page, testUsers.viewer);

      // Should not see any audit-related navigation
      await expect(page.locator('text=Audit Logs')).not.toBeVisible();
      await expect(page.locator('text=Activity Logs')).not.toBeVisible();
      
      // Try to access audit URLs directly
      await page.goto('https://apps.quentinspencer.com/audit');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/dashboard');
    });
  });

  test.describe('Security Features', () => {
    test('Session timeout redirects to login', async ({ page }) => {
      await loginAs(page, testUsers.admin);
      
      // Simulate session timeout
      await page.context().clearCookies();
      
      await page.goto('https://apps.quentinspencer.com/dashboard');
      await expect(page).toHaveURL('https://apps.quentinspencer.com/auth');
    });

    test('Invalid credentials show error', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com/auth');
      await page.fill('input[name="username"]', 'invalid');
      await page.fill('input[name="password"]', 'invalid');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    test('Account lockout after failed attempts', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com/auth');
      
      // Attempt multiple failed logins
      for (let i = 0; i < 5; i++) {
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', 'wrongpassword');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(1000);
      }
      
      await expect(page.locator('text=Account temporarily locked')).toBeVisible();
    });

    test('Password strength validation', async ({ page }) => {
      await loginAs(page, testUsers.admin);
      
      await page.click('text=Users');
      await page.click('button:has-text("Add User")');
      
      // Test weak password
      await page.fill('input[name="password"]', '123');
      await page.click('button:has-text("Create User")');
      await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
      
      // Test password without special characters
      await page.fill('input[name="password"]', 'password123');
      await page.click('button:has-text("Create User")');
      await expect(page.locator('text=Password must contain special characters')).toBeVisible();
    });
  });

  test.describe('API Security Tests', () => {
    test('API endpoints respect role permissions', async ({ page }) => {
      // Test admin API access
      await loginAs(page, testUsers.admin);
      const adminResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(adminResponse.status()).toBe(200);

      // Test staff API access (should be denied)
      await loginAs(page, testUsers.staff);
      const staffResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(staffResponse.status()).toBe(403);

      // Test viewer API access (should be denied)
      await loginAs(page, testUsers.viewer);
      const viewerResponse = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/audit/');
      expect(viewerResponse.status()).toBe(403);
    });

    test('API rate limiting works', async ({ page }) => {
      await loginAs(page, testUsers.admin);
      
      // Make multiple rapid requests
      const requests = [];
      for (let i = 0; i < 10; i++) {
        requests.push(page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/courses/'));
      }
      
      const responses = await Promise.all(requests);
      const rateLimitedResponses = responses.filter(r => r.status() === 429);
      
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });

    test('CORS headers are properly set', async ({ page }) => {
      const response = await page.request.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/health');
      const headers = response.headers();
      
      expect(headers['access-control-allow-origin']).toBe('https://apps.quentinspencer.com');
      expect(headers['access-control-allow-credentials']).toBe('true');
    });
  });
});
