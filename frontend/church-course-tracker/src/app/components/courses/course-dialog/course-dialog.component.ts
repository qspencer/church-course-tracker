import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseService } from '../../../services/course.service';
import { Course, CourseCreate, CourseUpdate } from '../../../models';

export interface CourseDialogData {
  course: Course | null;
  viewMode?: boolean; // If true, show read-only view
}

@Component({
  selector: 'app-course-dialog',
  templateUrl: './course-dialog.component.html',
  styleUrls: ['./course-dialog.component.scss']
})
export class CourseDialogComponent implements OnInit {
  courseForm: FormGroup;
  isEditing: boolean;
  viewMode: boolean;
  isLoading = false;
  course: Course | null = null;
  availablePrerequisites: Course[] = [];
  loadingPrerequisites = false;

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<CourseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CourseDialogData
  ) {
    this.viewMode = data.viewMode || false;
    this.isEditing = !!data.course && !this.viewMode;
    this.course = data.course || null;
    
    this.courseForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      duration_weeks: [1, [Validators.required, Validators.min(1), Validators.max(52)]],
      prerequisites: [[]]
    });
  }

  ngOnInit(): void {
    this.loadAvailablePrerequisites();
    
    if (this.data.course) {
      if (this.viewMode) {
        // In view mode, just store the course data
        this.course = this.data.course;
      } else {
        // In edit mode, populate the form
        const prerequisites = Array.isArray(this.data.course.prerequisites) 
          ? this.data.course.prerequisites 
          : [];
        this.courseForm.patchValue({
          title: this.data.course.title,
          description: this.data.course.description,
          duration_weeks: this.data.course.duration_weeks,
          prerequisites: prerequisites
        });
      }
    }
  }

  loadAvailablePrerequisites(): void {
    if (this.viewMode) return;
    
    this.loadingPrerequisites = true;
    this.courseService.getAvailablePrerequisites().subscribe({
      next: (courses) => {
        // Filter out the current course if editing
        if (this.isEditing && this.data.course) {
          this.availablePrerequisites = courses.filter(c => c.id !== this.data.course!.id);
        } else {
          this.availablePrerequisites = courses;
        }
        this.loadingPrerequisites = false;
      },
      error: (error) => {
        console.error('Error loading prerequisites:', error);
        this.loadingPrerequisites = false;
      }
    });
  }

  onSubmit(): void {
    // Prevent multiple submissions
    if (this.isLoading || !this.courseForm.valid) {
      return;
    }
    
    this.isLoading = true;
    const formValue = this.courseForm.value;

    if (this.isEditing && this.data.course) {
      // Update existing course
      const updateData: CourseUpdate = {
        title: formValue.title,
        description: formValue.description,
        duration_weeks: formValue.duration_weeks,
        prerequisites: formValue.prerequisites || []
      };

      this.courseService.updateCourse(this.data.course.id, updateData).subscribe({
        next: (course) => {
          this.isLoading = false;
          this.snackBar.open('Course updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(course);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error updating course:', error);
          // Extract error message
          let errorMessage = 'Failed to update course. Please try again.';
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to update courses.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid course data. Please check your input.';
          }
          // Error interceptor will also show a snackbar, but we show a more specific one here
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    } else {
      // Create new course
      const createData: CourseCreate = {
        title: formValue.title,
        description: formValue.description,
        duration_weeks: formValue.duration_weeks,
        prerequisites: formValue.prerequisites || []
      };

      this.courseService.createCourse(createData).subscribe({
        next: (course) => {
          this.isLoading = false;
          this.snackBar.open('Course created successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(course);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error creating course:', error);
          
          // If it's an auth error (401), user will be logged out by interceptor
          // Don't show course-specific error message for auth errors
          if (error?.status === 401) {
            // User will be redirected to login by auth service
            return;
          }
          
          // Extract error message
          let errorMessage = 'Failed to create course. Please try again.';
          if (error?.message && error.message.includes('session has expired')) {
            errorMessage = error.message;
          } else if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to create courses.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid course data. Please check your input.';
          }
          
          // Error interceptor will also show a snackbar, but we show a more specific one here
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onClose(): void {
    this.dialogRef.close();
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  }

  formatDuration(weeks: number | undefined): string {
    if (!weeks) return 'N/A';
    if (weeks === 1) return '1 week';
    if (weeks < 52) return `${weeks} weeks`;
    const years = Math.floor(weeks / 52);
    const remainingWeeks = weeks % 52;
    if (remainingWeeks === 0) {
      return years === 1 ? '1 year' : `${years} years`;
    }
    return `${years} year${years > 1 ? 's' : ''}, ${remainingWeeks} week${remainingWeeks > 1 ? 's' : ''}`;
  }

  getErrorMessage(fieldName: string): string {
    const field = this.courseForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('minlength')) {
      return `${fieldName} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    if (field?.hasError('min')) {
      return `${fieldName} must be at least ${field.errors?.['min'].min}`;
    }
    if (field?.hasError('max')) {
      return `${fieldName} must be at most ${field.errors?.['max'].max}`;
    }
    return '';
  }
}
