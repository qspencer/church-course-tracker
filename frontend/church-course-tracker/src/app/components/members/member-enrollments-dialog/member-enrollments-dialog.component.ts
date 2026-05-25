import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Enrollment } from '../../../models';
import { Person } from '../../../models';

export interface MemberEnrollmentsDialogData {
  member: Person;
  enrollments: Enrollment[];
}

@Component({
    selector: 'app-member-enrollments-dialog',
    templateUrl: './member-enrollments-dialog.component.html',
    styleUrls: ['./member-enrollments-dialog.component.scss'],
    standalone: false
})
export class MemberEnrollmentsDialogComponent implements OnInit {
  member: Person;
  enrollments: Enrollment[];

  constructor(
    public dialogRef: MatDialogRef<MemberEnrollmentsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: MemberEnrollmentsDialogData
  ) {
    this.member = data.member;
    this.enrollments = data.enrollments || [];
  }

  ngOnInit(): void {}

  getStatusColor(status: string): string {
    switch (status) {
      case 'completed':
        return 'primary';
      case 'in_progress':
        return 'accent';
      case 'dropped':
        return 'warn';
      default:
        return '';
    }
  }

  getStatusText(status: string): string {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  formatDate(date: string | null | undefined): string {
    if (!date) return 'N/A';
    try {
      const dateObj = new Date(date);
      if (isNaN(dateObj.getTime())) return 'N/A';
      return dateObj.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      return 'N/A';
    }
  }

  close(): void {
    this.dialogRef.close();
  }
}

