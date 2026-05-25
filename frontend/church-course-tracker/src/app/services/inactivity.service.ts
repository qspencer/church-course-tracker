import { Injectable, OnDestroy, inject } from '@angular/core';
import { Subject, Observable, fromEvent, merge } from 'rxjs';
import { debounceTime, takeUntil } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { InactivityWarningDialogComponent } from '../components/inactivity-warning-dialog/inactivity-warning-dialog.component';
import { LoggerService } from './logger.service';

@Injectable({
  providedIn: 'root'
})
export class InactivityService implements OnDestroy {
  private authService = inject(AuthService);
  private dialog = inject(MatDialog);
  private logger = inject(LoggerService);

  private readonly INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes in milliseconds
  private readonly WARNING_TIME = 2 * 60 * 1000; // Show warning 2 minutes before logout
  private readonly ACTIVITY_DEBOUNCE = 1000; // Debounce activity events by 1 second

  private inactivityTimer: ReturnType<typeof setTimeout> | null = null;
  private warningTimer: ReturnType<typeof setTimeout> | null = null;
  private warningDialogRef: MatDialogRef<InactivityWarningDialogComponent> | null = null;
  private destroy$ = new Subject<void>();
  private lastActivityTime: number = Date.now();

  /**
   * Start monitoring user activity
   */
  startMonitoring(): void {
    // Only monitor if user is authenticated
    this.authService.isAuthenticated$.subscribe(isAuthenticated => {
      if (isAuthenticated) {
        this.resetTimer();
        this.setupActivityListeners();
      } else {
        this.stopMonitoring();
      }
    });
  }

  /**
   * Stop monitoring user activity
   */
  stopMonitoring(): void {
    this.clearTimers();
    this.destroy$.next();
  }

  /**
   * Reset the inactivity timer
   */
  resetTimer(): void {
    this.lastActivityTime = Date.now();
    this.clearTimers();
    this.startTimers();
  }

  /**
   * Setup event listeners for user activity
   */
  private setupActivityListeners(): void {
    // Listen to various user activity events
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click'
    ];

    const eventStreams = events.map(event => fromEvent(document, event));

    merge(...eventStreams)
      .pipe(
        debounceTime(this.ACTIVITY_DEBOUNCE),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        // Only reset if user is still authenticated
        if (this.authService.getToken()) {
          this.resetTimer();
        }
      });
  }

  /**
   * Start the inactivity timers
   */
  private startTimers(): void {
    // Calculate when to show warning
    const warningTime = this.INACTIVITY_TIMEOUT - this.WARNING_TIME;

    // Set warning timer
    this.warningTimer = setTimeout(() => {
      this.showWarningDialog();
    }, warningTime);

    // Set logout timer
    this.inactivityTimer = setTimeout(() => {
      this.handleInactivity();
    }, this.INACTIVITY_TIMEOUT);
  }

  /**
   * Clear all timers
   */
  private clearTimers(): void {
    if (this.warningTimer) {
      clearTimeout(this.warningTimer);
      this.warningTimer = null;
    }
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = null;
    }
  }

  /**
   * Show warning dialog before logout
   */
  private showWarningDialog(): void {
    // Don't show multiple dialogs
    if (this.warningDialogRef) {
      return;
    }

    const timeRemainingMinutes = Math.ceil(this.WARNING_TIME / 1000 / 60); // minutes

    this.warningDialogRef = this.dialog.open(InactivityWarningDialogComponent, {
      width: '400px',
      disableClose: true,
      data: {
        timeRemaining: timeRemainingMinutes,
        message: `You will be logged out due to inactivity in ${timeRemainingMinutes} minute${timeRemainingMinutes > 1 ? 's' : ''}.`
      }
    });

    this.warningDialogRef.afterClosed().subscribe((result: string | undefined) => {
      this.warningDialogRef = null;
      if (result === 'stay') {
        // User clicked "Stay Logged In", reset timer
        this.resetTimer();
      } else if (result === 'logout') {
        // User clicked "Logout Now", logout immediately
        this.handleInactivity();
      }
      // If dialog is closed without action (shouldn't happen with disableClose: true),
      // the logout timer will still fire
    });
  }

  /**
   * Handle inactivity - log user out
   */
  private handleInactivity(): void {
    // Close warning dialog if open
    if (this.warningDialogRef) {
      this.warningDialogRef.close();
      this.warningDialogRef = null;
    }

    // Log user out
    this.authService.logout();

    // Log notification
    this.logger.info('User logged out due to inactivity', { component: 'InactivityService', action: 'handleInactivity' });
  }

  /**
   * Get time until logout (in milliseconds)
   */
  getTimeUntilLogout(): number {
    const elapsed = Date.now() - this.lastActivityTime;
    return Math.max(0, this.INACTIVITY_TIMEOUT - elapsed);
  }

  ngOnDestroy(): void {
    this.stopMonitoring();
    this.destroy$.complete();
  }
}

