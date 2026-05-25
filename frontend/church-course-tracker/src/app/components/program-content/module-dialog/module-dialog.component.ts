import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs/operators';
import { ProgramContentService } from '../../../services/program-content.service';
import { LoggerService } from '../../../services/logger.service';
import { ProgramModule, ProgramModuleCreate, ProgramModuleUpdate } from '../../../models/program-content.model';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatFormField, MatLabel, MatSuffix, MatError, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatIcon } from '@angular/material/icon';
import { MatButton } from '@angular/material/button';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

export interface ModuleDialogData {
  programId: number;
  module?: ProgramModule;
}

@Component({
    selector: 'app-program-module-dialog',
    templateUrl: './module-dialog.component.html',
    styleUrls: ['./module-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, ReactiveFormsModule, MatFormField, MatLabel, MatInput, MatIcon, MatSuffix, MatError, MatHint, MatDialogActions, MatButton, MatProgressSpinner]
})
export class ModuleDialogComponent implements OnInit {
  moduleForm: FormGroup;
  isEditing: boolean;
  isSubmitting = false;
  isSubmitted = false; // Track if form has been submitted

  constructor(
    private fb: FormBuilder,
    private programContentService: ProgramContentService,
    private logger: LoggerService,
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
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;

    if (this.isSubmitting || !this.moduleForm.valid) {
      return;
    }

    this.isSubmitting = true;

    if (this.isEditing && this.data.module) {
      // Update existing module
      const updateData: ProgramModuleUpdate = this.moduleForm.value;

      this.programContentService.updateModule(this.data.module.id, updateData)
        .pipe(finalize(() => this.isSubmitting = false))
        .subscribe({
          next: (module) => {
            this.snackBar.open('Category updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            this.logger.error('Error updating module', error, { component: 'ModuleDialogComponent', moduleId: this.data.module?.id });
            const errorMessage = error?.error?.detail || 'Error updating category';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
    } else {
      // Create new module
      const createData: ProgramModuleCreate = {
        ...this.moduleForm.value,
        program_id: this.data.programId
      };

      this.programContentService.createModule(createData)
        .pipe(finalize(() => this.isSubmitting = false))
        .subscribe({
          next: (module) => {
            this.snackBar.open('Category created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            this.logger.error('Error creating module', error, { component: 'ModuleDialogComponent', programId: this.data.programId });
            const errorMessage = error?.error?.detail || 'Error creating category';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
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


