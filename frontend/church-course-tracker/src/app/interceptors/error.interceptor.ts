import { Injectable, isDevMode } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoggerService } from '../services/logger.service';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  constructor(
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Log HTTPS warnings in development mode
    if (isDevMode()) {
      if (!req.url.startsWith('https://') && !req.url.includes('localhost')) {
        this.logger.warn('ErrorInterceptor - Request URL is NOT HTTPS!', { url: req.url });
      }
    }
    
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An unexpected error occurred';
        
        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = error.error.message || 'A network error occurred';
        } else {
          // Server-side error
          // Try to extract detailed error message
          if (error.error) {
            if (typeof error.error === 'string') {
              errorMessage = error.error;
            } else if (error.error.detail) {
              errorMessage = error.error.detail;
            } else if (error.error.message) {
              errorMessage = error.error.message;
            } else if (error.error.error) {
              errorMessage = error.error.error;
            }
          }
          
          // If no detailed message, use status-based messages
          if (errorMessage === 'An unexpected error occurred') {
            switch (error.status) {
              case 0:
                // Status 0 typically means connection blocked (CORS, mixed content, network error)
                if (req.url && req.url.startsWith('http://')) {
                  errorMessage = 'Mixed content blocked: The page is trying to use insecure HTTP. Please clear your browser cache and refresh.';
                } else {
                  errorMessage = 'Unable to connect to the server. Please check your internet connection.';
                }
                break;
              case 400:
                errorMessage = 'Bad request. Please check your input.';
                break;
              case 401:
                errorMessage = 'Unauthorized. Please log in again.';
                break;
              case 403:
                errorMessage = 'Access forbidden. You don\'t have permission to perform this action.';
                break;
              case 404:
                errorMessage = 'Resource not found.';
                break;
              case 500:
                errorMessage = 'Internal server error. Please try again later.';
                break;
              case 503:
                errorMessage = 'Service temporarily unavailable. Please try again later.';
                break;
              default:
                errorMessage = `Error ${error.status}: ${error.statusText || 'An unexpected error occurred'}`;
            }
          }
        }

        // Don't show error message for 401 errors on auth endpoints (handled by auth component)
        // But show for other 401 errors (e.g., expired tokens on protected routes)
        const isAuthEndpoint = req.url.includes('/auth/login') || req.url.includes('/auth/register');
        
        // Don't show snackbar if error is already handled by component (components will show their own messages)
        // This prevents duplicate error messages and potential infinite loops
        const isHandledByComponent = req.url.includes('/courses') && (req.method === 'POST' || req.method === 'PUT');
        
        if ((error.status !== 401 || !isAuthEndpoint) && !isHandledByComponent) {
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: error.status >= 400 ? ['error-snackbar'] : []
          });
        }

        return throwError(() => error);
      })
    );
  }
}
