import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { AdminGuard } from './admin.guard';
import { AuthService } from '../services/auth.service';
import { User } from '../models';
import { of } from 'rxjs';

describe('AdminGuard', () => {
  let guard: AdminGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  const mockAdminUser: User = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'Admin User',
    role: 'admin',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockStaffUser: User = {
    id: 2,
    username: 'staff',
    email: 'staff@example.com',
    full_name: 'Staff User',
    role: 'staff',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', [], {
      currentUser$: of(null)
    });
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AdminGuard,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });

    guard = TestBed.inject(AdminGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access for admin users', (done) => {
    // Mock admin user
    Object.defineProperty(authService, 'currentUser$', {
      value: of(mockAdminUser),
      writable: true
    });

    guard.canActivate().subscribe(result => {
      expect(result).toBe(true);
      expect(router.navigate).not.toHaveBeenCalled();
      done();
    });
  });

  it('should deny access for non-admin users and redirect to dashboard', (done) => {
    // Mock staff user
    Object.defineProperty(authService, 'currentUser$', {
      value: of(mockStaffUser),
      writable: true
    });

    guard.canActivate().subscribe(result => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
      done();
    });
  });

  it('should deny access for unauthenticated users and redirect to auth', (done) => {
    // Mock no user (null)
    Object.defineProperty(authService, 'currentUser$', {
      value: of(null),
      writable: true
    });

    guard.canActivate().subscribe(result => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/auth']);
      done();
    });
  });

  it('should deny access for viewer users and redirect to dashboard', (done) => {
    const mockViewerUser: User = {
      id: 3,
      username: 'viewer',
      email: 'viewer@example.com',
      full_name: 'Viewer User',
      role: 'viewer',
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    };

    // Mock viewer user
    Object.defineProperty(authService, 'currentUser$', {
      value: of(mockViewerUser),
      writable: true
    });

    guard.canActivate().subscribe(result => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
      done();
    });
  });
});
