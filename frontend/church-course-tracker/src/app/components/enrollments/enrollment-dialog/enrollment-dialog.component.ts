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
}

@Component({
  selector: 'app-enrollment-dialog',
  templateUrl: './enrollment-dialog.component.html',
  styleUrls: ['./enrollment-dialog.component.scss']
})
export class EnrollmentDialogComponent implements OnInit {
  enrollmentForm: FormGroup;
  isEditing: boolean;
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
    this.isEditing = !!data.enrollment;
    
    this.enrollmentForm = this.fb.group({
      person_id: ['', [Validators.required]],
      course_id: ['', [Validators.required]],
      status: [EnrollmentStatus.ENROLLED, [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.loadData();
    
    if (this.isEditing && this.data.enrollment) {
      this.enrollmentForm.patchValue({
        person_id: this.data.enrollment.person_id,
        course_id: this.data.enrollment.course_id,
        status: this.data.enrollment.status
      });
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
    return `${course.title} (${course.duration_weeks} weeks)`;
  }
}
