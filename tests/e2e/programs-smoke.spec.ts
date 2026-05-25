/**
 * Smoke test for /programs UI.
 *
 * Added 2026-05-25 ahead of the Angular 18→21 migration. The May-25
 * pre-upgrade coverage assessment found that the /programs route had
 * ZERO e2e visits across all 19 spec files - meaning a routing or
 * component-boot regression in the programs UI would ship to production
 * undetected by CI. This spec adds a single auth + navigate + smoke-
 * check that verifies the page renders without console errors.
 */
import { test, expect } from '@playwright/test';
import { APP_BASE_URL, loginAsRole } from './utils/auth';

test.describe('Programs page smoke', () => {
  test('renders /programs without console errors after admin login', async ({ page }, testInfo) => {
    // Capture browser console messages so we can fail on any errors that
    // surface during page load (Angular renders some errors as console
    // warnings rather than throwing).
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Log in as admin. loginAsRole skips the test cleanly if creds aren't
    // configured (e.g. when running locally without E2E_ADMIN_PASSWORD).
    const loggedIn = await loginAsRole(page, 'admin', testInfo);
    if (!loggedIn) {
      return; // test.skip was called inside loginAsRole
    }

    // Navigate to /programs and wait for Angular to settle.
    await page.goto(`${APP_BASE_URL}/programs`, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {
      // networkidle can be flaky on prod; not a hard failure if it
      // doesn't reach idle, as long as the page rendered something.
    });

    // The page should have landed on /programs (not bounced to /auth or /).
    expect(page.url()).toContain('/programs');

    // There should be SOME Angular content rendered - the sidenav at minimum.
    // We deliberately don't assert on the programs-table contents (the prod
    // DB content varies). The point is to catch "page failed to render at all".
    const sidenavCount = await page.locator('mat-sidenav, .sidenav-container, router-outlet').count();
    expect(sidenavCount).toBeGreaterThan(0);

    // No fatal console errors during render. We allow specific non-fatal
    // warnings (Sentry initialization, dev-only deprecation notices) that
    // wouldn't constitute a regression.
    const fatalErrors = consoleErrors.filter((msg) => {
      const lower = msg.toLowerCase();
      if (lower.includes('sentry')) return false;
      if (lower.includes('favicon')) return false;
      if (lower.includes('deprecation')) return false;
      return true;
    });
    expect(fatalErrors).toEqual([]);
  });
});
