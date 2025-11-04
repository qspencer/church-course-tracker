import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable, catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Debug: Log the actual request URL and full details
    console.log('AuthInterceptor - Request URL:', req.url);
    console.log('AuthInterceptor - Full Request:', {
      url: req.url,
      method: req.method,
      headers: req.headers.keys(),
      withCredentials: req.withCredentials
    });
    if (!req.url.startsWith('https://')) {
      console.error('❌ AuthInterceptor - Request URL is NOT HTTPS!', req.url);
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
          if (error.status === 401) {
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
                // Refresh failed, logout user
                this.authService.logout();
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
