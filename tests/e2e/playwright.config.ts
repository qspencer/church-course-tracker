import { defineConfig, devices } from '@playwright/test';

const env =
  ((globalThis as unknown as { process?: { env?: Record<string, string | undefined> } }).process?.env) ??
  {};

// Determine if we're testing against a remote URL (not localhost)
// Match the logic from utils/auth.ts - default includes the /churchcoursetracker path
let baseURL = env.APP_BASE_URL || env.PLAYWRIGHT_BASE_URL || env.BASE_URL || 'https://apps.quentinspencer.com/churchcoursetracker';
// Ensure the path is included if testing against the production domain
if (baseURL.includes('apps.quentinspencer.com') && !baseURL.includes('/churchcoursetracker')) {
  baseURL = `${baseURL}/churchcoursetracker`;
}
// Remove trailing slashes
baseURL = baseURL.replace(/\/+$/, '');
const isRemoteURL = baseURL && !baseURL.includes('localhost') && !baseURL.includes('127.0.0.1');

/**
 * @see https://playwright.dev/docs/test-configuration
 */
const config = {
  testDir: './',
  /* Global setup - loads CSV test data before tests run */
  globalSetup: require.resolve('./global-setup.ts'),
  /* Global teardown - cleans up CSV test data after tests complete */
  globalTeardown: require.resolve('./global-teardown.ts'),
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!env.CI,
  /* Retry on CI only - increased to 2 for network resilience */
  retries: env.CI ? 2 : 0,
  /* Use multiple workers for parallel execution - 1 on CI to avoid rate limiting, 4 locally */
  workers: env.CI ? 1 : 4,
  /* Global test timeout - increased for slower CI environments and network latency */
  timeout: env.CI ? 300000 : 30000, // 5 minutes in CI, 30 seconds locally
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: baseURL,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',

    /* Record video on failure */
    video: 'retain-on-failure',

    /* Global timeout for each action - increased in CI for network latency */
    actionTimeout: env.CI ? 60000 : 30000, // 1 minute in CI, 30 seconds locally

    /* Global timeout for navigation - increased in CI for network latency */
    navigationTimeout: env.CI ? 90000 : 30000, // 1.5 minutes in CI, 30 seconds locally
  },

  /* Configure projects for major browsers */
  /* In CI, only test chromium for faster execution. Locally, test all browsers. */
  projects: env.CI
    ? [
        /* CI: Only test chromium for faster execution */
        {
          name: 'chromium',
          use: { ...devices['Desktop Chrome'] },
        },
      ]
    : [
        /* Local: Test all browsers */
        {
          name: 'chromium',
          use: { ...devices['Desktop Chrome'] },
        },
        {
          name: 'firefox',
          use: { ...devices['Desktop Firefox'] },
        },
        {
          name: 'webkit',
          use: { ...devices['Desktop Safari'] },
        },
        /* Test against mobile viewports. */
        {
          name: 'Mobile Chrome',
          use: { ...devices['Pixel 5'] },
        },
        {
          name: 'Mobile Safari',
          use: { ...devices['iPhone 12'] },
        },
        /* Test against branded browsers. */
        {
          name: 'Microsoft Edge',
          use: { ...devices['Desktop Edge'], channel: 'msedge' },
        },
        {
          name: 'Google Chrome',
          use: { ...devices['Desktop Chrome'], channel: 'chrome' },
        },
      ],
};

// Only use webServer when testing locally (not against remote URLs)
if (!isRemoteURL) {
  config.webServer = {
    command: 'echo "Tests will run against production environment"',
    url: baseURL,
    reuseExistingServer: !env.CI,
  };
}

export default defineConfig(config);
