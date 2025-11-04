import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // CRITICAL: Log the FULL URL including query parameters
    const fullUrl = req.urlWithParams || req.url;
    console.log('AuthInterceptor - Request URL (base):', req.url);
    console.log('AuthInterceptor - Request URL (with params):', fullUrl);
    console.log('AuthInterceptor - Full Request:', {
      url: req.url,
      urlWithParams: req.urlWithParams,
      method: req.method,
      headers: req.headers.keys(),
      withCredentials: req.withCredentials
    });
    
    // Check both base URL and full URL with params
    if (!req.url.startsWith('https://')) {
      console.error('❌ AuthInterceptor - Request URL is NOT HTTPS!', req.url);
    }
    if (fullUrl && !fullUrl.startsWith('https://')) {
      console.error('❌ AuthInterceptor - Full URL with params is NOT HTTPS!', fullUrl);
    }
    
    // Force absolute URL if it's not already
    let requestUrl = req.url;
    if (!requestUrl.startsWith('http://') && !requestUrl.startsWith('https://')) {
      console.warn('⚠️ Relative URL detected, should be absolute:', requestUrl);
    }
    
    const token = this.authService.getToken();
    
    if (token) {
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
                const retryReq = authReq.clone({
                  setHeaders: {
                    Authorization: `Bearer ${newToken}`
                  }
                });
                return next.handle(retryReq);
              }),
              catchError(refreshError => {
                // Refresh failed with 401 - token is invalid/expired
                // Logout user and redirect to login
                console.error('Token refresh failed, logging out user:', refreshError);
                if (refreshError.status === 401) {
                  this.authService.logout();
                }
                return throwError(() => refreshError);
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
