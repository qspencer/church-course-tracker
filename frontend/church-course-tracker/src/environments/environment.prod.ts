// Version will be injected at build time by the deployment script
export const environment = {
  production: true,
  apiUrl: 'https://api.quentinspencer.com/api/v1',
  appName: 'Church Course Tracker',
  version: '0.84',
  // Add other production-specific configurations
  enableAnalytics: true,
  enableErrorReporting: true,  // Enabled in production
  logLevel: 'error',
  sentry: {
    dsn: 'https://84fc9533391baae4c2bbcbb1760f8206@o4510705558224896.ingest.us.sentry.io/4510705560322048',
    environment: 'production',
    tracesSampleRate: 0.1,  // 10% of transactions for performance monitoring
    tracePropagationTargets: ['localhost', 'api.quentinspencer.com', 'apps.quentinspencer.com']
  }
};