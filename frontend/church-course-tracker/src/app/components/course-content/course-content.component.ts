import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject } from 'rxjs';
import { takeUntil, finalize } from 'rxjs/operators';

import { CourseContentService } from '../../services/course-content.service';
import { AuthService } from '../../services/auth.service';
import { CourseService } from '../../services/course.service';
import { AuditService } from '../../services/audit.service';
import {
  CourseModule, CourseContent, CourseContentType, StorageType,
  CourseModuleCreate, CourseContentCreate, CourseContentSummary, Course,
  AuditLog
} from '../../models';
import { ContentDialogComponent } from './content-dialog/content-dialog.component';
import { ModuleDialogComponent, ModuleDialogData } from './module-dialog/module-dialog.component';
import { EmbeddedContentViewerComponent, EmbeddedContentViewerData } from './embedded-content-viewer/embedded-content-viewer.component';
import {
  ConfirmDialogComponent,
  ConfirmDialogData
} from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-course-content',
  templateUrl: './course-content.component.html',
  styleUrls: ['./course-content.component.scss']
})
export class CourseContentComponent implements OnInit, OnDestroy {
  @Input() courseId!: number;

  // Data
  course: Course | null = null;
  modules: CourseModule[] = [];
  contentItems: CourseContent[] = [];
  contentSummary: CourseContentSummary | null = null;
  auditLogs: AuditLog[] = [];

  // UI state
  isLoading = true;
  selectedModuleId: number | null = null;
  viewMode: 'modules' | 'content' | 'summary' | 'audit' = 'content';
  
  // Enums for template
  ContentType = CourseContentType;
  StorageType = StorageType;

  private destroy$ = new Subject<void>();

  constructor(
    private courseContentService: CourseContentService,
    private courseService: CourseService,
    private authService: AuthService,
    private auditService: AuditService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.courseId = Number(this.route.snapshot.paramMap.get('courseId'));
    if (isNaN(this.courseId)) {
      this.snackBar.open('Invalid course ID', 'Close', { duration: 3000 });
      this.router.navigate(['/churchcoursetracker/courses']);
      return;
    }
    this.loadData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadData(): void {
    this.isLoading = true;
    
    // Load course details
    this.courseService.getCourse(this.courseId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (course) => {
        this.course = course;
      },
      error: (error) => {
        console.error('Error loading course:', error);
        this.snackBar.open('Error loading course details', 'Close', { duration: 3000 });
      }
    });

    // Load modules
    this.courseContentService.getCourseModules(this.courseId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (modules) => {
        this.modules = modules.sort((a, b) => a.order_index - b.order_index);
      },
      error: (error) => {
        console.error('Error loading modules:', error);
        this.snackBar.open('Error loading course modules', 'Close', { duration: 3000 });
      }
    });

    // Load content items
    this.courseContentService.getCourseContent(this.courseId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (contentItems) => {
        this.contentItems = contentItems.sort((a, b) => a.order_index - b.order_index);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading content items:', error);
        this.snackBar.open('Error loading course content', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });

    // Load content summary
    this.courseContentService.getCourseContentSummary(this.courseId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (summary) => {
        this.contentSummary = summary;
      },
      error: (error) => {
        console.error('Error loading content summary:', error);
      }
    });

