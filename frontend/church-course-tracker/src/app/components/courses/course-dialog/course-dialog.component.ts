import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseService } from '../../../services/course.service';
import { Course, CourseCreate, CourseUpdate } from '../../../models';

export interface CourseDialogData {
  course: Course | null;
}

@Component({
  selector: 'app-course-dialog',
  templateUrl: './course-dialog.component.html',
  styleUrls: ['./course-dialog.component.scss']
})
export class CourseDialogComponent implements OnInit {
  courseForm: FormGroup;
  isEditing: boolean;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<CourseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CourseDialogData
  ) {
    this.isEditing = !!data.course;
    
    this.courseForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      duration_weeks: [1, [Validators.required, Validators.min(1), Validators.max(52)]]
    });
  }

  ngOnInit(): void {
    if (this.isEditing && this.data.course) {
      this.courseForm.patchValue({
        title: this.data.course.title,
        description: this.data.course.description,
        duration_weeks: this.data.course.duration_weeks
      });
    }
  }

  onSubmit(): void {
    if (this.courseForm.valid) {
      this.isLoading = true;
      const formValue = this.courseForm.value;

      if (this.isEditing && this.data.course) {
        // Update existing course
        const updateData: CourseUpdate = {
          title: formValue.title,
          description: formValue.description,
          duration_weeks: formValue.duration_weeks
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
          }
        });
      } else {
        // Create new course
        const createData: CourseCreate = {
          title: formValue.title,
          description: formValue.description,
          duration_weeks: formValue.duration_weeks
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
          }
        });
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close();
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
