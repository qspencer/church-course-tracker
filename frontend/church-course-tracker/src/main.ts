import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { environment } from './environments/environment';
import '@angular/compiler';
import * as Sentry from '@sentry/angular';

// Initialize Sentry for production error tracking
if (environment.production && environment.enableErrorReporting) {
  Sentry.init({
    dsn: environment.sentry.dsn,
    environment: environment.sentry.environment,
    integrations: [
      Sentry.browserTracingIntegration(),
    ],
    tracePropagationTargets: environment.sentry.tracePropagationTargets,
    tracesSampleRate: environment.sentry.tracesSampleRate,
    beforeSend(event) {
      // Filter out sensitive data
      if (event.request?.headers) {
        delete event.request.headers['Authorization'];
      }
      return event;
    },
  });
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
