import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { fakeAsync, tick, flush, discardPeriodicTasks } from '@angular/core/testing';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { InactivityWarningDialogComponent, InactivityWarningData } from './inactivity-warning-dialog.component';

describe('InactivityWarningDialogComponent', () => {
  let component: InactivityWarningDialogComponent;
  let fixture: ComponentFixture<InactivityWarningDialogComponent>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<InactivityWarningDialogComponent>>;

  const mockDialogData: InactivityWarningData = {
    timeRemaining: 5,
    message: 'You will be logged out due to inactivity in 5 minutes.'
  };

  beforeEach(async () => {
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
    imports: [
        BrowserAnimationsModule,
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
        InactivityWarningDialogComponent
    ],
    providers: [
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData }
    ]
}).compileComponents();

    fixture = TestBed.createComponent(InactivityWarningDialogComponent);
    component = fixture.componentInstance;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<InactivityWarningDialogComponent>>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with time remaining and message', () => {
    expect(component.timeRemaining).toBe(5);
    expect(component.message).toBe('You will be logged out due to inactivity in 5 minutes.');
  });

  it('should update countdown every second', fakeAsync(() => {
    // Clean up any existing timers from beforeEach
    component.ngOnDestroy();
    discardPeriodicTasks();
    
    // Reinitialize to start fresh timer
    component.timeRemaining = 5;
    component.message = 'You will be logged out due to inactivity in 5 minutes.';
    component.ngOnInit();
    
    expect(component.timeRemaining).toBe(5);

    tick(1000);
    expect(component.timeRemaining).toBe(4);
    expect(component.message).toContain('4 minute');

    tick(1000);
    expect(component.timeRemaining).toBe(3);
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  it('should update message when time remaining changes', fakeAsync(() => {
    // Clean up any existing timers from beforeEach
    component.ngOnDestroy();
    discardPeriodicTasks();
    
    // Reinitialize to start fresh timer
    component.timeRemaining = 5;
    component.message = 'You will be logged out due to inactivity in 5 minutes.';
    component.ngOnInit();
    
    tick(1000);

    expect(component.message).toContain('4 minute');
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  it('should handle singular minute', fakeAsync(() => {
    component.ngOnDestroy(); // Clean up existing timer
    discardPeriodicTasks();
    
    component.timeRemaining = 1;
    component.message = 'You will be logged out due to inactivity in 1 minute.';
    component.ngOnInit();
    tick(1000);

    // After 1 second, timeRemaining becomes 0, so message changes to "less than a minute"
    expect(component.timeRemaining).toBe(0);
    expect(component.message).toContain('less than a minute');
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  it('should handle plural minutes', fakeAsync(() => {
    component.ngOnDestroy(); // Clean up existing timer
    discardPeriodicTasks();
    
    component.timeRemaining = 2;
    component.message = 'You will be logged out due to inactivity in 2 minutes.';
    component.ngOnInit();
    tick(1000);

    // After 1 second, timeRemaining becomes 1, so message should say "1 minute"
    expect(component.timeRemaining).toBe(1);
    expect(component.message).toContain('1 minute');
    expect(component.message).not.toContain('minutes');
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  it('should update message when time reaches 0', fakeAsync(() => {
    component.ngOnDestroy(); // Clean up existing timer
    discardPeriodicTasks();
    
    component.timeRemaining = 1;
    component.message = 'You will be logged out due to inactivity in 1 minute.';
    component.ngOnInit();
    tick(1000);

    expect(component.timeRemaining).toBe(0);
    expect(component.message).toContain('less than a minute');
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  it('should not decrement below 0', fakeAsync(() => {
    component.ngOnDestroy(); // Clean up existing timer
    discardPeriodicTasks();
    
    component.timeRemaining = 0;
    component.message = 'You will be logged out due to inactivity in less than a minute.';
    component.ngOnInit();
    tick(2000);

    expect(component.timeRemaining).toBe(0);
    
    component.ngOnDestroy();
    discardPeriodicTasks();
    flush();
  }));

  describe('stayLoggedIn', () => {
    it('should close dialog with stay action', () => {
      component.stayLoggedIn();
      expect(dialogRefSpy.close).toHaveBeenCalledWith('stay');
    });
  });

  describe('logoutNow', () => {
    it('should close dialog with logout action', () => {
      component.logoutNow();
      expect(dialogRefSpy.close).toHaveBeenCalledWith('logout');
    });
  });

  describe('ngOnDestroy', () => {
    it('should complete destroy subject', fakeAsync(() => {
      // Clean up any existing timers from beforeEach
      component.ngOnDestroy();
      discardPeriodicTasks();
      
      // Reinitialize to start fresh timer
      component.timeRemaining = 5;
      component.message = 'You will be logged out due to inactivity in 5 minutes.';
      component.ngOnInit();
      
      const initialTime = component.timeRemaining;
      tick(1000);
      
      component.ngOnDestroy();
      discardPeriodicTasks();
      flush();

      // Time should have changed before destroy
      expect(component.timeRemaining).toBe(initialTime - 1);
    }));
  });
});
