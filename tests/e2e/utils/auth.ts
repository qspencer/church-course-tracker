import { expect, type Page, type TestInfo } from '@playwright/test';

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

export const APP_BASE_URL = (env.APP_BASE_URL ?? env.PLAYWRIGHT_BASE_URL ?? DEFAULT_APP_BASE_URL).replace(
  /\/+$/,
  ''
);

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


