import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';
import { NO_ERRORS_SCHEMA } from '@angular/core';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';

import { ContentDialogComponent, ContentDialogData } from './content-dialog.component';
import { CourseContentService } from '../../../services/course-content.service';
import { CourseContent, CourseContentType, StorageType, CourseModule } from '../../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('ContentDialogComponent', () => {
  let component: ContentDialogComponent;
  let fixture: ComponentFixture<ContentDialogComponent>;
  let courseContentServiceSpy: jasmine.SpyObj<CourseContentService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ContentDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockModule: CourseModule = {
    id: 1,
    course_id: 1,
    title: 'Test Module',
    description: 'Test Description',
    order_index: 1,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockContent: CourseContent = {
    id: 1,
    course_id: 1,
    module_id: 1,
    title: 'Test Content',
    description: 'Test Description',
    content_type: CourseContentType.DOCUMENT,
    storage_type: StorageType.DATABASE,
    external_url: undefined,
    embedded_content: undefined,
    order_index: 1,
    is_active: true,
    download_count: 0,
    view_count: 0,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockDialogData: ContentDialogData = {
    courseId: 1,
    modules: [mockModule],
    content: undefined
  };

  const mockUploadResponse = {
    file_name: 'test.pdf',
    file_size: 1024,
    mime_type: 'application/pdf',
    message: 'File uploaded successfully'
  };

  beforeEach(async () => {
    const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    courseContentSpy.createContent.and.returnValue(of(mockContent));
    courseContentSpy.updateContent.and.returnValue(of(mockContent));
    courseContentSpy.uploadFile.and.returnValue(of(mockUploadResponse));

    await TestBed.configureTestingModule({
      declarations: [ContentDialogComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule
      ],
      providers: [
        { provide: CourseContentService, useValue: courseContentSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    fixture = TestBed.createComponent(ContentDialogComponent);
    component = fixture.componentInstance;
    courseContentServiceSpy = TestBed.inject(CourseContentService) as jasmine.SpyObj<CourseContentService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<ContentDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    // Don't call detectChanges() here to avoid template rendering issues
    // Call it in individual tests that need it
  });

  it('should create', () => {
    expect(component).toBeTruthy();
    // Don't call detectChanges to avoid template errors in basic tests
  });

  describe('Initialization', () => {
    it('should initialize in create mode', () => {
      // Component already initialized in beforeEach with content: undefined
      expect(component.isEditing).toBe(false);
    });

    it('should initialize in edit mode', () => {
      TestBed.resetTestingModule();
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseContentSpy.createContent.and.returnValue(of(mockContent));
      courseContentSpy.updateContent.and.returnValue(of(mockContent));
      courseContentSpy.uploadFile.and.returnValue(of(mockUploadResponse));

      TestBed.configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const newFixture = TestBed.createComponent(ContentDialogComponent);
      const newComponent = newFixture.componentInstance;
      // ngOnInit is called automatically, but let's ensure it has run
      // The form values are patched in ngOnInit() if data.content exists
      if (!newComponent.contentForm.get('title')?.value) {
        // If form isn't patched, manually call ngOnInit
        newComponent.ngOnInit();
      }
      expect(newComponent.isEditing).toBe(true);
      expect(newComponent.contentForm.get('title')?.value).toBe(mockContent.title);
    });

    it('should patch form values when editing', () => {
      TestBed.resetTestingModule();
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      TestBed.configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const newFixture = TestBed.createComponent(ContentDialogComponent);
      const newComponent = newFixture.componentInstance;
      // ngOnInit is called automatically, but let's ensure it has run
      // The form values are patched in ngOnInit() if data.content exists
      if (!newComponent.contentForm.get('title')?.value) {
        // If form isn't patched, manually call ngOnInit
        newComponent.ngOnInit();
      }
      expect(newComponent.isEditing).toBe(true);
      expect(newComponent.contentForm.get('title')?.value).toBe(mockContent.title);
      expect(newComponent.contentForm.get('description')?.value).toBe(mockContent.description);
      expect(newComponent.contentForm.get('content_type')?.value).toBe(mockContent.content_type);
    });

    it('should update validators based on content type', () => {
      component.contentForm.patchValue({ content_type: CourseContentType.EXTERNAL_LINK });
      // Trigger validator update manually
      component.updateValidators(CourseContentType.EXTERNAL_LINK);

      const externalUrlControl = component.contentForm.get('external_url');
      expect(externalUrlControl?.hasError('required')).toBe(true);
    });
  });

  describe('updateValidators', () => {
    // Component already initialized in beforeEach

    it('should require external_url for EXTERNAL_LINK type', () => {
      component.updateValidators(CourseContentType.EXTERNAL_LINK);
      const externalUrlControl = component.contentForm.get('external_url');
      expect(externalUrlControl?.hasError('required')).toBe(true);
    });

    it('should require embedded_content for EMBEDDED type', () => {
      component.updateValidators(CourseContentType.EMBEDDED);
      const embeddedContentControl = component.contentForm.get('embedded_content');
      expect(embeddedContentControl?.hasError('required')).toBe(true);
    });

    it('should clear validators for DOCUMENT type', () => {
      component.updateValidators(CourseContentType.DOCUMENT);
      const externalUrlControl = component.contentForm.get('external_url');
      const embeddedContentControl = component.contentForm.get('embedded_content');
      expect(externalUrlControl?.hasError('required')).toBe(false);
      expect(embeddedContentControl?.hasError('required')).toBe(false);
    });
  });

  describe('onSubmit - Create', () => {
    // Component already initialized in beforeEach with content: undefined

    it('should not submit invalid form', () => {
      component.contentForm.patchValue({
        title: '',
        content_type: CourseContentType.DOCUMENT
      });
      component.onSubmit();

      expect(courseContentServiceSpy.createContent).not.toHaveBeenCalled();
    });

    it('should not submit when loading', () => {
      component.isLoading = true;
      component.onSubmit();

      expect(courseContentServiceSpy.createContent).not.toHaveBeenCalled();
    });

    it('should create content without file', () => {
      component.contentForm.patchValue({
        title: 'New Content',
        description: 'Description',
        content_type: CourseContentType.DOCUMENT,
        order_index: 1
      });
      component.onSubmit();

      expect(courseContentServiceSpy.createContent).toHaveBeenCalled();
      expect(snackBarSpy.open).toHaveBeenCalledWith('Content created successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockContent);
    });

    it('should create content with file upload', () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      component.selectedFile = file;
      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.DOCUMENT,
        order_index: 1
      });
      component.onSubmit();

      expect(courseContentServiceSpy.createContent).toHaveBeenCalled();
      expect(courseContentServiceSpy.uploadFile).toHaveBeenCalledWith(mockContent.id, file);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Content created and file uploaded successfully', 'Close', { duration: 3000 });
    });

    it('should handle file upload error after content creation', () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      component.selectedFile = file;
      courseContentServiceSpy.uploadFile.and.returnValue(throwError(() => ({ error: { detail: 'Upload failed' } })));

      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.DOCUMENT,
        order_index: 1
      });
      component.onSubmit();

      expect(courseContentServiceSpy.createContent).toHaveBeenCalled();
      expect(snackBarSpy.open).toHaveBeenCalledWith(
        jasmine.stringContaining('Content created but file upload failed'),
        'Close',
        jasmine.any(Object)
      );
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockContent);
    });

    it('should set storage_type to EXTERNAL for EXTERNAL_LINK', () => {
      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.EXTERNAL_LINK,
        external_url: 'https://example.com',
        order_index: 1
      });
      component.onSubmit();

      const callArgs = courseContentServiceSpy.createContent.calls.mostRecent().args[0];
      expect(callArgs.storage_type).toBe(StorageType.EXTERNAL);
    });

    it('should set storage_type to EXTERNAL for EMBEDDED', () => {
      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.EMBEDDED,
        embedded_content: '<iframe></iframe>',
        order_index: 1
      });
      component.onSubmit();

      const callArgs = courseContentServiceSpy.createContent.calls.mostRecent().args[0];
      expect(callArgs.storage_type).toBe(StorageType.EXTERNAL);
    });

    it('should handle create error', () => {
      const error = { error: { detail: 'Error creating content' }, status: 400 };
      courseContentServiceSpy.createContent.and.returnValue(throwError(() => error));

      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.DOCUMENT,
        order_index: 1
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
      // Component uses error.detail if present, otherwise falls back to status-based message
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error creating content', 'Close', jasmine.objectContaining({
        duration: 5000,
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['error-snackbar']
      }));
    });

    it('should handle 403 error', () => {
      const error = { error: { detail: 'Forbidden' }, status: 403 };
      courseContentServiceSpy.createContent.and.returnValue(throwError(() => error));

      component.contentForm.patchValue({
        title: 'New Content',
        content_type: CourseContentType.DOCUMENT,
        order_index: 1
      });
      component.onSubmit();

      // Component uses error.detail if present, otherwise falls back to status-based message
      expect(snackBarSpy.open).toHaveBeenCalledWith('Forbidden', 'Close', jasmine.objectContaining({
        duration: 5000,
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['error-snackbar']
      }));
    });
  });

  describe('onSubmit - Update', () => {
    // Note: These tests create new component instances with edit data since data is read in constructor

    it('should update content without file', async () => {
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseContentSpy.updateContent.and.returnValue(of(mockContent));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const updateFixture = TestBed.createComponent(ContentDialogComponent);
      const updateComponent = updateFixture.componentInstance;
      // ngOnInit is called automatically, don't need detectChanges() for component logic tests
      
      updateComponent.contentForm.patchValue({
        title: 'Updated Content',
        description: 'Updated Description'
      });
      updateComponent.onSubmit();

      expect(courseContentSpy.updateContent).toHaveBeenCalledWith(mockContent.id, jasmine.any(Object));
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Content updated successfully', 'Close', { duration: 3000 });
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(mockContent);
    });

    it('should update content with file replacement', async () => {
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseContentSpy.updateContent.and.returnValue(of(mockContent));
      courseContentSpy.uploadFile.and.returnValue(of(mockUploadResponse));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const updateFixture = TestBed.createComponent(ContentDialogComponent);
      const updateComponent = updateFixture.componentInstance;
      // ngOnInit is called automatically, don't need detectChanges() for component logic tests
      if (!updateComponent.contentForm.get('title')?.value) {
        updateComponent.ngOnInit();
      }
      
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      updateComponent.selectedFile = file;
      updateComponent.contentForm.patchValue({
        title: 'Updated Content',
        content_type: CourseContentType.DOCUMENT
      });
      updateComponent.onSubmit();

      expect(courseContentSpy.updateContent).toHaveBeenCalled();
      expect(courseContentSpy.uploadFile).toHaveBeenCalledWith(mockContent.id, file);
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Content updated and file replaced successfully', 'Close', { duration: 3000 });
    });

    it('should handle file upload error after update', async () => {
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseContentSpy.updateContent.and.returnValue(of(mockContent));
      courseContentSpy.uploadFile.and.returnValue(throwError(() => ({ error: { detail: 'Upload failed' } })));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const updateFixture = TestBed.createComponent(ContentDialogComponent);
      const updateComponent = updateFixture.componentInstance;
      // ngOnInit is called automatically, don't need detectChanges() for component logic tests
      if (!updateComponent.contentForm.get('title')?.value) {
        updateComponent.ngOnInit();
      }
      
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      updateComponent.selectedFile = file;
      updateComponent.contentForm.patchValue({
        title: 'Updated Content',
        content_type: CourseContentType.DOCUMENT
      });
      updateComponent.onSubmit();

      expect(matSnackBarSpy.open).toHaveBeenCalledWith(
        jasmine.stringContaining('Content updated but file replacement failed'),
        'Close',
        jasmine.any(Object)
      );
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(mockContent);
    });

    it('should handle update error', async () => {
      const courseContentSpy = jasmine.createSpyObj('CourseContentService', ['createContent', 'updateContent', 'uploadFile']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      const error = { error: { detail: 'Error updating content' }, status: 400 };
      courseContentSpy.updateContent.and.returnValue(throwError(() => error));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [ContentDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule,
          MatSelectModule
        ],
        providers: [
          { provide: CourseContentService, useValue: courseContentSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { courseId: 1, modules: [mockModule], content: mockContent } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const updateFixture = TestBed.createComponent(ContentDialogComponent);
      const updateComponent = updateFixture.componentInstance;
      // ngOnInit is called automatically, don't need detectChanges() for component logic tests
      if (!updateComponent.contentForm.get('title')?.value) {
        updateComponent.ngOnInit();
      }

      updateComponent.contentForm.patchValue({
        title: 'Updated Content'
      });
      updateComponent.onSubmit();

      expect(updateComponent.isLoading).toBe(false);
      // Component uses error.detail if present, otherwise falls back to status-based message
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Error updating content', 'Close', jasmine.objectContaining({
        duration: 5000,
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['error-snackbar']
      }));
    });
  });

  describe('onCancel', () => {
    it('should close dialog', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });
  });

  describe('File handling', () => {
    it('should handle file selection', () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      const event = {
        target: {
          files: [file]
        }
      } as any;

      component.onFileSelected(event);

      expect(component.selectedFile).toBe(file);
    });

    it('should handle empty file selection', () => {
      const event = {
        target: {
          files: []
        }
      } as any;

      component.onFileSelected(event);

      expect(component.selectedFile).toBeNull();
    });

    it('should get file name', () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      component.selectedFile = file;

      expect(component.getFileName()).toBe('test.pdf');
    });

    it('should return default message when no file selected', () => {
      component.selectedFile = null;
      expect(component.getFileName()).toBe('No file selected');
    });

    it('should format file size', () => {
      expect(component.formatFileSize(1024)).toBe('1 KB');
      expect(component.formatFileSize(1048576)).toBe('1 MB');
      expect(component.formatFileSize(0)).toBe('0 Bytes');
    });

    it('should return 0 Bytes for undefined', () => {
      expect(component.formatFileSize(undefined)).toBe('0 Bytes');
    });

    it('should check if content type requires file', () => {
      expect(component.requiresFile(CourseContentType.DOCUMENT)).toBe(true);
      expect(component.requiresFile(CourseContentType.VIDEO)).toBe(true);
      expect(component.requiresFile(CourseContentType.EXTERNAL_LINK)).toBe(false);
      expect(component.requiresFile(CourseContentType.EMBEDDED)).toBe(false);
    });
  });

  describe('Helper methods', () => {
    it('should get content type display name', () => {
      expect(component.getContentTypeDisplayName(CourseContentType.DOCUMENT)).toBe('Document');
      expect(component.getContentTypeDisplayName(CourseContentType.VIDEO)).toBe('Video');
      expect(component.getContentTypeDisplayName(CourseContentType.AUDIO)).toBe('Audio');
      expect(component.getContentTypeDisplayName(CourseContentType.IMAGE)).toBe('Image');
      expect(component.getContentTypeDisplayName(CourseContentType.EXTERNAL_LINK)).toBe('External Link');
      expect(component.getContentTypeDisplayName(CourseContentType.EMBEDDED)).toBe('Embedded Content');
    });

    it('should return Unknown for unknown type', () => {
      expect(component.getContentTypeDisplayName('unknown' as CourseContentType)).toBe('Unknown');
    });

    it('should show error when field is invalid and touched', () => {
      const field = component.contentForm.get('title');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('title')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.contentForm.get('title');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('title')).toBe(true);
    });
  });
});
