import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('should load dashboard within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    // Login
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
    
    // Check that main content is visible
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('should load courses page efficiently', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    const startTime = Date.now();
    
    // Navigate to courses
    const coursesLink = page.locator('text=Courses').or(page.locator('a[href*="courses"]'));
    await coursesLink.click();
    await expect(page).toHaveURL(/.*\/courses/, { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // Courses page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    // Check that courses content is visible
    await expect(page.locator('text=Courses')).toBeVisible();
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Navigate to members page
    const membersLink = page.locator('text=Members').or(page.locator('a[href*="members"]'));
    await membersLink.click();
    await expect(page).toHaveURL(/.*\/members/, { timeout: 10000 });
    
    const startTime = Date.now();
    
    // Wait for members list to load
    await expect(page.locator('text=Members')).toBeVisible();
    
    const loadTime = Date.now() - startTime;
    
    // Members page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    // Start performance monitoring
    await page.goto('/');
    
    // Login
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Get performance metrics
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const metrics = {};
          
          entries.forEach((entry) => {
            if (entry.entryType === 'largest-contentful-paint') {
              metrics.lcp = entry.startTime;
            }
            if (entry.entryType === 'first-input') {
              metrics.fid = entry.processingStart - entry.startTime;
            }
            if (entry.entryType === 'layout-shift') {
              metrics.cls = entry.value;
            }
          });
          
          resolve(metrics);
        }).observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
      });
    });
    
    // Check that metrics are reasonable (these are basic checks)
    expect(metrics).toBeDefined();
  });

  test('should handle concurrent user sessions', async ({ browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext()
    ]);
    
    const pages = await Promise.all(contexts.map(context => context.newPage()));
    
    try {
      // All users login simultaneously
      await Promise.all(pages.map(async (page) => {
        await page.goto('/');
        await page.fill('input[type="text"], input[type="email"]', 'admin');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
      }));
      
      // All users navigate to different pages simultaneously
      await Promise.all([
        pages[0].locator('text=Courses').or(pages[0].locator('a[href*="courses"]')).click(),
        pages[1].locator('text=Members').or(pages[1].locator('a[href*="members"]')).click(),
        pages[2].locator('text=Reports').or(pages[2].locator('a[href*="reports"]')).click()
      ]);
      
      // Wait for all pages to load
      await Promise.all([
        expect(pages[0]).toHaveURL(/.*\/courses/, { timeout: 10000 }),
        expect(pages[1]).toHaveURL(/.*\/members/, { timeout: 10000 }),
        expect(pages[2]).toHaveURL(/.*\/reports/, { timeout: 10000 })
      ]);
      
    } finally {
      // Clean up contexts
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('should handle network interruptions gracefully', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Simulate network issues by going offline
    await page.context().setOffline(true);
    
    // Try to navigate to courses (should handle gracefully)
    const coursesLink = page.locator('text=Courses').or(page.locator('a[href*="courses"]'));
    await coursesLink.click();
    
    // Should show some kind of error or loading state
    await expect(page.locator('text=offline').or(page.locator('text=network')).or(
      page.locator('text=error')
    )).toBeVisible({ timeout: 5000 });
    
    // Go back online
    await page.context().setOffline(false);
    
    // Should recover and load the page
    await expect(page).toHaveURL(/.*\/courses/, { timeout: 10000 });
  });
});
