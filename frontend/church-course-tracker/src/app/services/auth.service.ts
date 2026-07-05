import { Injectable, isDevMode, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, finalize, shareReplay } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { User, LoginRequest, LoginResponse, UserCreate } from '../models';
import { LoggerService } from './logger.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private logger = inject(LoggerService);

  private readonly API_URL = environment.apiUrl;
  private readonly TOKEN_KEY = 'access_token';
  private readonly USER_KEY = 'current_user';

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  private currentUserSubject = new BehaviorSubject<User | null>(this.getCurrentUserFromStorage());

  // Shared in-flight refresh: when several requests 401 at once they all
  // subscribe to the same /auth/refresh call instead of each firing their
  // own (which raced and could clobber a just-refreshed token).
  private refresh$: Observable<LoginResponse> | null = null;

  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();
  public currentUser$ = this.currentUserSubject.asObservable();

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/auth/login`, credentials)
      .pipe(
        tap(response => {
          this.setToken(response.access_token);

          // Handle missing user gracefully (should not happen in normal flow)
          if (response.user) {
            this.setCurrentUser(response.user);
            this.isAuthenticatedSubject.next(true);
            this.currentUserSubject.next(response.user);

            // Set user context for error tracking
            this.logger.setUser(
              response.user.id,
              response.user.username || 'unknown',
              response.user.email
            );
          } else {
            // User data missing - set minimal authenticated state
            this.isAuthenticatedSubject.next(true);
            this.currentUserSubject.next(null);
            this.logger.warn('Login response missing user data');
          }
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.isAuthenticatedSubject.next(false);
    this.currentUserSubject.next(null);

    // Clear user context from error tracking
    this.logger.clearUser();

    this.router.navigate(['/auth']);
  }

  register(userData: UserCreate): Observable<User> {
    return this.http.post<User>(`${this.API_URL}/auth/register`, userData);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }

  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  hasAnyRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }

  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  private setCurrentUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.currentUserSubject.next(user);
  }

  private getCurrentUserFromStorage(): User | null {
    const userJson = localStorage.getItem(this.USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
  }

  refreshToken(): Observable<LoginResponse> {
    // Coalesce concurrent callers onto one request.
    if (this.refresh$) {
      return this.refresh$;
    }

    this.refresh$ = this.http.post<LoginResponse>(`${this.API_URL}/auth/refresh`, {}).pipe(
      tap({
        next: (response) => {
          this.setToken(response.access_token);
          if (response.user) {
            this.setCurrentUser(response.user);
            this.isAuthenticatedSubject.next(true);
            this.currentUserSubject.next(response.user);
          }
        },
        error: (error) => {
          // If refresh fails with 401, the token is invalid/expired
          // Logout will be handled by the interceptor
          this.logger.error('Token refresh failed', error);
          if (error.status === 401) {
            // Token is invalid, clear everything and logout
            this.logout();
          }
        }
      }),
      // Reset once the shared call settles so the next 401 starts fresh.
      finalize(() => { this.refresh$ = null; }),
      // Replay the single result/error to every concurrent subscriber.
      shareReplay(1)
    );
    return this.refresh$;
  }
}
