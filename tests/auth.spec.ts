import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should display login form', async ({ page }) => {
    // Check if we're on the login page
    await expect(page).toHaveURL(/.*\/auth/);
    
    // Check for login form elements
    await expect(page.locator('input[type="text"], input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // Check for login form labels or placeholders
    await expect(page.locator('text=Login')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[type="text"], input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for error message
    await expect(page.locator('text=Invalid')).toBeVisible({ timeout: 10000 });
  });

  test('should login with valid credentials', async ({ page }) => {
    // Fill in valid credentials
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Check for dashboard elements
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('should redirect to dashboard if already authenticated', async ({ page }) => {
    // First login
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Navigate to auth page again
    await page.goto('/auth');
    
    // Should redirect back to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="text"], input[type="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
    
    // Look for logout button/link
    const logoutButton = page.locator('text=Logout').or(page.locator('button:has-text("Logout")'));
    await expect(logoutButton).toBeVisible();
    
    // Click logout
    await logoutButton.click();
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*\/auth/, { timeout: 10000 });
  });
});
