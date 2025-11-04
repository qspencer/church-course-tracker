import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseContentService } from '../../../services/course-content.service';
import { CourseContent, CourseContentCreate, CourseContentType, StorageType, CourseModule } from '../../../models';

export interface ContentDialogData {
  courseId: number;
  modules: CourseModule[];
  content?: CourseContent;
}

@Component({
  selector: 'app-content-dialog',
  templateUrl: './content-dialog.component.html',
  styleUrls: ['./content-dialog.component.scss']
})
export class ContentDialogComponent implements OnInit {
  contentForm: FormGroup;
  isEditing: boolean;
  isLoading = false;
  
  // Enums for template
  ContentType = CourseContentType;
  contentTypes = Object.values(CourseContentType);

  constructor(
    private fb: FormBuilder,
    private courseContentService: CourseContentService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<ContentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ContentDialogData
  ) {
    this.isEditing = !!data.content;
    
    this.contentForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(1)]],
      description: [''],
      content_type: [CourseContentType.DOCUMENT, Validators.required],
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
        title: this.data.content.title,
        description: this.data.content.description || '',
        content_type: this.data.content.content_type,
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

  updateValidators(contentType: CourseContentType): void {
    const externalUrlControl = this.contentForm.get('external_url');
    const embeddedContentControl = this.contentForm.get('embedded_content');
    
    if (contentType === CourseContentType.EXTERNAL_LINK) {
      externalUrlControl?.setValidators([Validators.required]);
      embeddedContentControl?.clearValidators();
    } else if (contentType === CourseContentType.EMBEDDED) {
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
    if (this.isLoading || !this.contentForm.valid) {
      return;
    }
    
    this.isLoading = true;
    const formValue = this.contentForm.value;

    if (this.isEditing && this.data.content) {
      // Update existing content
      const updateData: Partial<CourseContentCreate> = {
        title: formValue.title,
        description: formValue.description || undefined,
        content_type: formValue.content_type,
        module_id: formValue.module_id || undefined,
        external_url: formValue.external_url || undefined,
        embedded_content: formValue.embedded_content || undefined,
        order_index: formValue.order_index || 0
      };

      this.courseContentService.updateContent(this.data.content.id, updateData).subscribe({
        next: (content) => {
          this.isLoading = false;
          this.snackBar.open('Content updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(content);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error updating content:', error);
          let errorMessage = 'Failed to update content. Please try again.';
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to update content.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid content data. Please check your input.';
          }
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    } else {
      // Create new content
      // Determine storage type based on content type
      let storageType = StorageType.DATABASE;
      if (formValue.content_type === CourseContentType.EXTERNAL_LINK || 
          formValue.content_type === CourseContentType.EMBEDDED) {
        storageType = StorageType.EXTERNAL;
      }
      
      const contentData: CourseContentCreate = {
        course_id: this.data.courseId,
        title: formValue.title,
        description: formValue.description || undefined,
        content_type: formValue.content_type,
        storage_type: storageType,
        module_id: formValue.module_id || undefined,
        external_url: formValue.external_url || undefined,
        embedded_content: formValue.embedded_content || undefined,
        order_index: formValue.order_index || 0,
        is_active: true
      };

      this.courseContentService.createContent(contentData).subscribe({
        next: (content) => {
          this.isLoading = false;
          this.snackBar.open('Content created successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(content);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error creating content:', error);
          let errorMessage = 'Failed to create content. Please try again.';
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to create content.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid content data. Please check your input.';
          }
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

  getContentTypeDisplayName(type: CourseContentType): string {
    switch (type) {
      case CourseContentType.DOCUMENT: return 'Document';
      case CourseContentType.VIDEO: return 'Video';
      case CourseContentType.AUDIO: return 'Audio';
      case CourseContentType.IMAGE: return 'Image';
      case CourseContentType.EXTERNAL_LINK: return 'External Link';
      case CourseContentType.EMBEDDED: return 'Embedded Content';
      default: return 'Unknown';
    }
  }
}

