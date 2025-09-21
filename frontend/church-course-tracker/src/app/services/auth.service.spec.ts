import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { LoginRequest, LoginResponse, User } from '../models';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let routerSpy: jasmine.SpyObj<Router>;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    is_active: true,
    is_superuser: false,
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

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AuthService,
        { provide: Router, useValue: routerSpyObj }
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
      service.currentUser$.subscribe(user => currentUser = user);

      service.login(loginRequest).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      req.flush(mockLoginResponse);

      expect(isAuthenticated).toBe(true);
      expect(currentUser).toEqual(mockUser);
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
      service.currentUser$.subscribe(user => currentUser = user);

      service.logout();

      expect(isAuthenticated).toBe(false);
      expect(currentUser).toBeNull();
      expect(service.getToken()).toBeNull();
      expect(service.getCurrentUser()).toBeNull();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/auth']);
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
      
      const newService = new AuthService(TestBed.inject(HttpClientTestingModule), routerSpy);
      
      let isAuthenticated = false;
      newService.isAuthenticated$.subscribe(auth => isAuthenticated = auth);
      
      expect(isAuthenticated).toBe(true);
    });
  });

  describe('refreshToken', () => {
    it('should refresh token and update user data', () => {
      service.refreshToken().subscribe(response => {
        expect(response).toEqual(mockLoginResponse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/refresh`);
      expect(req.request.method).toBe('POST');
      req.flush(mockLoginResponse);

      expect(service.getToken()).toBe('mock-token');
      expect(service.getCurrentUser()).toEqual(mockUser);
    });
  });
});
