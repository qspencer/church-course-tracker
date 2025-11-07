import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';
import { EnrollmentService } from '../../../services/enrollment.service';
import { CourseService } from '../../../services/course.service';
import { MemberService } from '../../../services/member.service';
import { Enrollment, Course, Person, EnrollmentStatus } from '../../../models';

export interface EnrollmentDialogData {
  enrollment: Enrollment | null;
  viewMode?: boolean;
}

@Component({
  selector: 'app-enrollment-dialog',
  templateUrl: './enrollment-dialog.component.html',
  styleUrls: ['./enrollment-dialog.component.scss']
})
export class EnrollmentDialogComponent implements OnInit {
  enrollmentForm: FormGroup;
  isEditing: boolean;
  viewMode = false;
  isLoading = false;
  courses: Course[] = [];
  members: Person[] = [];
  statusOptions = [
    { value: EnrollmentStatus.ENROLLED, label: 'Enrolled' },
    { value: EnrollmentStatus.IN_PROGRESS, label: 'In Progress' },
    { value: EnrollmentStatus.COMPLETED, label: 'Completed' },
    { value: EnrollmentStatus.DROPPED, label: 'Dropped' }
  ];

  constructor(
    private fb: FormBuilder,
    private enrollmentService: EnrollmentService,
    private courseService: CourseService,
    private memberService: MemberService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<EnrollmentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EnrollmentDialogData
  ) {
    this.viewMode = !!data.viewMode;
    this.isEditing = !this.viewMode && !!data.enrollment;
    
    this.enrollmentForm = this.fb.group({
      person_id: ['', [Validators.required]],
      course_id: ['', [Validators.required]],
      status: [EnrollmentStatus.ENROLLED, [Validators.required]]
    });

    if (this.viewMode) {
      this.enrollmentForm.disable();
    }
  }

  ngOnInit(): void {
    if (!this.viewMode) {
      this.loadData();

      if (this.isEditing && this.data.enrollment) {
        this.enrollmentForm.patchValue({
          person_id: this.data.enrollment.person_id,
          course_id: this.data.enrollment.course_id,
          status: this.data.enrollment.status
        });
      }
    }
  }

  loadData(): void {
    this.isLoading = true;
    
    forkJoin({
      courses: this.courseService.getCourses({ is_active: true }),
      members: this.memberService.getMembers()
    }).subscribe({
      next: (data) => {
        this.courses = data.courses;
        this.members = data.members;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading data:', error);
        this.isLoading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.viewMode) {
      return;
    }
    if (this.enrollmentForm.valid) {
      this.isLoading = true;
      const formValue = this.enrollmentForm.value;

      if (this.isEditing && this.data.enrollment) {
        // Update existing enrollment
        const updateData = {
          status: formValue.status
        };

        this.enrollmentService.updateEnrollment(this.data.enrollment.id, updateData).subscribe({
          next: (enrollment) => {
            this.isLoading = false;
            this.snackBar.open('Enrollment updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(enrollment);
          },
          error: (error) => {
            this.isLoading = false;
            console.error('Error updating enrollment:', error);
          }
        });
      } else {
        // Create new enrollment
        const createData = {
          person_id: formValue.person_id,
          course_id: formValue.course_id
        };

        this.enrollmentService.createEnrollment(createData).subscribe({
          next: (enrollment) => {
            this.isLoading = false;
            this.snackBar.open('Enrollment created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(enrollment);
          },
          error: (error) => {
            this.isLoading = false;
            console.error('Error creating enrollment:', error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(fieldName: string): string {
    const field = this.enrollmentForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName.replace('_', ' ')} is required`;
    }
    return '';
  }

  getPersonDisplayName(person: Person): string {
    return `${person.first_name} ${person.last_name}`;
  }

  getCourseDisplayName(course: Course): string {
    const duration = course.duration_weeks ? ` (${course.duration_weeks} weeks)` : '';
    return `${course.title}${duration}`;
  }

  getStatusLabel(status: string): string {
    const match = this.statusOptions.find(option => option.value === status);
    return match ? match.label : status;
  }

  getStatusColor(status: string): 'primary' | 'accent' | 'warn' | undefined {
    if (!status) {
      return undefined;
    }

    switch (status.toLowerCase()) {
      case EnrollmentStatus.COMPLETED:
        return 'primary';
      case EnrollmentStatus.IN_PROGRESS:
        return 'accent';
      case EnrollmentStatus.DROPPED:
        return 'warn';
      default:
        return undefined;
    }
  }

  formatDate(date: string | Date | null | undefined): string {
    if (!date) {
      return 'N/A';
    }

    const parsedDate = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(parsedDate.getTime())) {
      return 'N/A';
    }

    return parsedDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  }
}
