import { test, expect } from '@playwright/test';

test('Test auth route specifically', async ({ page }) => {
  // Navigate directly to the auth route
  await page.goto('https://apps.quentinspencer.com/auth');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Wait longer for Angular to initialize
  await page.waitForTimeout(5000);
  
  // Check if we can find the login form elements
  const usernameInput = await page.locator('input[formControlName="username"]').count();
  const passwordInput = await page.locator('input[formControlName="password"]').count();
  const submitButton = await page.locator('button[type="submit"]').count();
  const loginForm = await page.locator('form').count();
  
  console.log('Username inputs (formControlName="username"):', usernameInput);
  console.log('Password inputs (formControlName="password"):', passwordInput);
  console.log('Submit buttons:', submitButton);
  console.log('Forms:', loginForm);
  
  // Check for any Angular Material form fields
  const matFormFields = await page.locator('mat-form-field').count();
  console.log('Material form fields:', matFormFields);
  
  // Check for any input elements with different selectors
  const allInputs = await page.locator('input').all();
  console.log('All inputs found:', allInputs.length);
  
  for (let i = 0; i < allInputs.length; i++) {
    const input = allInputs[i];
    const type = await input.getAttribute('type');
    const name = await input.getAttribute('name');
    const formControlName = await input.getAttribute('formControlName');
    const placeholder = await input.getAttribute('placeholder');
    console.log(`Input ${i}: type=${type}, name=${name}, formControlName=${formControlName}, placeholder=${placeholder}`);
  }
  
  // Check for any buttons
  const allButtons = await page.locator('button').all();
  console.log('All buttons found:', allButtons.length);
  
  for (let i = 0; i < allButtons.length; i++) {
    const button = allButtons[i];
    const type = await button.getAttribute('type');
    const text = await button.textContent();
    console.log(`Button ${i}: type=${type}, text="${text}"`);
  }
  
  // Check the current URL
  const currentUrl = page.url();
  console.log('Current URL:', currentUrl);
  
  // Check for any error messages
  const errorElements = await page.locator('[class*="error"], [class*="Error"], .error, .Error').all();
  console.log('Error elements found:', errorElements.length);
  for (const error of errorElements) {
    const text = await error.textContent();
    console.log('Error text:', text);
  }
  
  // Get the full page HTML to see what's actually rendered
  const bodyContent = await page.locator('body').innerHTML();
  console.log('Body content length:', bodyContent.length);
  console.log('Body content preview:', bodyContent.substring(0, 1000));
  
  // Take a screenshot for visual debugging
  await page.screenshot({ path: 'debug-auth-route.png', fullPage: true });
  
  // The test should pass if we can find the login form elements
  expect(usernameInput).toBeGreaterThan(0);
  expect(passwordInput).toBeGreaterThan(0);
  expect(submitButton).toBeGreaterThan(0);
});
