import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseContentService } from '../../../services/course-content.service';
import { CourseModule, CourseModuleCreate, CourseModuleUpdate } from '../../../models';

export interface ModuleDialogData {
  courseId: number;
  module?: CourseModule;
}

@Component({
  selector: 'app-module-dialog',
  templateUrl: './module-dialog.component.html',
  styleUrls: ['./module-dialog.component.scss']
})
export class ModuleDialogComponent implements OnInit {
  moduleForm: FormGroup;
  isEditing: boolean;
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private courseContentService: CourseContentService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<ModuleDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ModuleDialogData
  ) {
    this.isEditing = !!data.module;
    
    this.moduleForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(1)]],
      description: [''],
      order_index: [0, [Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    if (this.data.module) {
      // Edit mode - populate form
      this.moduleForm.patchValue({
        title: this.data.module.title,
        description: this.data.module.description || '',
        order_index: this.data.module.order_index || 0
      });
    }
  }

  onSubmit(): void {
    if (this.moduleForm.valid && !this.isSubmitting) {
      this.isSubmitting = true;
      
      if (this.isEditing && this.data.module) {
        // Update existing module
        const updateData: CourseModuleUpdate = this.moduleForm.value;
        
        this.courseContentService.updateModule(this.data.module.id, updateData).subscribe({
          next: (module) => {
            this.snackBar.open('Module updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            console.error('Error updating module:', error);
            const errorMessage = error?.error?.detail || 'Error updating module';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
            this.isSubmitting = false;
          }
        });
      } else {
        // Create new module
        const createData: CourseModuleCreate = {
          ...this.moduleForm.value,
          course_id: this.data.courseId
        };
        
        this.courseContentService.createModule(createData).subscribe({
          next: (module) => {
            this.snackBar.open('Module created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            console.error('Error creating module:', error);
            const errorMessage = error?.error?.detail || 'Error creating module';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
            this.isSubmitting = false;
          }
        });
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(fieldName: string): string {
    const field = this.moduleForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('minlength')) {
      return `${fieldName} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    if (field?.hasError('min')) {
      return `${fieldName} must be at least ${field.errors?.['min'].min}`;
    }
    return '';
  }
}

