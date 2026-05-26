import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { BehaviorSubject, firstValueFrom, isObservable, Observable, of } from 'rxjs';
import { adminGuard } from './admin.guard';
import { AuthService } from '../services/auth.service';
import { User } from '../models';

describe('adminGuard', () => {
  let routerSpy: jasmine.SpyObj<Router>;
  let currentUserSubject: BehaviorSubject<User | null>;

  const mockAdminUser: User = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'Admin User',
    role: 'admin',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  };

  const mockStaffUser: User = { ...mockAdminUser, id: 2, role: 'staff' };
  const mockViewerUser: User = { ...mockAdminUser, id: 3, role: 'viewer' };

  beforeEach(() => {
    currentUserSubject = new BehaviorSubject<User | null>(null);
    const authServiceSpy = jasmine.createSpyObj('AuthService', [], {
      currentUser$: currentUserSubject.asObservable(),
    });
    const routerSpyObj = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpyObj },
      ],
    });

    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  function run(): Observable<boolean> {
    return TestBed.runInInjectionContext(
      () => adminGuard(null as never, null as never) as Observable<boolean>,
    );
  }

  it('allows admin', async () => {
    currentUserSubject.next(mockAdminUser);
    const result = run();
    expect(isObservable(result)).toBe(true);
    expect(await firstValueFrom(result)).toBe(true);
    expect(routerSpy.navigate).not.toHaveBeenCalled();
  });

  it('denies staff and redirects to /dashboard', async () => {
    currentUserSubject.next(mockStaffUser);
    expect(await firstValueFrom(run())).toBe(false);
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('denies viewer and redirects to /dashboard', async () => {
    currentUserSubject.next(mockViewerUser);
    expect(await firstValueFrom(run())).toBe(false);
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
  });

  it('denies unauthenticated and redirects to /auth', async () => {
    currentUserSubject.next(null);
    expect(await firstValueFrom(run())).toBe(false);
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/auth']);
  });
});
