// Version will be injected at build time by the deployment script
export const environment = {
  production: true,
  apiUrl: 'https://api.quentinspencer.com/api/v1',
  appName: 'Church Course Tracker',
  version: '0.37',
  // Add other production-specific configurations
  enableAnalytics: true,
  enableErrorReporting: true,
  logLevel: 'error'
};