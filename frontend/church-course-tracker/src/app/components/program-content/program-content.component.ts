import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject } from 'rxjs';
import { takeUntil, finalize } from 'rxjs/operators';

import { ProgramContentService } from '../../services/program-content.service';
import { AuthService } from '../../services/auth.service';
import { ProgramService } from '../../services/program.service';
import {
  ProgramModule, ProgramContent, ContentType,
  ProgramModuleCreate, ProgramContentCreate
} from '../../models/program-content.model';
import { Program as ProgramModel } from '../../models/program.model';
import { ContentDialogComponent } from './content-dialog/content-dialog.component';
import { ModuleDialogComponent, ModuleDialogData } from './module-dialog/module-dialog.component';
import {
  ConfirmDialogComponent,
  ConfirmDialogData
} from '../../shared/confirm-dialog/confirm-dialog.component';
import {
  getContentTypeDisplayName,
  getContentTypeIcon,
  formatFileSize,
  formatDuration
} from '../../models/program-content.model';

@Component({
  selector: 'app-program-content',
  templateUrl: './program-content.component.html',
  styleUrls: ['./program-content.component.scss']
})
export class ProgramContentComponent implements OnInit, OnDestroy {
  @Input() programId!: number;

  // Data
  program: ProgramModel | null = null;
  modules: ProgramModule[] = [];
  contentItems: ProgramContent[] = [];

  // UI state
  isLoading = true;
  selectedModuleId: number | null = null;
  viewMode: 'modules' | 'content' = 'content';
  
  // Enums for template
  ContentType = ContentType;

  private destroy$ = new Subject<void>();

  constructor(
    private programContentService: ProgramContentService,
    private programService: ProgramService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    // Get programId from route or @Input
    if (!this.programId) {
      this.programId = Number(this.route.snapshot.paramMap.get('programId'));
    }
    if (isNaN(this.programId)) {
      this.snackBar.open('Invalid program ID', 'Close', { duration: 3000 });
      this.router.navigate(['/churchcoursetracker/programs']);
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
    
    // Load program details
    this.programService.getProgram(this.programId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (program) => {
        this.program = program;
      },
      error: (error) => {
        console.error('Error loading program:', error);
        this.snackBar.open('Error loading program details', 'Close', { duration: 3000 });
      }
    });

    // Load modules
    this.programContentService.getProgramModules(this.programId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (modules) => {
        this.modules = modules.sort((a, b) => a.order_index - b.order_index);
      },
      error: (error) => {
        console.error('Error loading modules:', error);
        this.snackBar.open('Error loading program modules', 'Close', { duration: 3000 });
      }
    });

    // Load content items
    this.programContentService.getProgramContent(this.programId).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (contentItems) => {
        this.contentItems = contentItems.sort((a, b) => a.order_index - b.order_index);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading content items:', error);
        this.snackBar.open('Error loading program content', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  // Permission checks - simplified for programs (program admins can manage)
  canManageContent(): boolean {
    // For now, allow admin/staff. In future, check program admin status
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canCreateModules(): boolean {
    return this.canManageContent();
  }

  canCreateContent(): boolean {
    return this.canManageContent();
  }

  canEditContent(): boolean {
    return this.canManageContent();
  }

  canDeleteContent(): boolean {
    return this.canManageContent();
  }

  // View mode management
  setViewMode(mode: 'modules' | 'content'): void {
    this.viewMode = mode;
  }

  // Module management
  selectModule(moduleId: number | null): void {
    this.selectedModuleId = moduleId;
  }

  getContentForModule(moduleId: number): ProgramContent[] {
    return this.contentItems.filter(item => item.module_id === moduleId);
  }

  getContentWithoutModule(): ProgramContent[] {
    return this.contentItems.filter(item => !item.module_id);
  }

  getModuleTitle(moduleId: number): string {
    const module = this.modules.find(m => m.id === moduleId);
    return module ? module.title : 'Unknown Module';
  }

  // Content type helpers
  isExternalContent(content: ProgramContent): boolean {
    return content.content_type === ContentType.EXTERNAL_LINK || 
           content.content_type === ContentType.EMBEDDED;
  }

  isFileContent(content: ProgramContent): boolean {
    return content.content_type === ContentType.DOCUMENT ||
           content.content_type === ContentType.VIDEO ||
           content.content_type === ContentType.AUDIO ||
           content.content_type === ContentType.IMAGE;
  }

  // Utility functions for template
  getContentTypeDisplayName(contentType?: ContentType): string {
    return getContentTypeDisplayName(contentType);
  }

  getContentTypeIcon(contentType?: ContentType): string {
    return getContentTypeIcon(contentType);
  }

  formatFileSize(bytes?: number): string {
    return formatFileSize(bytes);
  }

  formatDuration(seconds?: number): string {
    return formatDuration(seconds);
  }

  createModule(): void {
    const dialogData: ModuleDialogData = {
      programId: this.programId
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
        programId: this.programId,
        modules: this.modules
      }
    }).afterClosed().subscribe((result) => {
      if (result) {
        // Reload content after successful creation
        this.loadData();
      }
    });
  }

  editModule(module: ProgramModule): void {
    const dialogData: ModuleDialogData = {
      programId: this.programId,
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

  deleteModule(module: ProgramModule): void {
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
        this.programContentService.deleteModule(module.id).subscribe({
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

  editContent(content: ProgramContent): void {
    this.dialog.open(ContentDialogComponent, {
      width: '600px',
      maxWidth: '90vw',
      data: {
        programId: this.programId,
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

  deleteContent(content: ProgramContent): void {
    const dialogData: ConfirmDialogData = {
      title: 'Delete Content',
      message: `Are you sure you want to delete "${content.title || 'this content'}"? This action cannot be undone.`,
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
      this.programContentService
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

  viewContent(content: ProgramContent): void {
    if (content.content_type === ContentType.EXTERNAL_LINK && content.external_url) {
      window.open(content.external_url, '_blank');
      return;
    }

    if (content.content_type === ContentType.EMBEDDED && content.embedded_content) {
      // For embedded content, we could open a dialog similar to course-content
      // For now, just show a message
      this.snackBar.open('Embedded content viewer not yet implemented', 'Close', { duration: 3000 });
      return;
    }

    // For file content, show a message that file viewing is not yet implemented
    this.snackBar.open('File viewing not yet implemented for program content', 'Close', { duration: 3000 });
  }
}

