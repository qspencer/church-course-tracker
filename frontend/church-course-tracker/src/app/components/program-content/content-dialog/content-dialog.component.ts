import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs/operators';
import { ProgramContentService } from '../../../services/program-content.service';
import { LoggerService } from '../../../services/logger.service';
import { ProgramContent, ProgramContentCreate, ProgramContentUpdate, ContentType, ProgramModule, getContentTypeDisplayName } from '../../../models/program-content.model';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatFormField, MatLabel, MatError, MatHint } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatButton } from '@angular/material/button';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

export interface ContentDialogData {
  programId: number;
  modules: ProgramModule[];
  content?: ProgramContent;
}

@Component({
    selector: 'app-program-content-dialog',
    templateUrl: './content-dialog.component.html',
    styleUrls: ['./content-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, ReactiveFormsModule, MatFormField, MatLabel, MatInput, MatError, MatSelect, MatOption, MatHint, MatDialogActions, MatButton, MatProgressSpinner]
})
export class ContentDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private programContentService = inject(ProgramContentService);
  private logger = inject(LoggerService);
  private snackBar = inject(MatSnackBar);
  dialogRef = inject<MatDialogRef<ContentDialogComponent>>(MatDialogRef);
  data = inject<ContentDialogData>(MAT_DIALOG_DATA);

  contentForm: FormGroup;
  isEditing: boolean;
  isLoading = false;
  isSubmitted = false;
  
  // Enums for template
  ContentType = ContentType;
  contentTypes = Object.values(ContentType);

  constructor() {
    const data = this.data;

    this.isEditing = !!data.content;
    
    this.contentForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(1)]],
      description: [''],
      content_type: [ContentType.DOCUMENT],
      module_id: [null],
      external_url: [''],
      embedded_content: [''],
      order_index: [0]
    });
  }

  ngOnInit(): void {
    if (this.data.content) {
      // Edit mode - populate form
      this.contentForm.patchValue({
        title: this.data.content.title || '',
        description: this.data.content.description || '',
        content_type: this.data.content.content_type || ContentType.DOCUMENT,
        module_id: this.data.content.module_id || null,
        external_url: this.data.content.external_url || '',
        embedded_content: this.data.content.embedded_content || '',
        order_index: this.data.content.order_index || 0
      });
    }
    
    // Update validators based on content type
    this.contentForm.get('content_type')?.valueChanges.subscribe(type => {
      this.updateValidators(type);
    });
    
    this.updateValidators(this.contentForm.get('content_type')?.value);
  }

  updateValidators(contentType: ContentType): void {
    const externalUrlControl = this.contentForm.get('external_url');
    const embeddedContentControl = this.contentForm.get('embedded_content');
    
    if (contentType === ContentType.EXTERNAL_LINK) {
      externalUrlControl?.setValidators([Validators.required]);
      embeddedContentControl?.clearValidators();
    } else if (contentType === ContentType.EMBEDDED) {
      embeddedContentControl?.setValidators([Validators.required]);
      externalUrlControl?.clearValidators();
    } else {
      externalUrlControl?.clearValidators();
      embeddedContentControl?.clearValidators();
    }
    
    externalUrlControl?.updateValueAndValidity();
    embeddedContentControl?.updateValueAndValidity();
  }

  onSubmit(): void {
    this.isSubmitted = true;

    if (this.isLoading || !this.contentForm.valid) {
      return;
    }

    this.isLoading = true;
    const formValue = this.contentForm.value;

    if (this.isEditing && this.data.content) {
      // Update existing content
      const updateData: ProgramContentUpdate = {
        title: formValue.title,
        description: formValue.description || undefined,
        content_type: formValue.content_type,
        module_id: formValue.module_id || undefined,
        external_url: formValue.external_url || undefined,
        embedded_content: formValue.embedded_content || undefined,
        order_index: formValue.order_index || 0
      };

      this.programContentService.updateContent(this.data.content.id, updateData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: (content) => {
            this.snackBar.open('Content updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(content);
          },
          error: (error) => {
            this.logger.error('Error updating content', error, { component: 'ContentDialogComponent', contentId: this.data.content?.id });
            let errorMessage = 'Failed to update content. Please try again.';
            if (error?.error?.detail) {
              errorMessage = error.error.detail;
            }
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
    } else {
      // Create new content
      const contentData: ProgramContentCreate = {
        program_id: this.data.programId,
        title: formValue.title,
        description: formValue.description || undefined,
        content_type: formValue.content_type,
        module_id: formValue.module_id || undefined,
        external_url: formValue.external_url || undefined,
        embedded_content: formValue.embedded_content || undefined,
        order_index: formValue.order_index || 0,
        is_active: true
      };

      this.programContentService.createContent(contentData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: (content) => {
            this.snackBar.open('Content created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(content);
          },
          error: (error) => {
            this.logger.error('Error creating content', error, { component: 'ContentDialogComponent', programId: this.data.programId });
            let errorMessage = 'Failed to create content. Please try again.';
            if (error?.error?.detail) {
              errorMessage = error.error.detail;
            }
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getContentTypeDisplayName(type: ContentType): string {
    return getContentTypeDisplayName(type);
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.contentForm.get(fieldName);
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}


