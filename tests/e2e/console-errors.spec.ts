import { test, expect } from '@playwright/test';

test('Check for console errors that might be breaking routing', async ({ page }) => {
  const consoleErrors: string[] = [];
  const consoleWarnings: string[] = [];
  
  // Capture console messages
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    } else if (msg.type() === 'warning') {
      consoleWarnings.push(msg.text());
    }
  });
  
  // Capture network errors
  page.on('response', response => {
    if (response.status() >= 400) {
      consoleErrors.push(`Network error: ${response.status()} ${response.url()}`);
    }
  });
  
  // Navigate to the app
  await page.goto('https://apps.quentinspencer.com');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000);
  
  console.log('Console errors:', consoleErrors);
  console.log('Console warnings:', consoleWarnings);
  
  // Try to navigate to /auth and see if there are any errors
  await page.goto('https://apps.quentinspencer.com/auth');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  console.log('After /auth navigation - errors:', consoleErrors);
  console.log('After /auth navigation - warnings:', consoleWarnings);
  
  // Check if any JavaScript files failed to load
  const failedResources = await page.evaluate(() => {
    const resources = performance.getEntriesByType('resource');
    return resources
      .filter(resource => resource.name.includes('.js') || resource.name.includes('.css'))
      .filter(resource => resource.transferSize === 0)
      .map(resource => resource.name);
  });
  
  console.log('Failed resources:', failedResources);
  
  // Take a screenshot
  await page.screenshot({ path: 'console-errors-debug.png', fullPage: true });
  
  // The test should pass if there are no critical errors
  expect(consoleErrors.length).toBe(0);
});
