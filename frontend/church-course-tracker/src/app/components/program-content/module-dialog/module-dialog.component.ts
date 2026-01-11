import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgramContentService } from '../../../services/program-content.service';
import { ProgramModule, ProgramModuleCreate, ProgramModuleUpdate } from '../../../models/program-content.model';

export interface ModuleDialogData {
  programId: number;
  module?: ProgramModule;
}

@Component({
  selector: 'app-program-module-dialog',
  templateUrl: './module-dialog.component.html',
  styleUrls: ['./module-dialog.component.scss']
})
export class ModuleDialogComponent implements OnInit {
  moduleForm: FormGroup;
  isEditing: boolean;
  isSubmitting = false;
  isSubmitted = false; // Track if form has been submitted

  constructor(
    private fb: FormBuilder,
    private programContentService: ProgramContentService,
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
    
    if (this.moduleForm.valid && !this.isSubmitting) {
      this.isSubmitting = true;
      
      if (this.isEditing && this.data.module) {
        // Update existing module
        const updateData: ProgramModuleUpdate = this.moduleForm.value;
        
        this.programContentService.updateModule(this.data.module.id, updateData).subscribe({
          next: (module) => {
            this.snackBar.open('Category updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            console.error('Error updating module:', error);
            const errorMessage = error?.error?.detail || 'Error updating category';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
            this.isSubmitting = false;
          }
        });
      } else {
        // Create new module
        const createData: ProgramModuleCreate = {
          ...this.moduleForm.value,
          program_id: this.data.programId
        };
        
        this.programContentService.createModule(createData).subscribe({
          next: (module) => {
            this.snackBar.open('Category created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(module);
          },
          error: (error) => {
            console.error('Error creating module:', error);
            const errorMessage = error?.error?.detail || 'Error creating category';
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


