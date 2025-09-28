import { test, expect } from '@playwright/test';

test('Debug routing issue', async ({ page }) => {
  // Navigate to the app
  await page.goto('https://apps.quentinspencer.com');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  // Check the current URL
  const currentUrl = page.url();
  console.log('Current URL:', currentUrl);
  
  // Check if we can see the auth-container div
  const authContainer = await page.locator('.auth-container').count();
  console.log('Auth container found:', authContainer);
  
  // Check if we can see the sidenav-container div
  const sidenavContainer = await page.locator('.sidenav-container').count();
  console.log('Sidenav container found:', sidenavContainer);
  
  // Check for any router outlets
  const routerOutlets = await page.locator('router-outlet').count();
  console.log('Router outlets found:', routerOutlets);
  
  // Check for any Angular components
  const appAuth = await page.locator('app-auth').count();
  console.log('App-auth components found:', appAuth);
  
  // Check for any form elements anywhere on the page
  const allInputs = await page.locator('input').count();
  const allButtons = await page.locator('button').count();
  const allForms = await page.locator('form').count();
  
  console.log('All inputs:', allInputs);
  console.log('All buttons:', allButtons);
  console.log('All forms:', allForms);
  
  // Check the body content to see what's actually rendered
  const bodyContent = await page.locator('body').innerHTML();
  console.log('Body content length:', bodyContent.length);
  console.log('Body content preview:', bodyContent.substring(0, 1000));
  
  // Try navigating to /auth directly
  await page.goto('https://apps.quentinspencer.com/auth');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  const authUrl = page.url();
  console.log('After navigating to /auth, URL:', authUrl);
  
  // Check again for form elements
  const authInputs = await page.locator('input').count();
  const authButtons = await page.locator('button').count();
  const authForms = await page.locator('form').count();
  
  console.log('After /auth navigation - inputs:', authInputs);
  console.log('After /auth navigation - buttons:', authButtons);
  console.log('After /auth navigation - forms:', authForms);
  
  // Take a screenshot
  await page.screenshot({ path: 'debug-routing.png', fullPage: true });
});
