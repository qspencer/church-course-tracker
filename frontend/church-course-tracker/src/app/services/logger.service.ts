import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import * as Sentry from '@sentry/angular';

/**
 * Context information for logging
 */
export interface LogContext {
  component?: string;
  action?: string;
  userId?: number;
  [key: string]: any;
}

/**
 * Centralized logging service with Sentry integration
 * Replaces console.* statements with environment-aware logging
 */
@Injectable({
  providedIn: 'root'
})
export class LoggerService {

  /**
   * General log message
   */
  log(message: string, context?: LogContext): void {
    if (!environment.production) {
      console.log(`[LOG] ${message}`, context || '');
    }
  }

  /**
   * Info message - sent to Sentry in production
   */
  info(message: string, context?: LogContext): void {
    if (!environment.production) {
      console.info(`[INFO] ${message}`, context || '');
    }

    if (environment.production && environment.enableErrorReporting) {
      Sentry.captureMessage(message, {
        level: 'info',
        tags: context ? { component: context.component } : undefined,
        extra: context,
      });
    }
  }

  /**
   * Warning message - sent to Sentry in production
   */
  warn(message: string, context?: LogContext): void {
    if (!environment.production) {
      console.warn(`[WARN] ${message}`, context || '');
    }

    if (environment.production && environment.enableErrorReporting) {
      Sentry.captureMessage(message, {
        level: 'warning',
        tags: context ? { component: context.component } : undefined,
        extra: context,
      });
    }
  }

  /**
   * Error message - sent to Sentry in production
   */
  error(message: string, error?: any, context?: LogContext): void {
    if (!environment.production) {
      console.error(`[ERROR] ${message}`, error, context || '');
    }

    if (environment.production && environment.enableErrorReporting) {
      Sentry.captureException(error || new Error(message), {
        tags: {
          component: context?.component || 'unknown',
        },
        extra: {
          message,
          ...context,
        },
        level: 'error',
      });
    }
  }

  /**
   * Debug message - only in development
   */
  debug(message: string, context?: LogContext): void {
    if (!environment.production) {
      console.debug(`[DEBUG] ${message}`, context || '');
    }
  }

  /**
   * Set user context for error tracking
   * Should be called after successful login
   */
  setUser(userId: number, username: string, email?: string): void {
    if (environment.production && environment.enableErrorReporting) {
      Sentry.setUser({
        id: userId.toString(),
        username,
        email,
      });
    }
  }

  /**
   * Clear user context
   * Should be called on logout
   */
  clearUser(): void {
    if (environment.production && environment.enableErrorReporting) {
      Sentry.setUser(null);
    }
  }

  /**
   * Add breadcrumb for tracking user actions
   * Useful for debugging context around errors
   */
  addBreadcrumb(message: string, category: string, data?: any): void {
    if (environment.production && environment.enableErrorReporting) {
      Sentry.addBreadcrumb({
        message,
        category,
        data,
        level: 'info',
      });
    }
  }
}
