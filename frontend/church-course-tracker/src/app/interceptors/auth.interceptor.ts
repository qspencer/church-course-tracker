import { Injectable, isDevMode } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Only log in development mode - NEVER log tokens or sensitive data in production
    if (isDevMode()) {
      const fullUrl = req.urlWithParams || req.url;
      console.log('AuthInterceptor - Request URL (base):', req.url);
      console.log('AuthInterceptor - Request URL (with params):', fullUrl);
      
      // Check both base URL and full URL with params
      // Note: In local development, HTTP is expected
      if (!req.url.startsWith('https://') && !req.url.includes('localhost')) {
        console.error('❌ AuthInterceptor - Request URL is NOT HTTPS!', req.url);
      }
      if (fullUrl && !fullUrl.startsWith('https://') && !fullUrl.includes('localhost')) {
        console.error('❌ AuthInterceptor - Full URL with params is NOT HTTPS!', fullUrl);
      }
      
      // Force absolute URL if it's not already
      let requestUrl = req.url;
      if (!requestUrl.startsWith('http://') && !requestUrl.startsWith('https://')) {
        console.warn('⚠️ Relative URL detected, should be absolute:', requestUrl);
      }
    }
    
    const token = this.authService.getToken();
    
    if (token) {
      // NEVER log tokens in production - this is a security risk
      // Only log in development mode, and even then, be careful
      if (isDevMode()) {
        console.log('AuthInterceptor - Token present (length:', token.length + ')');
      }
      
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
                if (isDevMode()) {
                  console.error('Token refresh failed, logging out user:', refreshError);
                }
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
