import { Component, Inject, OnInit, OnDestroy } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { Subject, interval } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MatIcon } from '@angular/material/icon';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatButton } from '@angular/material/button';

export interface InactivityWarningData {
  timeRemaining: number;
  message: string;
}

@Component({
    selector: 'app-inactivity-warning-dialog',
    templateUrl: './inactivity-warning-dialog.component.html',
    styleUrls: ['./inactivity-warning-dialog.component.scss'],
    imports: [MatDialogTitle, MatIcon, CdkScrollable, MatDialogContent, MatDialogActions, MatButton]
})
export class InactivityWarningDialogComponent implements OnInit, OnDestroy {
  timeRemaining: number;
  message: string;
  private destroy$ = new Subject<void>();

  constructor(
    public dialogRef: MatDialogRef<InactivityWarningDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: InactivityWarningData
  ) {
    this.timeRemaining = data.timeRemaining;
    this.message = data.message;
  }

  ngOnInit(): void {
    // Update countdown every second
    interval(1000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        if (this.timeRemaining > 0) {
          this.timeRemaining--;
          if (this.timeRemaining > 0) {
            this.message = `You will be logged out due to inactivity in ${this.timeRemaining} minute${this.timeRemaining !== 1 ? 's' : ''}.`;
          } else {
            this.message = 'You will be logged out due to inactivity in less than a minute.';
          }
        }
      });
  }

  stayLoggedIn(): void {
    this.dialogRef.close('stay');
  }

  logoutNow(): void {
    this.dialogRef.close('logout');
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

