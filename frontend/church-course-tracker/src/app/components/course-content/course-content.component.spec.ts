import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { CourseContentComponent } from './course-content.component';
import { CourseContentService } from '../../services/course-content.service';
import { CourseService } from '../../services/course.service';
import { AuthService } from '../../services/auth.service';
import { AuditService } from '../../services/audit.service';
import {
  Course, CourseModule, CourseContent, CourseContentType, StorageType,
  CourseContentSummary, AuditLog
} from '../../models';

describe('CourseContentComponent', () => {
  let component: CourseContentComponent;
  let fixture: ComponentFixture<CourseContentComponent>;
  let courseContentService: jasmine.SpyObj<CourseContentService>;
  let courseService: jasmine.SpyObj<CourseService>;
  let authService: jasmine.SpyObj<AuthService>;
  let auditService: jasmine.SpyObj<AuditService>;
  let router: jasmine.SpyObj<Router>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;
  let activatedRoute: jasmine.SpyObj<ActivatedRoute>;

  const mockCourse: Course = {
    id: 1,
    title: 'Test Course',
    description: 'Test Description',
    duration_weeks: 4,
    prerequisites: undefined,
    planning_center_event_id: undefined,
    planning_center_event_name: undefined,
    event_start_date: undefined,
    event_end_date: undefined,
    max_capacity: 50,
    current_registrations: 0,
    is_active: true,
    content_unlock_mode: 'immediate',
    max_file_size_mb: 1024,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1
  };

  const mockModule: CourseModule = {
    id: 1,
    course_id: 1,
    title: 'Test Module',
    description: 'Test Description',
    order_index: 1,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1,
    content_items: []
  };

  const mockContent: CourseContent = {
    id: 1,
    course_id: 1,
    module_id: 1,
    title: 'Test Content',
    description: 'Test Description',
    content_type: CourseContentType.DOCUMENT,
    storage_type: StorageType.DATABASE,
    file_name: 'test.pdf',
    file_size: 1024,
    file_path: '/path/to/file',
    mime_type: 'application/pdf',
    external_url: undefined,
    embedded_content: undefined,
    duration: undefined,
    download_count: 0,
    view_count: 0,
    order_index: 1,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    created_by: 1,
    updated_by: 1
  };

  const mockSummary: CourseContentSummary = {
    course_id: 1,
    total_content_items: 5,
    total_modules: 2,
    total_file_size: 1024000,
    content_by_type: {
      'document': 3,
      'video': 2
    },
    recent_uploads: [mockContent]
  };

  const mockAuditLog: AuditLog = {
    id: 1,
    table_name: 'course_content',
    record_id: 1,
    action: 'insert',
    old_values: undefined,
    new_values: { title: 'Test Content' },
    changed_by: 1,
    changed_at: '2024-01-01T00:00:00Z',
    ip_address: '192.168.1.1',
    user_agent: 'Mozilla/5.0...'
  };

  beforeEach(async () => {
    const courseContentServiceSpy = jasmine.createSpyObj('CourseContentService', [
      'getCourseModules', 'getCourseContent', 'getCourseContentSummary',
      'downloadContent', 'getContentAuditLogs'
    ]);
    const courseServiceSpy = jasmine.createSpyObj('CourseService', ['getCourse']);
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['isAdmin', 'hasAnyRole', 'hasRole']);
    const auditServiceSpy = jasmine.createSpyObj('AuditService', ['getAuditLogs']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    const activatedRouteSpy = jasmine.createSpyObj('ActivatedRoute', [], {
      snapshot: { 
        paramMap: { 
          get: jasmine.createSpy('get').and.returnValue('1') 
        } 
      }
    });

    await TestBed.configureTestingModule({
      declarations: [CourseContentComponent],
      imports: [
        NoopAnimationsModule,
        MatTabsModule,
        MatListModule,
        MatIconModule,
        MatButtonModule,
        MatProgressSpinnerModule
      ],
      providers: [
        { provide: CourseContentService, useValue: courseContentServiceSpy },
        { provide: CourseService, useValue: courseServiceSpy },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: AuditService, useValue: auditServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatDialog, useValue: dialogSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: ActivatedRoute, useValue: activatedRouteSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(CourseContentComponent);
    component = fixture.componentInstance;
    courseContentService = TestBed.inject(CourseContentService) as jasmine.SpyObj<CourseContentService>;
    courseService = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    auditService = TestBed.inject(AuditService) as jasmine.SpyObj<AuditService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    dialog = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    activatedRoute = TestBed.inject(ActivatedRoute) as jasmine.SpyObj<ActivatedRoute>;
  });

  beforeEach(() => {
    // Setup default spy returns
    courseService.getCourse.and.returnValue(of(mockCourse));
    courseContentService.getCourseModules.and.returnValue(of([mockModule]));
    courseContentService.getCourseContent.and.returnValue(of([mockContent]));
    courseContentService.getCourseContentSummary.and.returnValue(of(mockSummary));
    auditService.getAuditLogs.and.returnValue(of([mockAuditLog]));
    authService.isAdmin.and.returnValue(true);
    authService.hasAnyRole.and.returnValue(true);
    authService.hasRole.and.returnValue(true);
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with correct course ID', () => {
      component.ngOnInit();
      expect(component.courseId).toBe(1);
    });

    it('should handle invalid course ID', () => {
      // Reset the spy and set it to return invalid value
      (activatedRoute.snapshot.paramMap.get as jasmine.Spy).and.returnValue('invalid');
      component.ngOnInit();
      expect(snackBar.open).toHaveBeenCalledWith('Invalid course ID', 'Close', { duration: 3000 });
      expect(router.navigate).toHaveBeenCalledWith(['/courses']);
    });

    it('should load data on initialization', () => {
      component.ngOnInit();
      expect(courseService.getCourse).toHaveBeenCalledWith(1);
      expect(courseContentService.getCourseModules).toHaveBeenCalledWith(1);
      expect(courseContentService.getCourseContent).toHaveBeenCalledWith(1);
      expect(courseContentService.getCourseContentSummary).toHaveBeenCalledWith(1);
    });

    it('should set loading state correctly', () => {
      expect(component.isLoading).toBe(true);
      component.ngOnInit();
      expect(component.isLoading).toBe(false);
    });
  });

  describe('Data Loading', () => {
    it('should load course data successfully', () => {
      component.ngOnInit();
      expect(component.course).toEqual(mockCourse);
    });

    it('should load modules data successfully', () => {
      component.ngOnInit();
      expect(component.modules).toEqual([mockModule]);
    });

    it('should load content items successfully', () => {
      component.ngOnInit();
      expect(component.contentItems).toEqual([mockContent]);
    });

    it('should load content summary successfully', () => {
      component.ngOnInit();
      expect(component.contentSummary).toEqual(mockSummary);
    });

    it('should load audit logs for admin users', () => {
      authService.isAdmin.and.returnValue(true);
      component.ngOnInit();
      expect(auditService.getAuditLogs).toHaveBeenCalledWith({
        table_name: 'course_content',
        limit: 100
      });
      expect(component.auditLogs).toEqual([mockAuditLog]);
    });

    it('should not load audit logs for non-admin users', () => {
      authService.isAdmin.and.returnValue(false);
      component.ngOnInit();
      expect(auditService.getAuditLogs).not.toHaveBeenCalled();
    });

    it('should handle course loading error', () => {
      courseService.getCourse.and.returnValue(throwError('Course not found'));
      component.ngOnInit();
      expect(snackBar.open).toHaveBeenCalledWith('Error loading course details', 'Close', { duration: 3000 });
    });

    it('should handle modules loading error', () => {
      courseContentService.getCourseModules.and.returnValue(throwError('Modules not found'));
      component.ngOnInit();
      expect(snackBar.open).toHaveBeenCalledWith('Error loading course modules', 'Close', { duration: 3000 });
    });

    it('should handle content loading error', () => {
      courseContentService.getCourseContent.and.returnValue(throwError('Content not found'));
      component.ngOnInit();
      expect(snackBar.open).toHaveBeenCalledWith('Error loading course content', 'Close', { duration: 3000 });
      expect(component.isLoading).toBe(false);
    });

    it('should handle summary loading error', () => {
      courseContentService.getCourseContentSummary.and.returnValue(throwError('Summary not found'));
      component.ngOnInit();
      // Should not show error for summary as it's not critical
    });

    it('should handle audit logs loading error', () => {
      auditService.getAuditLogs.and.returnValue(throwError('Audit logs not found'));
      component.ngOnInit();
      // Should not show error for audit logs as it's not critical
    });
  });

  describe('Permission Checks', () => {
    it('should check if user can manage content', () => {
      authService.hasAnyRole.and.returnValue(true);
      expect(component.canManageContent()).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should check if user can create modules', () => {
      authService.hasAnyRole.and.returnValue(true);
      expect(component.canCreateModules()).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should check if user can create content', () => {
      authService.hasAnyRole.and.returnValue(true);
      expect(component.canCreateContent()).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should check if user can edit content', () => {
      authService.hasAnyRole.and.returnValue(true);
      expect(component.canEditContent()).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should check if user can delete content', () => {
      authService.hasAnyRole.and.returnValue(true);
      expect(component.canDeleteContent()).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should check if user can view audit logs', () => {
      authService.isAdmin.and.returnValue(true);
      expect(component.canViewAuditLogs()).toBe(true);
      expect(authService.isAdmin).toHaveBeenCalled();
    });
  });

  describe('View Mode Management', () => {
    it('should set view mode correctly', () => {
      component.setViewMode('modules');
      expect(component.viewMode).toBe('modules');
      
      component.setViewMode('content');
      expect(component.viewMode).toBe('content');
      
      component.setViewMode('summary');
      expect(component.viewMode).toBe('summary');
      
      component.setViewMode('audit');
      expect(component.viewMode).toBe('audit');
    });
  });

  describe('Module Management', () => {
    it('should select module correctly', () => {
      component.selectModule(1);
      expect(component.selectedModuleId).toBe(1);
      
      component.selectModule(null);
      expect(component.selectedModuleId).toBeNull();
    });

    it('should get content for module', () => {
      component.contentItems = [mockContent];
      const content = component.getContentForModule(1);
      expect(content).toEqual([mockContent]);
    });

    it('should get content without module', () => {
      const contentWithoutModule = { ...mockContent, module_id: undefined };
      component.contentItems = [mockContent, contentWithoutModule];
      const content = component.getContentWithoutModule();
      expect(content).toEqual([contentWithoutModule]);
    });

    it('should get module title', () => {
      component.modules = [mockModule];
      const title = component.getModuleTitle(1);
      expect(title).toBe('Test Module');
    });

    it('should return unknown for non-existent module', () => {
      const title = component.getModuleTitle(999);
      expect(title).toBe('Unknown Module');
    });
  });

  describe('Content Type Helpers', () => {
    it('should check if content is external', () => {
      const externalContent = { ...mockContent, content_type: CourseContentType.EXTERNAL_LINK };
      expect(component.isExternalContent(externalContent)).toBe(true);
      
      const embeddedContent = { ...mockContent, content_type: CourseContentType.EMBEDDED };
      expect(component.isExternalContent(embeddedContent)).toBe(true);
      
      expect(component.isExternalContent(mockContent)).toBe(false);
    });

    it('should check if content is file content', () => {
      expect(component.isFileContent(mockContent)).toBe(true);
      
      const videoContent = { ...mockContent, content_type: CourseContentType.VIDEO };
      expect(component.isFileContent(videoContent)).toBe(true);
      
      const externalContent = { ...mockContent, content_type: CourseContentType.EXTERNAL_LINK };
      expect(component.isFileContent(externalContent)).toBe(false);
    });
  });

  describe('Utility Functions', () => {
    it('should get content type display name', () => {
      expect(component.getContentTypeDisplayName(CourseContentType.DOCUMENT)).toBe('Document');
      expect(component.getContentTypeDisplayName(CourseContentType.VIDEO)).toBe('Video');
      expect(component.getContentTypeDisplayName(CourseContentType.AUDIO)).toBe('Audio');
      expect(component.getContentTypeDisplayName(CourseContentType.IMAGE)).toBe('Image');
      expect(component.getContentTypeDisplayName(CourseContentType.EXTERNAL_LINK)).toBe('External Link');
      expect(component.getContentTypeDisplayName(CourseContentType.EMBEDDED)).toBe('Embedded Content');
    });

    it('should get content type icon', () => {
      expect(component.getContentTypeIcon(CourseContentType.DOCUMENT)).toBe('description');
      expect(component.getContentTypeIcon(CourseContentType.VIDEO)).toBe('videocam');
      expect(component.getContentTypeIcon(CourseContentType.AUDIO)).toBe('audiotrack');
      expect(component.getContentTypeIcon(CourseContentType.IMAGE)).toBe('image');
      expect(component.getContentTypeIcon(CourseContentType.EXTERNAL_LINK)).toBe('link');
      expect(component.getContentTypeIcon(CourseContentType.EMBEDDED)).toBe('code');
    });

    it('should format file size', () => {
      expect(component.formatFileSize(0)).toBe('0 Bytes');
      expect(component.formatFileSize(1024)).toBe('1 KB');
      expect(component.formatFileSize(1048576)).toBe('1 MB');
      expect(component.formatFileSize(1073741824)).toBe('1 GB');
    });

    it('should format duration', () => {
      expect(component.formatDuration(0)).toBe('0:00');
      expect(component.formatDuration(60)).toBe('1:00');
      expect(component.formatDuration(3661)).toBe('1:01:01');
    });
  });

  describe('Content Actions', () => {
    it('should view external content', () => {
      const externalContent = { ...mockContent, content_type: CourseContentType.EXTERNAL_LINK, external_url: 'https://example.com' };
      spyOn(window, 'open');
      component.viewContent(externalContent);
      expect(window.open).toHaveBeenCalledWith('https://example.com', '_blank');
    });

    it('should view embedded content', () => {
      const embeddedContent = { ...mockContent, content_type: CourseContentType.EMBEDDED, embedded_content: '<iframe></iframe>' };
      component.viewContent(embeddedContent);
      expect(snackBar.open).toHaveBeenCalledWith('Embedded content viewer not implemented yet', 'Close', { duration: 3000 });
    });

    it('should download file content', () => {
      spyOn(component, 'downloadContent');
      component.viewContent(mockContent);
      expect(component.downloadContent).toHaveBeenCalledWith(mockContent);
    });

    it('should download content successfully', () => {
      const blob = new Blob(['content'], { type: 'application/pdf' });
      courseContentService.downloadContent.and.returnValue(of(blob));
      spyOn(URL, 'createObjectURL').and.returnValue('blob:url');
      spyOn(URL, 'revokeObjectURL');
      
      const linkSpy = jasmine.createSpyObj('HTMLAnchorElement', ['click']);
      spyOn(document, 'createElement').and.returnValue(linkSpy);
      
      component.downloadContent(mockContent);
      
      expect(courseContentService.downloadContent).toHaveBeenCalledWith(1);
      expect(snackBar.open).toHaveBeenCalledWith('Content downloaded successfully', 'Close', { duration: 3000 });
    });

    it('should handle download error', () => {
      courseContentService.downloadContent.and.returnValue(throwError('Download failed'));
      component.downloadContent(mockContent);
      expect(snackBar.open).toHaveBeenCalledWith('Failed to download content', 'Close', { duration: 3000 });
    });

    it('should download external content', () => {
      const externalContent = { ...mockContent, storage_type: StorageType.EXTERNAL, external_url: 'https://example.com' };
      spyOn(window, 'open');
      component.downloadContent(externalContent);
      expect(window.open).toHaveBeenCalledWith('https://example.com', '_blank');
    });

    it('should show message for unavailable content', () => {
      const unavailableContent = { ...mockContent, storage_type: StorageType.EXTERNAL, external_url: undefined };
      component.downloadContent(unavailableContent);
      expect(snackBar.open).toHaveBeenCalledWith('Content not available for download', 'Close', { duration: 3000 });
    });
  });

  describe('Placeholder Methods', () => {
    it('should show placeholder for create module', () => {
      component.createModule();
      expect(snackBar.open).toHaveBeenCalledWith('Module creation not implemented yet', 'Close', { duration: 3000 });
    });

    it('should show placeholder for create content', () => {
      component.createContent();
      expect(snackBar.open).toHaveBeenCalledWith('Content creation not implemented yet', 'Close', { duration: 3000 });
    });

    it('should show placeholder for edit module', () => {
      component.editModule(mockModule);
      expect(snackBar.open).toHaveBeenCalledWith('Module editing not implemented yet', 'Close', { duration: 3000 });
    });

    it('should show placeholder for delete module', () => {
      component.deleteModule(mockModule);
      expect(snackBar.open).toHaveBeenCalledWith('Module deletion not implemented yet', 'Close', { duration: 3000 });
    });

    it('should show placeholder for edit content', () => {
      component.editContent(mockContent);
      expect(snackBar.open).toHaveBeenCalledWith('Content editing not implemented yet', 'Close', { duration: 3000 });
    });

    it('should show placeholder for delete content', () => {
      component.deleteContent(mockContent);
      expect(snackBar.open).toHaveBeenCalledWith('Content deletion not implemented yet', 'Close', { duration: 3000 });
    });
  });

  describe('Audit Log Utilities', () => {
    it('should get audit action display name', () => {
      expect(component.getAuditActionDisplayName('insert')).toBe('Created');
      expect(component.getAuditActionDisplayName('update')).toBe('Updated');
      expect(component.getAuditActionDisplayName('delete')).toBe('Deleted');
      expect(component.getAuditActionDisplayName('unknown')).toBe('unknown');
    });

    it('should get audit action icon', () => {
      expect(component.getAuditActionIcon('insert')).toBe('add_circle');
      expect(component.getAuditActionIcon('update')).toBe('edit');
      expect(component.getAuditActionIcon('delete')).toBe('delete');
      expect(component.getAuditActionIcon('unknown')).toBe('help');
    });

    it('should format audit timestamp', () => {
      const timestamp = '2024-01-01T12:30:45Z';
      const formatted = component.formatAuditTimestamp(timestamp);
      expect(formatted).toContain('2024');
      expect(formatted).toContain('12:30');
    });
  });

  describe('Component Cleanup', () => {
    it('should complete destroy subject on destroy', () => {
      spyOn(component['destroy$'], 'next');
      spyOn(component['destroy$'], 'complete');
      component.ngOnDestroy();
      expect(component['destroy$'].next).toHaveBeenCalled();
      expect(component['destroy$'].complete).toHaveBeenCalled();
    });
  });
});
