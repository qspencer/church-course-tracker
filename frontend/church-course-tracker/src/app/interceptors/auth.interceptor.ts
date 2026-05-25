import { Injectable, isDevMode, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { LoggerService } from '../services/logger.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private authService = inject(AuthService);
  private logger = inject(LoggerService);


  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Log HTTPS warnings in development mode
    if (isDevMode()) {
      // Check both base URL and full URL with params
      // Note: In local development, HTTP is expected
      if (!req.url.startsWith('https://') && !req.url.includes('localhost')) {
        this.logger.warn('AuthInterceptor - Request URL is NOT HTTPS!', { url: req.url });
      }
    }
    
    const token = this.authService.getToken();
    
    if (token) {
      // Token is present and will be added to request
      // No need to log this for every request
      
      const authReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
      
      return next.handle(authReq).pipe(
        catchError(error => {
          // Don't try to refresh if this is already a refresh request - prevents infinite loop
          if (error.status === 401 && !req.url.includes('/auth/refresh')) {
            // Token might be expired, try to refresh
            return this.authService.refreshToken().pipe(
              switchMap(() => {
                const newToken = this.authService.getToken();
                if (!newToken) {
                  // No token after refresh, logout
                  this.authService.logout();
                  return throwError(() => new Error('Authentication failed. Please log in again.'));
                }
                const retryReq = authReq.clone({
                  setHeaders: {
                    Authorization: `Bearer ${newToken}`
                  }
                });
                return next.handle(retryReq);
              }),
              catchError(refreshError => {
                // Refresh failed with 401 - token is invalid/expired
                // Logout user immediately and don't retry the original request
                this.logger.error('Token refresh failed, logging out user', refreshError);
                this.authService.logout();
                // Return the original error, not the refresh error, so components see the right error
                return throwError(() => ({
                  ...error,
                  message: 'Your session has expired. Please log in again.',
                  status: 401,
                  statusText: 'Unauthorized'
                }));
              })
            );
          }
          return throwError(() => error);
        })
      );
    }
    
    return next.handle(req);
  }
}
