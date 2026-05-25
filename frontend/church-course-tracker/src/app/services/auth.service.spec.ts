import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { HttpClient, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { LoggerService } from './logger.service';
import { LoginRequest, LoginResponse, User } from '../models';
import { environment } from '../../environments/environment';

const ROUTE_PREFIX = '';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let routerSpy: jasmine.SpyObj<Router>;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    role: 'staff',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockLoginResponse: LoginResponse = {
    access_token: 'mock-token',
    token_type: 'Bearer',
    user: mockUser
  };

  beforeEach(() => {
    const routerSpyObj = jasmine.createSpyObj('Router', ['navigate']);
    const loggerSpyObj = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug', 'setUser', 'clearUser']);

    TestBed.configureTestingModule({
    imports: [],
    providers: [
        AuthService,
        { provide: Router, useValue: routerSpyObj },
        { provide: LoggerService, useValue: loggerSpyObj },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
});

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should login user and store token', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      service.login(loginRequest).subscribe(response => {
        expect(response).toEqual(mockLoginResponse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(loginRequest);
      req.flush(mockLoginResponse);

      expect(service.getToken()).toBe('mock-token');
      expect(service.getCurrentUser()).toEqual(mockUser);
    });

    it('should update authentication state on successful login', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      let isAuthenticated = false;
      let currentUser = null;

      service.isAuthenticated$.subscribe(auth => isAuthenticated = auth);
      service.currentUser$.subscribe(user => currentUser = user as any);

      service.login(loginRequest).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush(mockLoginResponse);

      expect(isAuthenticated).toBe(true);
      expect(currentUser).toEqual(jasmine.any(Object));
    });
  });

  describe('logout', () => {
    beforeEach(() => {
      // Set up authenticated state
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('current_user', JSON.stringify(mockUser));
    });

    it('should clear authentication state and navigate to auth', () => {
      let isAuthenticated = true;
      let currentUser = mockUser;

      service.isAuthenticated$.subscribe(auth => isAuthenticated = auth);
      service.currentUser$.subscribe(user => currentUser = user as any);

      service.logout();

      expect(isAuthenticated).toBe(false);
      expect(currentUser).toBeNull();
      expect(service.getToken()).toBeNull();
      expect(service.getCurrentUser()).toBeNull();
      expect(routerSpy.navigate).toHaveBeenCalledWith([`${ROUTE_PREFIX}/auth`]);
    });
  });

  describe('register', () => {
    it('should register new user', () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        full_name: 'New User',
        password: 'password123'
      };

      service.register(userData).subscribe(user => {
        expect(user).toEqual(mockUser);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/register`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(userData);
      req.flush(mockUser);
    });
  });

  describe('token management', () => {
    it('should return null when no token exists', () => {
      expect(service.getToken()).toBeNull();
    });

    it('should return token when it exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(service.getToken()).toBe('test-token');
    });

    it('should detect authentication state from stored token', () => {
      localStorage.setItem('access_token', 'test-token');

      const newService = TestBed.runInInjectionContext(() => new AuthService());

      let isAuthenticated = false;
      newService.isAuthenticated$.subscribe(auth => isAuthenticated = auth);

      expect(isAuthenticated).toBe(true);
    });
  });

  describe('refreshToken', () => {
    it('should refresh token and update user data', (done) => {
      service.refreshToken().subscribe({
        next: (response) => {
          expect(response).toEqual(mockLoginResponse);
          expect(service.getToken()).toBe('mock-token');
          // The user should be set after the tap operator executes
          setTimeout(() => {
            expect(service.getCurrentUser()).toEqual(mockLoginResponse.user);
            done();
          }, 10);
        },
        error: (error) => {
          fail('Should not have errored: ' + error);
          done();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/refresh`);
      expect(req.request.method).toBe('POST');
      req.flush(mockLoginResponse);
    });
  });

  // Negative test cases
  describe('error handling', () => {
    it('should handle network errors during login', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.error(new ErrorEvent('Network error'));
    });

    it('should handle 401 Unauthorized during login', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'wrongpassword'
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush({ detail: 'Incorrect username or password' }, { status: 401, statusText: 'Unauthorized' });
    });

    it('should handle 400 Bad Request during login', () => {
      const loginRequest: LoginRequest = {
        username: '',
        password: ''
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush({ detail: 'Invalid request' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should handle timeout during login', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.error(new ErrorEvent('timeout'));
    });

    it('should handle network errors during register', () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        full_name: 'New User',
        password: 'password123'
      };

      service.register(userData).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/register`);
      req.error(new ErrorEvent('Network error'));
    });

    it('should handle 401 Unauthorized during token refresh', () => {
      service.refreshToken().subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/refresh`);
      req.flush({ detail: 'Invalid token' }, { status: 401, statusText: 'Unauthorized' });
    });

    it('should handle invalid token format', () => {
      localStorage.setItem('access_token', 'invalid.token.format');
      
      const token = service.getToken();
      expect(token).toBe('invalid.token.format');
      
      // Token validation would happen on the server
      // This test just verifies we can retrieve it
    });

    it('should handle expired token gracefully', () => {
      localStorage.setItem('access_token', 'expired.token.here');
      
      service.refreshToken().subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/refresh`);
      req.flush({ detail: 'Token expired' }, { status: 401, statusText: 'Unauthorized' });
    });
  });

  // Edge case tests
  describe('edge cases', () => {
    it('should handle empty username during login', () => {
      const loginRequest: LoginRequest = {
        username: '',
        password: 'password123'
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush({ detail: 'Username required' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should handle empty password during login', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: ''
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush({ detail: 'Password required' }, { status: 400, statusText: 'Bad Request' });
    });

    it('should handle very long username', () => {
      const loginRequest: LoginRequest = {
        username: 'a'.repeat(1000),
        password: 'password123'
      };

      service.login(loginRequest).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      expect(req.request.body.username.length).toBe(1000);
      req.flush(mockLoginResponse);
    });

    it('should handle special characters in username', () => {
      const loginRequest: LoginRequest = {
        username: "test@user#123!",
        password: 'password123'
      };

      service.login(loginRequest).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      expect(req.request.body.username).toBe("test@user#123!");
      req.flush(mockLoginResponse);
    });

    it('should handle unicode characters in username', () => {
      const loginRequest: LoginRequest = {
        username: "测试用户🎉",
        password: 'password123'
      };

      service.login(loginRequest).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      expect(req.request.body.username).toBe("测试用户🎉");
      req.flush(mockLoginResponse);
    });

    it('should handle malformed JSON response', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      service.login(loginRequest).subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      // Simulate malformed JSON by using error event or 500 error
      // Angular HTTP client will parse JSON and throw error if invalid
      req.flush('invalid json response', { 
        status: 500, 
        statusText: 'Internal Server Error',
        headers: { 'Content-Type': 'application/json' }
      });
    });

    it('should handle missing user in login response', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      service.login(loginRequest).subscribe({
        next: (response) => {
          // Should handle missing user gracefully
          expect(response).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush({ access_token: 'token', token_type: 'Bearer' }); // Missing user
    });

    it('should handle concurrent login attempts', () => {
      const loginRequest: LoginRequest = {
        username: 'testuser',
        password: 'password123'
      };

      // Simulate concurrent logins
      service.login(loginRequest).subscribe();
      service.login(loginRequest).subscribe();

      const requests = httpMock.match(`${environment.apiUrl}/auth/login`);
      expect(requests.length).toBe(2);
      requests.forEach(req => req.flush(mockLoginResponse));
    });

    it('should handle logout when not authenticated', () => {
      localStorage.clear();
      
      service.logout();
      
      expect(service.getToken()).toBeNull();
      expect(service.getCurrentUser()).toBeNull();
      expect(routerSpy.navigate).toHaveBeenCalledWith([`${ROUTE_PREFIX}/auth`]);
    });

    it('should handle token refresh when no token exists', () => {
      localStorage.clear();
      
      service.refreshToken().subscribe({
        next: () => fail('Should have errored'),
        error: (error) => {
          expect(error).toBeDefined();
        }
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/refresh`);
      req.flush({ detail: 'No token' }, { status: 401, statusText: 'Unauthorized' });
    });
  });
});
