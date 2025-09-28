import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
  });

  test('should navigate to courses page', async ({ page }) => {
    // Look for courses navigation link
    const coursesLink = page.locator('text=Courses').or(page.locator('a[href*="courses"]'));
    await expect(coursesLink).toBeVisible();
    
    // Click on courses
    await coursesLink.click();
    
    // Should navigate to courses page
    await expect(page).toHaveURL(/.*\/courses/, { timeout: 10000 });
    
    // Check for courses page content
    await expect(page.locator('text=Courses')).toBeVisible();
  });

  test('should navigate to members page', async ({ page }) => {
    // Look for members navigation link
    const membersLink = page.locator('text=Members').or(page.locator('a[href*="members"]'));
    await expect(membersLink).toBeVisible();
    
    // Click on members
    await membersLink.click();
    
    // Should navigate to members page
    await expect(page).toHaveURL(/.*\/members/, { timeout: 10000 });
    
    // Check for members page content
    await expect(page.locator('text=Members')).toBeVisible();
  });

  test('should navigate to users page (admin only)', async ({ page }) => {
    // Look for users navigation link
    const usersLink = page.locator('text=Users').or(page.locator('a[href*="users"]'));
    
    // Users link should be visible for admin
    await expect(usersLink).toBeVisible();
    
    // Click on users
    await usersLink.click();
    
    // Should navigate to users page
    await expect(page).toHaveURL(/.*\/users/, { timeout: 10000 });
    
    // Check for users page content
    await expect(page.locator('text=Users')).toBeVisible();
  });

  test('should navigate to reports page', async ({ page }) => {
    // Look for reports navigation link
    const reportsLink = page.locator('text=Reports').or(page.locator('a[href*="reports"]'));
    await expect(reportsLink).toBeVisible();
    
    // Click on reports
    await reportsLink.click();
    
    // Should navigate to reports page
    await expect(page).toHaveURL(/.*\/reports/, { timeout: 10000 });
    
    // Check for reports page content
    await expect(page.locator('text=Reports')).toBeVisible();
  });

  test('should navigate back to dashboard', async ({ page }) => {
    // Navigate to a different page first
    const coursesLink = page.locator('text=Courses').or(page.locator('a[href*="courses"]'));
    await coursesLink.click();
    await expect(page).toHaveURL(/.*\/courses/, { timeout: 10000 });
    
    // Look for dashboard navigation link
    const dashboardLink = page.locator('text=Dashboard').or(page.locator('a[href*="dashboard"]'));
    await expect(dashboardLink).toBeVisible();
    
    // Click on dashboard
    await dashboardLink.click();
    
    // Should navigate back to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
  });

  test('should have responsive navigation on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Look for mobile menu button (hamburger menu)
    const mobileMenuButton = page.locator('button[aria-label*="menu"]').or(
      page.locator('button:has-text("Menu")')
    ).or(page.locator('[data-testid="mobile-menu"]'));
    
    // Mobile menu should be visible on small screens
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click();
      
      // Check that navigation items are visible in mobile menu
      await expect(page.locator('text=Courses')).toBeVisible();
      await expect(page.locator('text=Members')).toBeVisible();
    }
  });
});
