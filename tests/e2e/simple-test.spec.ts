import { test, expect } from '@playwright/test';

test('Simple test to verify setup', async ({ page }) => {
  await page.goto('https://apps.quentinspencer.com');
  await expect(page).toHaveTitle(/Church Course Tracker/);
});
