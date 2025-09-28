import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject, takeUntil } from 'rxjs';

import { CourseContentService } from '../../services/course-content.service';
import { AuthService } from '../../services/auth.service';
import { CourseService } from '../../services/course.service';
import { AuditService } from '../../services/audit.service';
import {
  CourseModule, CourseContent, CourseContentType, StorageType,
  CourseModuleCreate, CourseContentCreate, CourseContentSummary, Course,
  AuditLog
} from '../../models';

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
      this.router.navigate(['/courses']);
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

  // Placeholder methods for future implementation
  createModule(): void {
    this.snackBar.open('Module creation not implemented yet', 'Close', { duration: 3000 });
  }

  createContent(): void {
    this.snackBar.open('Content creation not implemented yet', 'Close', { duration: 3000 });
  }

  editModule(module: CourseModule): void {
    this.snackBar.open('Module editing not implemented yet', 'Close', { duration: 3000 });
  }

  deleteModule(module: CourseModule): void {
    this.snackBar.open('Module deletion not implemented yet', 'Close', { duration: 3000 });
  }

  editContent(content: CourseContent): void {
    this.snackBar.open('Content editing not implemented yet', 'Close', { duration: 3000 });
  }

  deleteContent(content: CourseContent): void {
    this.snackBar.open('Content deletion not implemented yet', 'Close', { duration: 3000 });
  }

  viewContent(content: CourseContent): void {
    if (content.content_type === CourseContentType.EXTERNAL_LINK && content.external_url) {
      window.open(content.external_url, '_blank');
    } else if (content.content_type === CourseContentType.EMBEDDED && content.embedded_content) {
      this.snackBar.open('Embedded content viewer not implemented yet', 'Close', { duration: 3000 });
    } else {
      this.downloadContent(content);
    }
  }

  downloadContent(content: CourseContent): void {
    if (content.storage_type === StorageType.EXTERNAL && content.external_url) {
      window.open(content.external_url, '_blank');
    } else if (content.storage_type === StorageType.DATABASE || content.storage_type === StorageType.S3) {
      this.courseContentService.downloadContent(content.id).subscribe({
        next: (blob) => {
          const a = document.createElement('a');
          const objectUrl = URL.createObjectURL(blob);
          a.href = objectUrl;
          a.download = content.file_name || 'download';
          a.click();
          URL.revokeObjectURL(objectUrl);
          this.snackBar.open('Content downloaded successfully', 'Close', { duration: 3000 });
        },
        error: (error) => {
          console.error('Error downloading content:', error);
          this.snackBar.open('Failed to download content', 'Close', { duration: 3000 });
        }
      });
    } else {
      this.snackBar.open('Content not available for download', 'Close', { duration: 3000 });
    }
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
