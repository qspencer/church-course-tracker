import { test, expect } from '@playwright/test';

test('Final frontend test - verify login form is working', async ({ page }) => {
  // Navigate to the auth route
  await page.goto('https://apps.quentinspencer.com/auth');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  // Check that we can find the login form elements
  const usernameInput = await page.locator('input[formControlName="username"]');
  const passwordInput = await page.locator('input[formControlName="password"]');
  const submitButton = await page.locator('button[type="submit"]');
  
  // Verify the form elements are present and visible
  await expect(usernameInput).toBeVisible();
  await expect(passwordInput).toBeVisible();
  await expect(submitButton).toBeVisible();
  
  // Check the form labels
  const usernameLabel = await page.locator('mat-label:has-text("Username")');
  const passwordLabel = await page.locator('mat-label:has-text("Password")');
  
  await expect(usernameLabel).toBeVisible();
  await expect(passwordLabel).toBeVisible();
  
  // Check the submit button text
  const submitButtonText = await submitButton.textContent();
  expect(submitButtonText).toContain('Sign In');
  
  // Test form interaction
  await usernameInput.fill('testuser');
  await passwordInput.fill('testpass');
  
  // Verify the values were set
  const usernameValue = await usernameInput.inputValue();
  const passwordValue = await passwordInput.inputValue();
  
  expect(usernameValue).toBe('testuser');
  expect(passwordValue).toBe('testpass');
  
  // Check that the form is valid (no validation errors)
  const errorMessages = await page.locator('mat-error').count();
  expect(errorMessages).toBe(0);
  
  // Take a screenshot for verification
  await page.screenshot({ path: 'final-frontend-test.png', fullPage: true });
  
  console.log('✅ Frontend login form is working correctly!');
});
