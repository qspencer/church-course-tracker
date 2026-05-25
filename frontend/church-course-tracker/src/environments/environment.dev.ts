export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Church Course Tracker',
  version: '0.98', // Should match environment.prod.ts - updated by scripts/increment-version.sh
  enableAnalytics: false,
  enableErrorReporting: false,  // Disabled in dev
  logLevel: 'debug',
  sentry: {
    dsn: '',  // Empty in dev - errors not sent to Sentry
    environment: 'development',
    tracePropagationTargets: ['localhost'],
    tracesSampleRate: 0.0  // No tracing in dev
  }
};
