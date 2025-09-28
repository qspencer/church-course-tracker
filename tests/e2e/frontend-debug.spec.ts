import { test, expect } from '@playwright/test';

test('Debug frontend loading', async ({ page }) => {
  // Navigate to the frontend
  await page.goto('https://apps.quentinspencer.com');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Take a screenshot for debugging
  await page.screenshot({ path: 'debug-frontend.png' });
  
  // Check if Angular app loaded
  const appRoot = await page.locator('app-root');
  const appRootContent = await appRoot.textContent();
  console.log('App root content:', appRootContent);
  
  // Check for any error messages
  const errorElements = await page.locator('[class*="error"], [class*="Error"]').all();
  console.log('Error elements found:', errorElements.length);
  
  // Check for login form elements
  const usernameInput = await page.locator('input[name="username"]').count();
  const passwordInput = await page.locator('input[name="password"]').count();
  const loginForm = await page.locator('form').count();
  
  console.log('Username inputs:', usernameInput);
  console.log('Password inputs:', passwordInput);
  console.log('Forms:', loginForm);
  
  // Check for any Angular-specific elements
  const angularElements = await page.locator('[ng-version], [data-ng-version]').count();
  console.log('Angular elements:', angularElements);
  
  // Get page title
  const title = await page.title();
  console.log('Page title:', title);
  
  // Check for console errors
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  // Wait a bit for any async operations
  await page.waitForTimeout(2000);
  
  console.log('Console errors:', consoleErrors);
  
  // Check if we can find any login-related elements
  const allInputs = await page.locator('input').all();
  console.log('All inputs found:', allInputs.length);
  
  for (let i = 0; i < allInputs.length; i++) {
    const input = allInputs[i];
    const type = await input.getAttribute('type');
    const name = await input.getAttribute('name');
    const placeholder = await input.getAttribute('placeholder');
    console.log(`Input ${i}: type=${type}, name=${name}, placeholder=${placeholder}`);
  }
});
