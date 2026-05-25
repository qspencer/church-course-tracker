// Base environment file - will be replaced by environment.dev.ts or environment.prod.ts during build
// For local development (ng serve), uses environment.dev.ts
// For production builds, uses environment.prod.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Church Course Tracker',
  version: '0.97', // This should match environment.prod.ts - will be replaced during build
  enableAnalytics: false,
  enableErrorReporting: false,  // Disabled in dev
  logLevel: 'debug', // 'debug', 'info', 'warn', 'error'
  sentry: {
    dsn: '',  // Empty in dev - errors not sent to Sentry
    environment: 'development',
    tracePropagationTargets: ['localhost'],
    tracesSampleRate: 0.0  // No tracing in dev
  }
};
