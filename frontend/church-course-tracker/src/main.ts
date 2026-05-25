import { provideZoneChangeDetection, ErrorHandler, importProvidersFrom } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';
import {
  HTTP_INTERCEPTORS,
  provideHttpClient,
  withInterceptorsFromDi,
} from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { provideNativeDateAdapter } from '@angular/material/core';
import * as Sentry from '@sentry/angular';
import '@angular/compiler';

import { environment } from './environments/environment';
import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';
import { AuthInterceptor } from './app/interceptors/auth.interceptor';
import { ErrorInterceptor } from './app/interceptors/error.interceptor';

// Sentry initialization runs before bootstrap so the error handler can hook in.
if (environment.production && environment.enableErrorReporting) {
  Sentry.init({
    dsn: environment.sentry.dsn,
    environment: environment.sentry.environment,
    integrations: [Sentry.browserTracingIntegration()],
    tracePropagationTargets: environment.sentry.tracePropagationTargets,
    tracesSampleRate: environment.sentry.tracesSampleRate,
    beforeSend(event) {
      if (event.request?.headers) {
        delete event.request.headers['Authorization'];
      }
      return event;
    },
  });
}

bootstrapApplication(AppComponent, {
  providers: [
    provideZoneChangeDetection(),
    provideAnimations(),
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi()),
    provideNativeDateAdapter(),
    importProvidersFrom(ReactiveFormsModule, FormsModule),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
    {
      provide: ErrorHandler,
      useValue:
        environment.production && environment.enableErrorReporting
          ? Sentry.createErrorHandler({ showDialog: false })
          : new ErrorHandler(),
    },
  ],
}).catch(err => console.error(err));
