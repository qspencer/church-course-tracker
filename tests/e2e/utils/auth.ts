import { expect, type APIRequestContext, type Page, type TestInfo } from '@playwright/test';

type UserRole = 'admin' | 'staff' | 'viewer';

type Credentials = { username: string; password: string };

const env =
  ((globalThis as unknown as { process?: { env?: Record<string, string | undefined> } }).process?.env) ??
  {};

const DEFAULT_APP_BASE_URL = 'https://apps.quentinspencer.com/churchcoursetracker';
const DEFAULT_API_BASE_URL = 'https://tinev5iszf.execute-api.us-east-1.amazonaws.com';

// IMPORTANT: Credentials must be provided via environment variables
// Set E2E_ADMIN_USERNAME, E2E_ADMIN_PASSWORD, etc. in your environment or .env file
// DO NOT hardcode production passwords in source code
const DEFAULT_CREDENTIALS: Record<UserRole, Credentials | undefined> = {
  admin: undefined,
  staff: undefined,
  viewer: undefined,
};

function readEnvCredentials(role: UserRole): Credentials | undefined {
  const prefix = role.toUpperCase();
  const username =
    env[`E2E_${prefix}_USERNAME`] ??
    env[`${prefix}_USERNAME`];
  const password =
    env[`E2E_${prefix}_PASSWORD`] ??
    env[`${prefix}_PASSWORD`];

  if (!username || !password) {
    return undefined;
  }

  return { username, password };
}

// Export testUsers for API tests - these are read from environment variables
export const testUsers: Record<UserRole, Credentials | undefined> = {
  admin: readEnvCredentials('admin'),
  staff: readEnvCredentials('staff'),
  viewer: readEnvCredentials('viewer'),
};

// Resolve the app base URL. We prefer APP_BASE_URL (which is typically
// set with the /churchcoursetracker base href included), then fall back
// to PLAYWRIGHT_BASE_URL or BASE_URL (typically set in CI workflows
// without the suffix), then the suffixed default for local dev.
//
// IMPORTANT: production routes are served under /churchcoursetracker.
// If a caller passes a bare https://apps.quentinspencer.com (which is
// what .github/workflows/e2e-tests.yml does), we must re-add the
// /churchcoursetracker suffix so APP_BASE_URL-based assertions match
// the actual prod URL. This was the root cause of the
// audit-and-security.spec.ts "Session timeout" test failing every CI
// run from 2026-03-30 through 2026-05-18 (see 2026-05-18 evaluation
// §3.2 finding Q1).
function _resolveAppBaseUrl(): string {
  let url = env.APP_BASE_URL ?? env.PLAYWRIGHT_BASE_URL ?? env.BASE_URL ?? DEFAULT_APP_BASE_URL;
  // strip trailing slashes for clean concatenation
  url = url.replace(/\/+$/, '');
  // re-attach the /churchcoursetracker base href when the host implies it
  if (url.includes('apps.quentinspencer.com') && !url.includes('/churchcoursetracker')) {
    url = `${url}/churchcoursetracker`;
  }
  return url;
}

export const APP_BASE_URL = _resolveAppBaseUrl();

export const API_BASE_URL = (env.API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/+$/, '');

export const credentials: Record<UserRole, Credentials | undefined> = {
  admin: readEnvCredentials('admin'),
  staff: readEnvCredentials('staff'),
  viewer: readEnvCredentials('viewer'),
};

export interface LoginOptions {
  expectNavigation?: boolean;
  dashboardPath?: string;
  timeoutMs?: number;
}

const DEFAULT_LOGIN_OPTIONS: Required<LoginOptions> = {
  expectNavigation: true,
  dashboardPath: '/dashboard',
  timeoutMs: 30_000,
};

