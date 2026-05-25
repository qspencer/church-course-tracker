import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseContentService } from '../../../services/course-content.service';
import { CourseModule, CourseModuleCreate, CourseModuleUpdate } from '../../../models';
import { LoggerService } from '../../../services/logger.service';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatFormField, MatLabel, MatSuffix, MatError, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

export interface ModuleDialogData {
  courseId: number;
  module?: CourseModule;
}

@Component({
    selector: 'app-module-dialog',
    templateUrl: './module-dialog.component.html',
    styleUrls: ['./module-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, ReactiveFormsModule, MatFormField, MatLabel, MatInput, MatIcon, MatSuffix, MatError, MatHint, MatDialogActions, MatButton, MatProgressSpinner]
})
export class ModuleDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private courseContentService = inject(CourseContentService);
  private snackBar = inject(MatSnackBar);
  dialogRef = inject<MatDialogRef<ModuleDialogComponent>>(MatDialogRef);
  data = inject<ModuleDialogData>(MAT_DIALOG_DATA);
  private logger = inject(LoggerService);

  moduleForm: FormGroup;
  isEditing: boolean;
  isSubmitting = false;
  isSubmitted = false; // Track if form has been submitted

  constructor() {
    const data = this.data;

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
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
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
            this.logger.error('Error updating module', error, { component: 'ModuleDialogComponent', action: 'updateModule', moduleId: this.data.module?.id, courseId: this.data.courseId });
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
            this.logger.error('Error creating module', error, { component: 'ModuleDialogComponent', action: 'createModule', courseId: this.data.courseId });
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

  shouldShowError(fieldName: string): boolean {
    const field = this.moduleForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

