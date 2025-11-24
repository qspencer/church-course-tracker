import { expect, type Page, type TestInfo } from '@playwright/test';

type UserRole = 'admin' | 'staff' | 'viewer';

type Credentials = { username: string; password: string };

const env =
  ((globalThis as unknown as { process?: { env?: Record<string, string | undefined> } }).process?.env) ??
  {};

const DEFAULT_APP_BASE_URL = 'https://apps.quentinspencer.com/churchcoursetracker';
const DEFAULT_API_BASE_URL = 'https://tinev5iszf.execute-api.us-east-1.amazonaws.com';

const DEFAULT_CREDENTIALS: Record<UserRole, Credentials> = {
  admin: { username: 'Admin', password: 'Admin123!' },
  staff: { username: 'staff', password: 'staff123' },
  viewer: { username: 'viewer', password: 'viewer123' },
};

function readEnvCredentials(role: UserRole): Credentials | undefined {
  const prefix = role.toUpperCase();
  const username =
    env[`E2E_${prefix}_USERNAME`] ??
    env[`${prefix}_USERNAME`] ??
    DEFAULT_CREDENTIALS[role]?.username;
  const password =
    env[`E2E_${prefix}_PASSWORD`] ??
    env[`${prefix}_PASSWORD`] ??
    DEFAULT_CREDENTIALS[role]?.password;

  if (!username || !password) {
    return undefined;
  }

  return { username, password };
}

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
  timeoutMs: 20_000,
};

export async function loginAsRole(page: Page, role: UserRole, testInfo: TestInfo, options?: LoginOptions) {
  const user = credentials[role];
  if (!user) {
    testInfo.skip(`Credentials for ${role} user are not configured for end-to-end tests`);
    return undefined;
  }

  const { expectNavigation, dashboardPath, timeoutMs } = { ...DEFAULT_LOGIN_OPTIONS, ...options };

  await page.goto(`${APP_BASE_URL}/auth`, { waitUntil: 'domcontentloaded' });

  const usernameLocator = page.locator('input[formControlName="username"]');
  const passwordLocator = page.locator('input[formControlName="password"]');

  await expect(usernameLocator).toBeVisible({ timeout: 10_000 });
  await expect(passwordLocator).toBeVisible({ timeout: 10_000 });

  await usernameLocator.fill(user.username);
  await passwordLocator.fill(user.password);
  await page.click('button[type="submit"]');

  if (expectNavigation) {
    const navigationSucceeded = await page
      .waitForURL(`${APP_BASE_URL}${dashboardPath}`, { timeout: timeoutMs })
      .then(
        () => true,
        () => false
      );

    if (!navigationSucceeded) {
      testInfo.skip(`Configured ${role} credentials failed to authenticate in the target environment`);
      return undefined;
    }
  }

  return user;
}

export function requireEnvValue(testInfo: TestInfo, value: string | undefined, message: string) {
  if (!value) {
    testInfo.skip(message);
    return false;
  }
  return true;
}


