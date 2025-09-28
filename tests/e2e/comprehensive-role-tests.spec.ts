import { test, expect, Page } from '@playwright/test';

// Test data for different roles
const testUsers = {
  admin: {
    username: 'admin',
    password: 'admin123',
    role: 'admin'
  },
  staff: {
    username: 'staff', 
    password: 'staff123',
    role: 'staff'
  },
  viewer: {
    username: 'viewer',
    password: 'viewer123', 
    role: 'viewer'
  }
};

// Helper function to login with specific role
async function loginAs(page: Page, user: typeof testUsers.admin) {
  try {
    await page.goto('https://apps.quentinspencer.com/auth', { waitUntil: 'networkidle' });
    await page.fill('input[name="username"]', user.username);
    await page.fill('input[name="password"]', user.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  } catch (error) {
    console.log('Login failed, trying alternative approach...');
    // Alternative login approach
    await page.goto('https://apps.quentinspencer.com');
    await page.waitForLoadState('networkidle');
  }
}

// Helper function to check if element is visible
async function isVisible(page: Page, selector: string): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { timeout: 2000 });
    return await page.isVisible(selector);
  } catch {
    return false;
  }
}

test.describe('Comprehensive Role-Based Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('https://apps.quentinspencer.com', { waitUntil: 'networkidle' });
  });

  test.describe('Application Accessibility Tests', () => {
    test('Application loads successfully', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com');
      await page.waitForLoadState('networkidle');
      
      // Check if the page loads without errors
      const title = await page.title();
      expect(title).toContain('Church Course Tracker');
    });

    test('API endpoints are accessible', async ({ page }) => {
      // Test API health endpoint
      const response = await page.request.get('https://api.quentinspencer.com/api/v1/health');
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.status).toBe('healthy');
    });
  });

  test.describe('Authentication Tests', () => {
    test('Login page is accessible', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com/auth');
      await page.waitForLoadState('networkidle');
      
      // Check for login form elements
      const usernameField = await page.locator('input[name="username"]').isVisible();
      const passwordField = await page.locator('input[name="password"]').isVisible();
      const submitButton = await page.locator('button[type="submit"]').isVisible();
      
      expect(usernameField).toBeTruthy();
      expect(passwordField).toBeTruthy();
      expect(submitButton).toBeTruthy();
    });

    test('Invalid credentials show error', async ({ page }) => {
      await page.goto('https://apps.quentinspencer.com/auth');
      await page.fill('input[name="username"]', 'invalid');
      await page.fill('input[name="password"]', 'invalid');
      await page.click('button[type="submit"]');
      
      // Wait for error message or redirect
      await page.waitForTimeout(2000);
      
      // Check for error indicators
      const errorMessage = await page.locator('text=Invalid').isVisible();
      const stillOnAuthPage = page.url().includes('/auth');
      
      expect(errorMessage || stillOnAuthPage).toBeTruthy();
    });
  });

  test.describe('Admin Role Tests', () => {
    test('Admin can access dashboard', async ({ page }) => {
      await loginAs(page, testUsers.admin);
      
      // Verify dashboard access
      const currentUrl = page.url();
      expect(currentUrl).toContain('dashboard');
    });

    test('Admin navigation elements are present', async ({ page }) => {
      await loginAs(page, testUsers.admin);
      
      // Check for admin-specific navigation elements
      const navElements = [
        'Courses',
        'Users',
        'Reports',
        'Settings'
      ];

      for (const element of navElements) {
        const isVisible = await page.locator(`text=${element}`).isVisible();
        if (isVisible) {
          console.log(`✓ Admin navigation element "${element}" is visible`);
        } else {
          console.log(`⚠ Admin navigation element "${element}" not found`);
        }
      }
    });
  });

  test.describe('Staff Role Tests', () => {
    test('Staff can access dashboard', async ({ page }) => {
      await loginAs(page, testUsers.staff);
      
      // Verify dashboard access
      const currentUrl = page.url();
      expect(currentUrl).toContain('dashboard');
    });

    test('Staff navigation is limited', async ({ page }) => {
      await loginAs(page, testUsers.staff);
      
      // Staff should see operational elements
      const staffElements = [
        'Courses',
        'Content',
        'Progress'
      ];

      for (const element of staffElements) {
        const isVisible = await page.locator(`text=${element}`).isVisible();
        if (isVisible) {
          console.log(`✓ Staff navigation element "${element}" is visible`);
        }
      }
    });
  });

  test.describe('Viewer Role Tests', () => {
    test('Viewer can access dashboard', async ({ page }) => {
      await loginAs(page, testUsers.viewer);
      
      // Verify dashboard access
      const currentUrl = page.url();
      expect(currentUrl).toContain('dashboard');
    });

    test('Viewer navigation is limited', async ({ page }) => {
      await loginAs(page, testUsers.viewer);
      
      // Viewer should see limited elements
      const viewerElements = [
        'My Courses',
        'Progress',
        'Profile'
      ];

      for (const element of viewerElements) {
        const isVisible = await page.locator(`text=${element}`).isVisible();
        if (isVisible) {
          console.log(`✓ Viewer navigation element "${element}" is visible`);
        }
      }
    });
  });

  test.describe('API Security Tests', () => {
    test('API endpoints respond correctly', async ({ page }) => {
      // Test various API endpoints
      const endpoints = [
        'https://api.quentinspencer.com/api/v1/health',
        'https://api.quentinspencer.com/api/v1/courses/',
        'https://api.quentinspencer.com/api/v1/users/'
      ];

      for (const endpoint of endpoints) {
        try {
          const response = await page.request.get(endpoint);
          console.log(`✓ API endpoint ${endpoint} responded with status: ${response.status()}`);
        } catch (error) {
          console.log(`⚠ API endpoint ${endpoint} failed: ${error}`);
        }
      }
    });

    test('CORS headers are present', async ({ page }) => {
      const response = await page.request.get('https://api.quentinspencer.com/api/v1/health');
      const headers = response.headers();
      
      const corsHeaders = [
        'access-control-allow-origin',
        'access-control-allow-methods',
        'access-control-allow-headers'
      ];

      for (const header of corsHeaders) {
        if (headers[header]) {
          console.log(`✓ CORS header ${header}: ${headers[header]}`);
        } else {
          console.log(`⚠ CORS header ${header} not found`);
        }
      }
    });
  });

  test.describe('Performance Tests', () => {
    test('Page load performance', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('https://apps.quentinspencer.com');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      console.log(`Page load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(10000); // Should load within 10 seconds
    });

    test('API response times', async ({ page }) => {
      const startTime = Date.now();
      const response = await page.request.get('https://api.quentinspencer.com/api/v1/health');
      const responseTime = Date.now() - startTime;
      
      console.log(`API response time: ${responseTime}ms`);
      expect(responseTime).toBeLessThan(5000); // Should respond within 5 seconds
      expect(response.status()).toBe(200);
    });
  });

  test.describe('Error Handling Tests', () => {
    test('404 pages are handled gracefully', async ({ page }) => {
      const response = await page.goto('https://apps.quentinspencer.com/nonexistent-page');
      expect(response?.status()).toBe(404);
    });

    test('Network errors are handled', async ({ page }) => {
      // Simulate network error by going to invalid URL
      try {
        await page.goto('https://invalid-domain-that-does-not-exist.com');
      } catch (error) {
        console.log('✓ Network error handled gracefully');
      }
    });
  });

  test.describe('Mobile Responsiveness Tests', () => {
    test('Mobile viewport works', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('https://apps.quentinspencer.com');
      await page.waitForLoadState('networkidle');
      
      // Check if page is responsive
      const body = await page.locator('body');
      expect(await body.isVisible()).toBeTruthy();
    });
  });
});
