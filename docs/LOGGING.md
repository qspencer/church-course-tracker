# Logging and Error Tracking Guide

This document describes the logging infrastructure and best practices for the Church Course Tracker application.

## Table of Contents

- [Overview](#overview)
- [LoggerService](#loggerservice)
- [Sentry Integration](#sentry-integration)
- [Log Levels](#log-levels)
- [Context and Metadata](#context-and-metadata)
- [User Context Tracking](#user-context-tracking)
- [Production Debugging](#production-debugging)
- [Configuration](#configuration)

---

## Overview

The application uses a centralized logging approach:

- **Frontend**: LoggerService with Sentry integration
- **Backend**: Python logging with structured output
- **Production**: Sentry for error tracking and monitoring

### Why Centralized Logging?

- Consistent error tracking across the application
- Structured context for debugging
- Production error monitoring without exposing details to users
- User context for reproducing issues
- Performance monitoring and tracing

---

## LoggerService

Located at `frontend/church-course-tracker/src/app/services/logger.service.ts`, the LoggerService provides a unified logging interface.

### Basic Usage

```typescript
import { LoggerService } from './services/logger.service';

constructor(private logger: LoggerService) {}

performAction(): void {
  this.service.doSomething().subscribe({
    next: (result) => this.handleSuccess(result),
    error: (error) => {
      this.logger.error('Action failed', error, {
        component: 'ComponentName',
        action: 'performAction',
        userId: this.currentUserId
      });
      this.snackBar.open('Action failed', 'Close', { duration: 5000 });
    }
  });
}
```

### Available Methods

#### error()
Logs errors with full stack traces. Always use for exceptions and failures.

```typescript
this.logger.error(message: string, error?: any, context?: LogContext): void
```

**Example:**
```typescript
this.logger.error('Failed to load data', error, {
  component: 'DashboardComponent',
  action: 'loadData',
  userId: this.currentUser?.id
});
```

#### warn()
Logs warnings for unexpected but non-critical situations.

```typescript
this.logger.warn(message: string, context?: LogContext): void
```

**Example:**
```typescript
this.logger.warn('User preference not found, using default', {
  component: 'SettingsComponent',
  userId: this.currentUser?.id,
  preferenceKey: 'theme'
});
```

#### info()
Logs informational messages (typically for debugging).

```typescript
this.logger.info(message: string, context?: LogContext): void
```

**Example:**
```typescript
this.logger.info('Sync completed successfully', {
  component: 'SyncComponent',
  recordsProcessed: 150,
  duration: 2500
});
```

#### debug()
Logs detailed debugging information (only in development).

```typescript
this.logger.debug(message: string, data?: any): void
```

**Example:**
```typescript
this.logger.debug('API response', { response, headers });
```

---

## Sentry Integration

### What is Sentry?

Sentry is a production error tracking service that captures:
- Errors and exceptions with full stack traces
- User context (who experienced the error)
- Breadcrumbs (events leading up to the error)
- Performance metrics
- Release tracking

### Setup

#### 1. Create Sentry Account

1. Visit https://sentry.io/signup/
2. Create new organization
3. Create new project: "Church Course Tracker"
4. Select platform: "Angular"
5. Copy DSN (Data Source Name)

#### 2. Install SDK

```bash
cd frontend/church-course-tracker
npm install --save @sentry/angular @sentry/tracing
```

#### 3. Configure Environment

**Development** (`environment.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  enableErrorReporting: false,  // Disabled in dev
  sentry: {
    dsn: '',  // Empty in dev
    environment: 'development'
  }
};
```

**Production** (`environment.prod.ts`):
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.quentinspencer.com/api/v1',
  enableErrorReporting: true,  // Enabled in production
  sentry: {
    dsn: 'YOUR_SENTRY_DSN_HERE',
    environment: 'production',
    tracesSampleRate: 0.1,  // Sample 10% of transactions
    tracePropagationTargets: ['localhost', 'api.quentinspencer.com']
  }
};
```

#### 4. Initialize in main.ts

```typescript
import * as Sentry from '@sentry/angular';
import { environment } from './environments/environment';

if (environment.production && environment.enableErrorReporting) {
  Sentry.init({
    dsn: environment.sentry.dsn,
    environment: environment.sentry.environment,
    integrations: [
      new Sentry.BrowserTracing({
        tracePropagationTargets: environment.sentry.tracePropagationTargets,
        routingInstrumentation: Sentry.routingInstrumentation,
      }),
    ],
    tracesSampleRate: environment.sentry.tracesSampleRate,
    beforeSend(event) {
      // Filter sensitive data
      if (event.request?.headers) {
        delete event.request.headers['Authorization'];
      }
      return event;
    },
  });
}
```

#### 5. Register Error Handler

**File**: `app.module.ts`
```typescript
import { ErrorHandler } from '@angular/core';
import * as Sentry from '@sentry/angular';
import { environment } from '../environments/environment';

@NgModule({
  providers: [
    {
      provide: ErrorHandler,
      useValue: environment.production && environment.enableErrorReporting
        ? Sentry.createErrorHandler({ showDialog: false })
        : new ErrorHandler(),
    },
  ],
})
export class AppModule {}
```

### Testing Sentry

To verify Sentry is working:

```typescript
// In any component
testSentry(): void {
  try {
    throw new Error('Test Sentry error');
  } catch (error) {
    this.logger.error('Test error', error, {
      component: 'TestComponent',
      action: 'testSentry'
    });
  }
}
```

Check the Sentry dashboard - you should see the error with full context.

---

## Log Levels

### When to Use Each Level

| Level | Purpose | Examples | Production? |
|-------|---------|----------|-------------|
| **error** | Exceptions, failures, data loss | API errors, validation failures, sync failures | ✅ Yes |
| **warn** | Unexpected but non-critical | Missing preferences, deprecated features | ✅ Yes |
| **info** | Important business events | Successful operations, audit events | ❌ No (dev only) |
| **debug** | Detailed debugging data | API responses, state changes | ❌ No (dev only) |

### Examples by Level

#### error - Critical Issues
```typescript
// API failure
this.logger.error('Failed to save course', error, {
  component: 'CourseDialogComponent',
  action: 'save',
  courseId: this.course?.id
});

// Validation failure
this.logger.error('Invalid form data', null, {
  component: 'EnrollmentDialog',
  action: 'submit',
  validationErrors: this.form.errors
});

// Sync failure
this.logger.error('Planning Center sync failed', error, {
  component: 'SyncComponent',
  syncType: 'people',
  recordsProcessed: count
});
```

#### warn - Unexpected Situations
```typescript
// Missing data (non-critical)
this.logger.warn('User preference not found', {
  component: 'SettingsComponent',
  preferenceKey: 'defaultView',
  userId: this.currentUser.id
});

// Deprecated feature usage
this.logger.warn('Using deprecated API endpoint', {
  component: 'LegacyComponent',
  endpoint: '/api/v1/old-endpoint'
});

// Rate limit approaching
this.logger.warn('API rate limit at 80%', {
  component: 'PlanningCenterService',
  remaining: 200,
  limit: 1000
});
```

#### info - Business Events (Development Only)
```typescript
// Successful operations
this.logger.info('Course created successfully', {
  component: 'CourseDialog',
  courseId: result.id,
  courseName: result.name
});

// Sync completion
this.logger.info('Sync completed', {
  component: 'SyncComponent',
  recordsProcessed: 150,
  duration: 2500
});
```

#### debug - Detailed Data (Development Only)
```typescript
// API responses
this.logger.debug('API response received', {
  endpoint: '/api/v1/courses',
  data: response
});

// State changes
this.logger.debug('Form state changed', {
  valid: this.form.valid,
  values: this.form.value
});
```

---

## Context and Metadata

### LogContext Interface

```typescript
export interface LogContext {
  component?: string;    // Component name (required)
  action?: string;       // Method/action name
  userId?: number;       // Current user ID
  [key: string]: any;    // Additional context
}
```

### Best Practices for Context

#### Always Include Component Name
```typescript
this.logger.error('Operation failed', error, {
  component: 'CourseDialogComponent',  // ✅ Always include
  action: 'save'
});
```

#### Include Relevant IDs
```typescript
this.logger.error('Failed to update participant', error, {
  component: 'ParticipantDialog',
  action: 'onSubmit-update',
  participantId: this.data.participant?.id,
  programId: this.program.id,
  userId: this.currentUser?.id
});
```

#### Add Contextual Data
```typescript
this.logger.error('Import failed', error, {
  component: 'EventRegistrationsDialog',
  action: 'importBulk',
  eventId: this.eventId,
  registrationCount: this.selectedRegistrations.size,
  courseId: this.courseId
});
```

### Context Examples by Component Type

#### Service Methods
```typescript
// In services
this.logger.error('API request failed', error, {
  component: 'ProgramService',
  action: 'getProgramById',
  programId: id,
  endpoint: `/programs/${id}`
});
```

#### Dialog Components
```typescript
// In dialogs
this.logger.error('Save failed', error, {
  component: 'UserDialogComponent',
  action: 'onSubmit',
  isEditing: this.isEditing,
  userId: this.data.user?.id
});
```

#### List Components
```typescript
// In list/table components
this.logger.error('Load failed', error, {
  component: 'CoursesComponent',
  action: 'loadCourses',
  page: this.currentPage,
  pageSize: this.pageSize,
  filters: this.appliedFilters
});
```

---

## User Context Tracking

### Setting User Context

User context is automatically set on login and cleared on logout.

**File**: `auth.service.ts`
```typescript
import { LoggerService } from './logger.service';

constructor(private logger: LoggerService) {}

login(username: string, password: string): Observable<any> {
  return this.http.post(`${this.apiUrl}/auth/login`, { username, password })
    .pipe(
      tap((response: any) => {
        // Set authentication...

        // Set user context for error tracking
        this.logger.setUser(
          response.user.id,
          response.user.username,
          response.user.email
        );
      })
    );
}

logout(): void {
  this.logger.clearUser();
  // Clear authentication...
}
```

### What User Context Provides

When an error occurs, Sentry automatically includes:
- User ID
- Username
- Email address
- IP address
- Last active time

This allows you to:
- Contact users who experienced errors
- Reproduce issues with specific user accounts
- Identify patterns (e.g., errors only for certain users)

---

## Production Debugging

### Viewing Errors in Sentry

1. **Dashboard**: https://sentry.io/organizations/YOUR_ORG/issues/
2. **Filter by**:
   - Environment (production, staging)
   - Release version
   - User
   - Component (via tags)
   - Time range

### Understanding Error Details

Each error in Sentry includes:

#### 1. Exception Details
- Error message
- Full stack trace
- Source map support (shows original TypeScript)

#### 2. User Context
```json
{
  "id": "123",
  "username": "john.doe",
  "email": "john@example.com",
  "ip_address": "192.168.1.1"
}
```

#### 3. Tags
```json
{
  "component": "CourseDialogComponent",
  "environment": "production",
  "release": "1.2.3"
}
```

#### 4. Extra Context
```json
{
  "action": "save",
  "courseId": 456,
  "userId": 123,
  "message": "Failed to save course"
}
```

#### 5. Breadcrumbs
```
10:15:23 - Navigation to /courses
10:15:25 - Clicked "Add Course"
10:15:28 - Form validation passed
10:15:30 - API request to POST /api/v1/courses
10:15:31 - Error: 500 Internal Server Error
```

### Debugging Common Issues

#### API Errors
1. Check error message and status code
2. Review user context - can you reproduce with their account?
3. Check backend logs for corresponding request
4. Review API endpoint implementation

#### UI Errors
1. Check browser and OS from user context
2. Review breadcrumbs for user actions leading to error
3. Check for environment-specific issues (production vs dev)
4. Verify source maps are working (TypeScript line numbers shown)

#### Sync Errors
1. Check Planning Center API status
2. Review sync logs in backend
3. Check for rate limiting (429 errors)
4. Verify authentication credentials

---

## Configuration

### Environment Variables

**Development**:
```typescript
enableErrorReporting: false  // Console logging only
```

**Production**:
```typescript
enableErrorReporting: true   // Sentry + console logging
```

### Sentry Configuration Options

#### tracesSampleRate
Controls performance monitoring sample rate:
```typescript
tracesSampleRate: 0.1  // Sample 10% of transactions
```

- Lower = less overhead, less data
- Higher = more visibility, more cost
- Recommended: 0.1 (10%) for production

#### beforeSend
Filter sensitive data before sending to Sentry:
```typescript
beforeSend(event) {
  // Remove sensitive headers
  if (event.request?.headers) {
    delete event.request.headers['Authorization'];
    delete event.request.headers['Cookie'];
  }

  // Filter sensitive URLs
  if (event.request?.url?.includes('/auth/')) {
    delete event.request.data;
  }

  return event;
}
```

#### ignoreErrors
Ignore specific errors:
```typescript
ignoreErrors: [
  'Non-Error exception captured',  // Ignore non-Error objects
  'ResizeObserver loop limit exceeded',  // Browser quirk
  /^Cannot read property .* of undefined$/  // Common benign error
]
```

### Backend Logging Configuration

**File**: `backend/app/core/config.py`
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Set third-party log levels
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
```

---

## Best Practices Summary

### Frontend

✅ **Do:**
- Use LoggerService for all error logging
- Always include component name in context
- Add relevant IDs (userId, courseId, etc.)
- Show user-friendly messages via snackBar
- Use finalize() to ensure cleanup
- Set user context on login
- Test Sentry integration before deploying

❌ **Don't:**
- Use console.log/console.error in production
- Log sensitive data (passwords, tokens)
- Show technical errors to users
- Skip component context
- Forget to clear user context on logout

### Backend

✅ **Do:**
- Use structured logging (logger.error with context)
- Log with exc_info=True for exceptions
- Include request IDs for tracing
- Use appropriate log levels
- Rotate log files
- Monitor log volume

❌ **Don't:**
- Log sensitive data (passwords, tokens)
- Use print() statements
- Log excessive DEBUG information in production
- Ignore exceptions silently
- Mix log levels (e.g., logging errors as warnings)

---

## Testing

### Unit Tests

Test that errors are logged correctly:

```typescript
describe('ComponentName', () => {
  let logger: jasmine.SpyObj<LoggerService>;

  beforeEach(() => {
    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn']);
    TestBed.configureTestingModule({
      providers: [{ provide: LoggerService, useValue: loggerSpy }]
    });
    logger = TestBed.inject(LoggerService) as jasmine.SpyObj<LoggerService>;
  });

  it('should log errors with component context', () => {
    component.performAction();

    expect(logger.error).toHaveBeenCalledWith(
      'Action failed',
      jasmine.any(Error),
      jasmine.objectContaining({
        component: 'ComponentName',
        action: 'performAction'
      })
    );
  });

  it('should log warnings with context', () => {
    component.checkPreferences();

    expect(logger.warn).toHaveBeenCalledWith(
      'Preference not found',
      jasmine.objectContaining({
        component: 'ComponentName',
        preferenceKey: 'theme'
      })
    );
  });
});
```

### Integration Tests

Verify Sentry integration:

```typescript
it('should send error to Sentry in production', () => {
  // Mock environment
  spyOnProperty(environment, 'production').and.returnValue(true);
  spyOnProperty(environment, 'enableErrorReporting').and.returnValue(true);

  spyOn(Sentry, 'captureException');

  // Trigger error
  logger.error('Test error', new Error('Test'), { component: 'Test' });

  expect(Sentry.captureException).toHaveBeenCalled();
});
```

---

## Troubleshooting

### Sentry Not Receiving Errors

1. **Check environment configuration**:
   - Verify `enableErrorReporting: true` in production
   - Verify DSN is correct
   - Check network requests (should see POST to sentry.io)

2. **Check beforeSend filter**:
   - Ensure you're not filtering out all errors
   - Test with simple error

3. **Check initialization**:
   - Verify Sentry.init() runs before app bootstrap
   - Check browser console for Sentry errors

### Source Maps Not Working

1. **Enable source maps in production**:
   ```json
   // angular.json
   "production": {
     "sourceMap": true
   }
   ```

2. **Upload source maps to Sentry**:
   ```bash
   npm install --save-dev @sentry/webpack-plugin
   ```

### Too Many Errors

1. **Add ignoreErrors configuration**:
   - Filter benign errors
   - Use regex patterns

2. **Sample error rate**:
   ```typescript
   sampleRate: 0.5  // Only send 50% of errors
   ```

---

## Additional Resources

- [Sentry Angular Documentation](https://docs.sentry.io/platforms/javascript/guides/angular/)
- [Sentry Best Practices](https://docs.sentry.io/product/best-practices/)
- [Error Handling Guide](./ERROR_HANDLING.md)
- [Frontend LoggerService](../frontend/church-course-tracker/src/app/services/logger.service.ts)