    // Load audit logs for course content
    this.loadAuditLogs();
  }

  loadAuditLogs(): void {
    if (!this.authService.isAdmin()) {
      return; // Only admins can view audit logs
    }

    this.auditService.getAuditLogs({
      table_name: 'course_content',
      limit: 100
    }).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (logs) => {
        // Filter logs for this course's content
        this.auditLogs = logs.filter(log => {
          // Check if the record_id corresponds to content items in this course
          return this.contentItems.some(item => item.id === log.record_id);
        });
      },
      error: (error) => {
        console.error('Error loading audit logs:', error);
      }
    });
  }

  // Permission checks
  canManageContent(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canCreateModules(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canCreateContent(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canEditContent(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canDeleteContent(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  // View mode management
  setViewMode(mode: 'modules' | 'content' | 'summary' | 'audit'): void {
    this.viewMode = mode;
  }

  // Module management
  selectModule(moduleId: number | null): void {
    this.selectedModuleId = moduleId;
  }

  getContentForModule(moduleId: number): CourseContent[] {
    return this.contentItems.filter(item => item.module_id === moduleId);
  }

  getContentWithoutModule(): CourseContent[] {
    return this.contentItems.filter(item => !item.module_id);
  }

  getModuleTitle(moduleId: number): string {
    const module = this.modules.find(m => m.id === moduleId);
    return module ? module.title : 'Unknown Module';
  }

  // Content type helpers
  isExternalContent(content: CourseContent): boolean {
    return content.content_type === CourseContentType.EXTERNAL_LINK || 
           content.content_type === CourseContentType.EMBEDDED;
  }

  isFileContent(content: CourseContent): boolean {
    return content.content_type === CourseContentType.DOCUMENT ||
           content.content_type === CourseContentType.VIDEO ||
           content.content_type === CourseContentType.AUDIO ||
           content.content_type === CourseContentType.IMAGE;
  }

  // Utility functions for template
  getContentTypeDisplayName(contentType: CourseContentType): string {
    switch (contentType) {
      case CourseContentType.DOCUMENT: return 'Document';
      case CourseContentType.VIDEO: return 'Video';
      case CourseContentType.AUDIO: return 'Audio';
      case CourseContentType.IMAGE: return 'Image';
      case CourseContentType.EXTERNAL_LINK: return 'External Link';
      case CourseContentType.EMBEDDED: return 'Embedded Content';
      default: return 'Unknown';
    }
  }

  getContentTypeIcon(contentType: CourseContentType): string {
    switch (contentType) {
      case CourseContentType.DOCUMENT: return 'description';
      case CourseContentType.VIDEO: return 'videocam';
      case CourseContentType.AUDIO: return 'audiotrack';
      case CourseContentType.IMAGE: return 'image';
      case CourseContentType.EXTERNAL_LINK: return 'link';
      case CourseContentType.EMBEDDED: return 'code';
      default: return 'insert_drive_file';
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDuration(seconds: number): string {
    if (!seconds) return '0:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  }

  createModule(): void {
    const dialogData: ModuleDialogData = {
      courseId: this.courseId
    };
    
    const dialogRef = this.dialog.open(ModuleDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: dialogData
    });
    
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        // Reload modules after successful creation
        this.loadData();
      }
    });
  }

  createContent(): void {
    this.dialog.open(ContentDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: {
        courseId: this.courseId,
        modules: this.modules
      }
    }).afterClosed().subscribe((result) => {
      if (result) {
        // Reload content after successful creation
        this.loadData();
      }
    });
  }

  editModule(module: CourseModule): void {
    const dialogData: ModuleDialogData = {
      courseId: this.courseId,
      module: module
    };
    
    const dialogRef = this.dialog.open(ModuleDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: dialogData
    });
    
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        // Reload modules after successful update
        this.loadData();
      }
    });
  }

  deleteModule(module: CourseModule): void {
    const dialogData: ConfirmDialogData = {
      title: 'Delete Module',
      message: `Are you sure you want to delete "${module.title}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    };
    
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: dialogData
    });
    
    dialogRef.afterClosed().subscribe((confirmed) => {
      if (confirmed) {
        this.courseContentService.deleteModule(module.id).subscribe({
          next: () => {
            this.snackBar.open('Module deleted successfully', 'Close', { duration: 3000 });
            this.loadData();
          },
          error: (error) => {
            console.error('Error deleting module:', error);
            const errorMessage = error?.error?.detail || 'Error deleting module';
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
      }
    });
  }

  editContent(content: CourseContent): void {
    this.dialog.open(ContentDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: {
        courseId: this.courseId,
        modules: this.modules,
        content: content // Pass the content to edit
      }
    }).afterClosed().subscribe((result) => {
      if (result) {
        // Reload content after successful update
        this.loadData();
      }
    });
  }

  deleteContent(content: CourseContent): void {
    const dialogData: ConfirmDialogData = {
      title: 'Delete Content',
      message: `Are you sure you want to delete "${content.title}"? This action cannot be undone.`,
      confirmText: 'Delete',
      cancelText: 'Cancel'
    };

    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '420px',
      data: dialogData,
      autoFocus: false
    });

    dialogRef.afterClosed().subscribe(confirmed => {
      if (!confirmed) {
        return;
      }

      this.isLoading = true;
      this.courseContentService
        .deleteContent(content.id)
        .pipe(
          finalize(() => {
            this.isLoading = false;
          })
        )
        .subscribe({
          next: () => {
            this.snackBar.open('Content deleted successfully', 'Close', {
              duration: 3000
            });
            this.loadData();
          },
          error: error => {
            console.error('Error deleting content:', error);
            let errorMessage = 'Failed to delete content. Please try again.';
            if (error?.error?.detail) {
              errorMessage = error.error.detail;
            }
            this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          }
        });
    });
  }

  viewContent(content: CourseContent): void {
    if (content.content_type === CourseContentType.EXTERNAL_LINK && content.external_url) {
      window.open(content.external_url, '_blank');
      return;
    }

    if (content.content_type === CourseContentType.EMBEDDED && content.embedded_content) {
      const viewerData: EmbeddedContentViewerData = {
        title: content.title,
        content: content.embedded_content
      };
      
      this.dialog.open(EmbeddedContentViewerComponent, {
        width: '800px',
        maxWidth: '90vw',
        maxHeight: '90vh',
        data: viewerData
      });
      return;
    }

    if (!content.file_path && !content.file_name) {
      // Fetch the latest metadata in case the UI is out of sync (e.g., right after an upload)
      this.courseContentService.getContentItem(content.id).subscribe({
        next: refreshedContent => {
          Object.assign(content, refreshedContent);
          if (!refreshedContent.file_path && !refreshedContent.file_name) {
            this.snackBar.open(
              'No file uploaded for this content. Please upload a file first.',
              'Close',
              { duration: 5000 }
            );
            return;
          }
          this.downloadContent(refreshedContent);
        },
        error: error => {
          console.error('Error refreshing content metadata:', error);
          this.snackBar.open(
            'Unable to load the latest file information. Please try again.',
            'Close',
            { duration: 5000 }
          );
        }
      });
      return;
    }

    this.downloadContent(content);
  }

  downloadContent(content: CourseContent): void {
    if (content.storage_type === StorageType.EXTERNAL && content.external_url) {
      window.open(content.external_url, '_blank');
    } else if (content.storage_type === StorageType.DATABASE || content.storage_type === StorageType.S3) {
      // Check if file exists before attempting download
      if (!content.file_path && !content.file_name) {
        this.snackBar.open('No file uploaded for this content. Please upload a file first.', 'Close', { duration: 5000 });
        return;
      }
      
      this.courseContentService.downloadContent(content.id).subscribe({
        next: (blob) => {
          const objectUrl = URL.createObjectURL(blob);
          const isPdf =
            (blob.type && blob.type.toLowerCase().includes('pdf')) ||
            (content.file_name && content.file_name.toLowerCase().endsWith('.pdf'));

          if (isPdf) {
            const newWindow = window.open(objectUrl, '_blank');
            if (!newWindow) {
              // Pop-up blocked; fallback to download
              this.triggerFileDownload(content, objectUrl);
              URL.revokeObjectURL(objectUrl);
            } else {
              newWindow.addEventListener(
                'load',
                () => {
                  URL.revokeObjectURL(objectUrl);
                },
                { once: true }
              );
              this.snackBar.open('Opening PDF in a new tab', 'Close', { duration: 3000 });
            }
          } else {
            this.triggerFileDownload(content, objectUrl);
            URL.revokeObjectURL(objectUrl);
          }
        },
        error: (error) => {
          console.error('Error downloading content:', error);
          let errorMessage = 'Failed to download content.';
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.status === 404) {
            errorMessage = 'File not found. The content may not have a file uploaded yet.';
          }
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
        }
      });
    } else {
      this.snackBar.open('Content not available for download', 'Close', { duration: 3000 });
    }
  }

  private triggerFileDownload(content: CourseContent, objectUrl: string): void {
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = content.file_name || 'download';
    anchor.click();
    this.snackBar.open('Content downloaded successfully', 'Close', { duration: 3000 });
  }

  // Audit-related utility functions
  canViewAuditLogs(): boolean {
    return this.authService.isAdmin();
  }

  getAuditActionDisplayName(action: string): string {
    switch (action) {
      case 'insert': return 'Created';
      case 'update': return 'Updated';
      case 'delete': return 'Deleted';
      default: return action;
    }
  }

  getAuditActionIcon(action: string): string {
    switch (action) {
      case 'insert': return 'add_circle';
      case 'update': return 'edit';
      case 'delete': return 'delete';
      default: return 'help';
    }
  }

  formatAuditTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    return date.toLocaleString();
  }
}
