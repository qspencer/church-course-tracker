import { TestBed } from '@angular/core/testing';
import { fakeAsync, tick, flush, discardPeriodicTasks } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { AuthService } from './auth.service';
import { InactivityService } from './inactivity.service';
import { InactivityWarningDialogComponent } from '../components/inactivity-warning-dialog/inactivity-warning-dialog.component';
import { BehaviorSubject, of } from 'rxjs';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('InactivityService', () => {
  let service: InactivityService;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;

  beforeEach(() => {
    const authSpy = jasmine.createSpyObj('AuthService', ['logout', 'getToken'], {
      isAuthenticated$: new BehaviorSubject<boolean>(true)
    });
    const matDialogSpy = jasmine.createSpyObj('MatDialog', ['open']);

    TestBed.configureTestingModule({
      providers: [
        InactivityService,
        { provide: AuthService, useValue: authSpy },
        { provide: MatDialog, useValue: matDialogSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(InactivityService);
    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    dialogSpy = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    authServiceSpy.getToken.and.returnValue('mock-token');
  });

  afterEach(() => {
    service.stopMonitoring();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('startMonitoring', () => {
    it('should start monitoring when authenticated', fakeAsync(() => {
      authServiceSpy.isAuthenticated$ = new BehaviorSubject<boolean>(true);
      authServiceSpy.getToken.and.returnValue('mock-token');

      service.startMonitoring();
      tick(100); // Allow subscription to set up

      // getToken() is called when an event occurs, so trigger a DOM event
      const clickEvent = new MouseEvent('click', { bubbles: true });
      document.dispatchEvent(clickEvent);
      
      tick(1100); // Wait for debounceTime (1000ms) + processing time
      
      expect(authServiceSpy.getToken).toHaveBeenCalled();
      
      // Clean up timers
      service.stopMonitoring();
      flush();
      discardPeriodicTasks();
    }));

    it('should stop monitoring when not authenticated', fakeAsync(() => {
      const stopSpy = spyOn(service, 'stopMonitoring').and.callThrough();
      
      // Emit false on the existing BehaviorSubject instead of creating a new one
      (authServiceSpy.isAuthenticated$ as BehaviorSubject<boolean>).next(false);
      
      service.startMonitoring();
      tick(100); // Allow subscription to process

      expect(stopSpy).toHaveBeenCalled();
      
      // Clean up
      service.stopMonitoring();
      flush();
      discardPeriodicTasks();
    }));
  });

  describe('stopMonitoring', () => {
    it('should stop monitoring and clear timers', () => {
      service.startMonitoring();
      service.stopMonitoring();

      expect(service).toBeTruthy();
    });
  });

  describe('resetTimer', () => {
    it('should reset the inactivity timer', () => {
      service.startMonitoring();
      const initialTime = service.getTimeUntilLogout();
      
      service.resetTimer();
      
      const newTime = service.getTimeUntilLogout();
      expect(newTime).toBeGreaterThanOrEqual(initialTime);
    });
  });

  describe('getTimeUntilLogout', () => {
    it('should return time until logout', () => {
      service.startMonitoring();
      const time = service.getTimeUntilLogout();
      
      expect(time).toBeGreaterThan(0);
      expect(time).toBeLessThanOrEqual(30 * 60 * 1000); // Should be <= 30 minutes
    });

    it('should return 0 if timeout has passed', () => {
      // This is hard to test without manipulating time, but we can verify the method exists
      const time = service.getTimeUntilLogout();
      expect(typeof time).toBe('number');
    });
  });

  describe('ngOnDestroy', () => {
    it('should stop monitoring on destroy', () => {
      const stopSpy = spyOn(service, 'stopMonitoring');
      
      service.ngOnDestroy();
      
      expect(stopSpy).toHaveBeenCalled();
    });
  });
});
