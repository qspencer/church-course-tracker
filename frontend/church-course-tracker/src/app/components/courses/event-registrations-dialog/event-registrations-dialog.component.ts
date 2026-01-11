import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';
import { PlanningCenterService, PlanningCenterRegistration } from '../../../services/planning-center.service';
import { EnrollmentService } from '../../../services/enrollment.service';
import { MemberService } from '../../../services/member.service';

export interface EventRegistrationsDialogData {
  eventId: string;
  eventName: string;
  courseId?: number;
}

@Component({
  selector: 'app-event-registrations-dialog',
  templateUrl: './event-registrations-dialog.component.html',
  styleUrls: ['./event-registrations-dialog.component.scss']
})
export class EventRegistrationsDialogComponent implements OnInit {
  registrations: PlanningCenterRegistration[] = [];
  dataSource = new MatTableDataSource<PlanningCenterRegistration>([]);
  isLoading = false;
  displayedColumns: string[] = ['select', 'person_name', 'status', 'registration_date', 'actions'];
  selectedRegistrations: Set<string> = new Set();

  constructor(
    private planningCenterService: PlanningCenterService,
    private enrollmentService: EnrollmentService,
    private memberService: MemberService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<EventRegistrationsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EventRegistrationsDialogData
  ) {}

  ngOnInit(): void {
    this.loadRegistrations();
  }

  loadRegistrations(): void {
    this.isLoading = true;
    this.planningCenterService.getEventRegistrations(this.data.eventId).subscribe({
      next: (registrations) => {
        this.registrations = registrations;
        this.dataSource.data = registrations;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading registrations:', error);
        this.snackBar.open('Error loading registrations: ' + (error.error?.detail || error.message), 'Close', { duration: 5000 });
        this.isLoading = false;
      }
    });
  }

  getPersonName(registration: PlanningCenterRegistration): string {
    const attrs = registration.attributes || {};
    // Backend attaches person_name, first_name, last_name to registration attributes
    if (attrs['person_name']) {
      return attrs['person_name'];
    }
    if (attrs['first_name'] || attrs['last_name']) {
      return `${attrs['first_name'] || ''} ${attrs['last_name'] || ''}`.trim();
    }
    // Fallback: check relationships
    if (registration.relationships?.person?.data) {
      return 'Person (ID: ' + registration.relationships.person.data.id + ')';
    }
    return 'Unknown Person';
  }

  getPersonEmail(registration: PlanningCenterRegistration): string {
    const attrs = registration.attributes || {};
    // Backend attaches email to registration attributes
    return attrs['email'] || '';
  }

  getStatusColor(status: string | undefined): 'primary' | 'accent' | 'warn' {
    if (!status) return 'primary';
    const statusLower = status.toLowerCase();
    if (statusLower.includes('registered') || statusLower.includes('active')) {
      return 'primary';
    } else if (statusLower.includes('waitlist') || statusLower.includes('pending')) {
      return 'accent';
    } else if (statusLower.includes('cancel') || statusLower.includes('inactive')) {
      return 'warn';
    }
    return 'primary';
  }

  importSingle(registration: PlanningCenterRegistration): void {
    // TODO: Implement single import
    this.toggleSelection(registration.id);
  }

  toggleSelection(registrationId: string): void {
    if (this.selectedRegistrations.has(registrationId)) {
      this.selectedRegistrations.delete(registrationId);
    } else {
      this.selectedRegistrations.add(registrationId);
    }
  }

  isSelected(registrationId: string): boolean {
    return this.selectedRegistrations.has(registrationId);
  }

  selectAll(): void {
    if (this.selectedRegistrations.size === this.registrations.length) {
      this.selectedRegistrations.clear();
    } else {
      this.registrations.forEach(reg => this.selectedRegistrations.add(reg.id));
    }
  }

  getSelectedCount(): number {
    return this.selectedRegistrations.size;
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  }

  onImport(): void {
    if (!this.data.courseId) {
      this.snackBar.open('Cannot import: Course ID is missing', 'Close', { duration: 3000 });
      return;
    }

    if (this.selectedRegistrations.size === 0) {
      this.snackBar.open('Please select at least one registration to import', 'Close', { duration: 3000 });
      return;
    }

    this.isLoading = true;
    const registrationIds = Array.from(this.selectedRegistrations);
    
    this.enrollmentService.importRegistrations(
      this.data.courseId,
      this.data.eventId,
      registrationIds
    ).subscribe({
      next: (enrollments) => {
        this.isLoading = false;
        this.snackBar.open(
          `Successfully imported ${enrollments.length} registration(s) as enrollments`,
          'Close',
          { duration: 5000 }
        );
        this.dialogRef.close({ imported: true, count: enrollments.length });
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error importing registrations:', error);
        const errorMessage = error.error?.detail || error.message || 'Failed to import registrations';
        this.snackBar.open(`Error: ${errorMessage}`, 'Close', { duration: 7000 });
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}