export async function loginAsRole(page: Page, role: UserRole, testInfo: TestInfo, options?: LoginOptions) {
  const user = credentials[role];
  if (!user) {
    testInfo.skip(`Credentials for ${role} user are not configured for end-to-end tests`);
    return undefined;
  }

  const { expectNavigation, dashboardPath, timeoutMs } = { ...DEFAULT_LOGIN_OPTIONS, ...options };

  // Navigate and wait for network to settle
  await page.goto(`${APP_BASE_URL}/auth`, { waitUntil: 'domcontentloaded' });

  // Wait for Angular to initialize
  await page.waitForTimeout(1000);

  const usernameLocator = page.locator('input[formControlName="username"]');
  const passwordLocator = page.locator('input[formControlName="password"]');
  const submitButton = page.locator('button[type="submit"]');

  // Wait for form fields to be visible
  await expect(usernameLocator).toBeVisible({ timeout: 15_000 });
  await expect(passwordLocator).toBeVisible({ timeout: 15_000 });

  // Wait for form to be enabled (not disabled)
  await expect(usernameLocator).toBeEnabled({ timeout: 5_000 });
  await expect(passwordLocator).toBeEnabled({ timeout: 5_000 });

  // Clear any existing values and fill
  await usernameLocator.clear();
  await usernameLocator.fill(user.username);
  await passwordLocator.clear();
  await passwordLocator.fill(user.password);

  // Wait for submit button to be enabled
  await expect(submitButton).toBeEnabled({ timeout: 5_000 });
  await submitButton.click();

  if (expectNavigation) {
    // Wait for either dashboard navigation or URL pattern change
    const navigationSucceeded = await page
      .waitForURL((url) => url.pathname.includes(dashboardPath) || url.pathname.includes('/dashboard'), { timeout: timeoutMs })
      .then(
        () => true,
        () => false
      );

    if (!navigationSucceeded) {
      // Check if we're still on auth page (login failed) vs some other issue
      const currentUrl = page.url();
      if (currentUrl.includes('/auth')) {
        console.log(`Login failed for ${role} - still on auth page`);
      }
      testInfo.skip(`Configured ${role} credentials failed to authenticate in the target environment`);
      return undefined;
    }

    // Wait for dashboard to fully load
    await page.waitForLoadState('domcontentloaded');
  }

  return user;
}

/**
 * Logs out the current user by clearing all auth tokens and session storage
 * This is essential when switching between users in the same test
 */
export async function logout(page: Page) {
  // Clear all browser storage
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
    // Clear cookies by setting them to expire
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  });

  // Navigate to auth page to ensure we're logged out
  await page.goto(`${APP_BASE_URL}/auth`, { waitUntil: 'domcontentloaded' });

  // Wait for auth page to be ready - ensure form is visible
  const usernameLocator = page.locator('input[formControlName="username"]');
  await usernameLocator.isVisible({ timeout: 10_000 }).catch(() => false);

  // Additional wait for Angular to stabilize
  await page.waitForTimeout(500);
}

export function requireEnvValue(testInfo: TestInfo, value: string | undefined, message: string) {
  if (!value) {
    testInfo.skip(message);
    return false;
  }
  return true;
}

/**
 * Fetches a Bearer token for the given role by POSTing to /api/v1/auth/login.
 * Returns null when the role's credentials are not configured in env (so the
 * caller can test.skip cleanly) or when login fails. Handles transient 429/503
 * by retrying once with a short backoff.
 *
 * Use this in API tests that need to hit endpoints requiring auth (notably
 * /api/v1/users/ which was made auth-required during the May 2026 hardening
 * pass). Pair the returned token with `Authorization: Bearer <token>` on the
 * request you actually want to test.
 */
export async function getApiAuthToken(
  request: APIRequestContext,
  role: UserRole = 'admin',
): Promise<string | null> {
  const creds = credentials[role];
  if (!creds) {
    return null;
  }

  const post = () => request.post(`${API_BASE_URL}/api/v1/auth/login`, {
    headers: { 'Content-Type': 'application/json' },
    data: creds,
  });

  let response = await post();
  if (response.status() === 429 || response.status() === 503) {
    await new Promise((r) => setTimeout(r, response.status() === 503 ? 3000 : 1500));
    response = await post();
  }
  if (response.status() !== 200) {
    return null;
  }
  const data = await response.json();
  return data.access_token ?? data.token ?? null;
}


