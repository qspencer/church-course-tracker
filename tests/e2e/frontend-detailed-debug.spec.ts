import { test, expect } from '@playwright/test';

test('Detailed frontend debugging', async ({ page }) => {
  // Navigate to the frontend
  await page.goto('https://apps.quentinspencer.com');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Wait longer for Angular to initialize
  await page.waitForTimeout(5000);
  
  // Check if Angular app loaded
  const appRoot = await page.locator('app-root');
  const appRootContent = await appRoot.textContent();
  console.log('App root content after 5s:', appRootContent);
  
  // Check for Angular version
  const angularVersion = await page.evaluate(() => {
    const element = document.querySelector('[ng-version]');
    return element ? element.getAttribute('ng-version') : null;
  });
  console.log('Angular version:', angularVersion);
  
  // Check for any error messages in the page
  const errorMessages = await page.locator('[class*="error"], [class*="Error"], .error, .Error').all();
  console.log('Error elements found:', errorMessages.length);
  for (const error of errorMessages) {
    const text = await error.textContent();
    console.log('Error text:', text);
  }
  
  // Check for any loading indicators
  const loadingElements = await page.locator('[class*="loading"], [class*="spinner"], .loading, .spinner').all();
  console.log('Loading elements found:', loadingElements.length);
  
  // Check for any router outlet or main content
  const routerOutlet = await page.locator('router-outlet').count();
  const mainContent = await page.locator('main, [role="main"]').count();
  console.log('Router outlets:', routerOutlet);
  console.log('Main content areas:', mainContent);
  
  // Check for any navigation elements
  const navElements = await page.locator('nav, [role="navigation"]').count();
  console.log('Navigation elements:', navElements);
  
  // Check for any login-related elements with different selectors
  const loginSelectors = [
    'input[type="text"]',
    'input[type="email"]', 
    'input[type="password"]',
    'input[name*="user"]',
    'input[name*="email"]',
    'input[name*="login"]',
    'input[placeholder*="user"]',
    'input[placeholder*="email"]',
    'input[placeholder*="login"]',
    'button[type="submit"]',
    'button:has-text("Login")',
    'button:has-text("Sign In")',
    'form'
  ];
  
  for (const selector of loginSelectors) {
    const elements = await page.locator(selector).count();
    if (elements > 0) {
      console.log(`Found ${elements} elements with selector: ${selector}`);
    }
  }
  
  // Check for any Angular-specific components
  const angularComponents = await page.locator('[ng-reflect-], [ng-reflect-router], [ng-reflect-ng-for]').count();
  console.log('Angular components with reflections:', angularComponents);
  
  // Get the full page HTML to see what's actually rendered
  const bodyContent = await page.locator('body').innerHTML();
  console.log('Body content length:', bodyContent.length);
  console.log('Body content preview:', bodyContent.substring(0, 500));
  
  // Check for any console errors
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  // Wait a bit more for any async operations
  await page.waitForTimeout(3000);
  
  console.log('Console errors:', consoleErrors);
  
  // Take a screenshot for visual debugging
  await page.screenshot({ path: 'debug-frontend-detailed.png', fullPage: true });
});
