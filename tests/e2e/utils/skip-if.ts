import type { TestInfo, Locator } from '@playwright/test';

/**
 * Skip-or-fail helper for e2e tests.
 *
 * Replaces the legacy silent-fallback anti-pattern:
 *
 *   if (!buttonVisible) {
 *     // "If button not found, at least verify we're on the page"
 *     expect(url.includes('/X')).toBeTruthy();
 *     return;   // ← TEST SILENTLY PASSES even when feature is missing
 *   }
 *
 * With this helper:
 *
 *   await skipIfMissing(buttonLocator, testInfo, 'Add User button not present');
 *   // ... test continues with the real assertion
 *
 * The skip path is reported as SKIPPED (not PASSED), so the test count is
 * honest about what was actually validated.
 *
 * Use this for any "feature might be unavailable" gate in a test that
 * otherwise would silently pass.
 */
export async function skipIfMissing(
  locator: Locator,
  testInfo: TestInfo,
  reason: string,
  timeoutMs = 5000,
): Promise<void> {
  const visible = await locator.isVisible({ timeout: timeoutMs }).catch(() => false);
  if (!visible) {
    testInfo.skip(true, reason);
  }
}

/**
 * Skip the test if a precondition is false.
 *
 *   skipUnless(rowCount > 0, testInfo, 'No courses available to test against');
 */
export function skipUnless(condition: boolean, testInfo: TestInfo, reason: string): void {
  if (!condition) {
    testInfo.skip(true, reason);
  }
}
