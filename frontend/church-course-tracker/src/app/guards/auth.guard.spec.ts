import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { BehaviorSubject, firstValueFrom, isObservable } from 'rxjs';
import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

describe('authGuard', () => {
  let routerSpy: jasmine.SpyObj<Router>;
  let isAuthenticatedSubject: BehaviorSubject<boolean>;

  beforeEach(() => {
    isAuthenticatedSubject = new BehaviorSubject<boolean>(true);
    const authSpy = jasmine.createSpyObj('AuthService', [], {
      isAuthenticated$: isAuthenticatedSubject.asObservable(),
    });
    const routerSpyObj = jasmine.createSpyObj('Router', ['createUrlTree']);

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authSpy },
        { provide: Router, useValue: routerSpyObj },
      ],
    });

    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  function run(): unknown {
    return TestBed.runInInjectionContext(() => authGuard(null as never, null as never));
  }

  it('allows access when authenticated', async () => {
    isAuthenticatedSubject.next(true);
    const result = run();
    expect(isObservable(result)).toBe(true);
    expect(await firstValueFrom(result as never)).toBe(true);
  });

  it('redirects to /auth when not authenticated', async () => {
    const urlTree = {} as UrlTree;
    routerSpy.createUrlTree.and.returnValue(urlTree);
    isAuthenticatedSubject.next(false);

    const result = run();
    expect(await firstValueFrom(result as never)).toBe(urlTree);
    expect(routerSpy.createUrlTree).toHaveBeenCalledWith(['/auth']);
  });
});
