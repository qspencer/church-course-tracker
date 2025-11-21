import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { ModuleDialogComponent, ModuleDialogData } from './module-dialog.component';
import { CourseContentService } from '../../../services/course-content.service';
import { CourseModule } from '../../../models';

describe('ModuleDialogComponent', () => {
  let component: ModuleDialogComponent;
  let fixture: ComponentFixture<ModuleDialogComponent>;
  let courseContentService: jasmine.SpyObj<CourseContentService>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<ModuleDialogComponent>>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

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

  const mockDialogData: ModuleDialogData = {
    courseId: 1
  };

  const mockEditDialogData: ModuleDialogData = {
    courseId: 1,
    module: mockModule
  };

  beforeEach(async () => {
    const courseContentServiceSpy = jasmine.createSpyObj('CourseContentService', [
      'createModule',
      'updateModule'
    ]);
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [ModuleDialogComponent],
      imports: [
        ReactiveFormsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatSnackBarModule,
        NoopAnimationsModule
      ],
      providers: [
        FormBuilder,
        { provide: CourseContentService, useValue: courseContentServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ModuleDialogComponent);
    component = fixture.componentInstance;
    courseContentService = TestBed.inject(CourseContentService) as jasmine.SpyObj<CourseContentService>;
    dialogRef = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<ModuleDialogComponent>>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize form in create mode', () => {
      // Recreate component with create mode data
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ModuleDialogComponent],
        imports: [
          ReactiveFormsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatSnackBarModule,
          NoopAnimationsModule
        ],
        providers: [
          FormBuilder,
          { provide: CourseContentService, useValue: courseContentService },
          { provide: MatDialogRef, useValue: dialogRef },
          { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
          { provide: MatSnackBar, useValue: snackBar }
        ]
      }).compileComponents();
      
      fixture = TestBed.createComponent(ModuleDialogComponent);
      component = fixture.componentInstance;
      component.ngOnInit();
      
      expect(component.isEditing).toBe(false);
      expect(component.moduleForm).toBeDefined();
      expect(component.moduleForm.get('title')?.value).toBe('');
    });

    it('should initialize form in edit mode with module data', () => {
      // Recreate component with edit mode data
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ModuleDialogComponent],
        imports: [
          ReactiveFormsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatSnackBarModule,
          NoopAnimationsModule
        ],
        providers: [
          FormBuilder,
          { provide: CourseContentService, useValue: courseContentService },
          { provide: MatDialogRef, useValue: dialogRef },
          { provide: MAT_DIALOG_DATA, useValue: mockEditDialogData },
          { provide: MatSnackBar, useValue: snackBar }
        ]
      }).compileComponents();
      
      fixture = TestBed.createComponent(ModuleDialogComponent);
      component = fixture.componentInstance;
      component.ngOnInit();
      
      expect(component.isEditing).toBe(true);
      expect(component.moduleForm.get('title')?.value).toBe('Test Module');
      expect(component.moduleForm.get('description')?.value).toBe('Test Description');
      expect(component.moduleForm.get('order_index')?.value).toBe(1);
    });
  });

  describe('Form Validation', () => {
    beforeEach(() => {
      component.ngOnInit();
    });

    it('should require title', () => {
      const titleControl = component.moduleForm.get('title');
      titleControl?.setValue('');
      expect(titleControl?.hasError('required')).toBe(true);
      
      titleControl?.setValue('Valid Title');
      expect(titleControl?.hasError('required')).toBe(false);
    });

    it('should validate order_index minimum value', () => {
      const orderControl = component.moduleForm.get('order_index');
      orderControl?.setValue(-1);
      expect(orderControl?.hasError('min')).toBe(true);
      
      orderControl?.setValue(0);
      expect(orderControl?.hasError('min')).toBe(false);
    });

    it('should get error message for required field', () => {
      component.moduleForm.get('title')?.setValue('');
      component.moduleForm.get('title')?.markAsTouched();
      
      const errorMessage = component.getErrorMessage('title');
      expect(errorMessage).toBe('title is required');
    });
  });

  describe('Create Module', () => {
    beforeEach(() => {
      component.data = mockDialogData;
      component.ngOnInit();
      component.moduleForm.patchValue({
        title: 'New Module',
        description: 'New Description',
        order_index: 0
      });
    });

    it('should create module successfully', () => {
      const createdModule = { ...mockModule, title: 'New Module' };
      courseContentService.createModule.and.returnValue(of(createdModule));
      
      component.onSubmit();
      
      expect(courseContentService.createModule).toHaveBeenCalledWith(jasmine.objectContaining({
        course_id: 1,
        title: 'New Module',
        description: 'New Description',
        order_index: 0
      }));
      expect(dialogRef.close).toHaveBeenCalledWith(createdModule);
    });

    it('should handle create module error', () => {
      courseContentService.createModule.and.returnValue(throwError({ error: { detail: 'Error message' } }));
      
      component.onSubmit();
      
      expect(courseContentService.createModule).toHaveBeenCalled();
      expect(component.isSubmitting).toBe(false);
    });
  });

  describe('Update Module', () => {
    beforeEach(() => {
      // Recreate component with edit mode data
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ModuleDialogComponent],
        imports: [
          ReactiveFormsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatSnackBarModule,
          NoopAnimationsModule
        ],
        providers: [
          FormBuilder,
          { provide: CourseContentService, useValue: courseContentService },
          { provide: MatDialogRef, useValue: dialogRef },
          { provide: MAT_DIALOG_DATA, useValue: mockEditDialogData },
          { provide: MatSnackBar, useValue: snackBar }
        ]
      }).compileComponents();
      
      fixture = TestBed.createComponent(ModuleDialogComponent);
      component = fixture.componentInstance;
      component.ngOnInit();
      component.moduleForm.patchValue({
        title: 'Updated Module',
        description: 'Updated Description'
      });
    });

    it('should update module successfully', () => {
      const updatedModule = { ...mockModule, title: 'Updated Module' };
      courseContentService.updateModule.and.returnValue(of(updatedModule));
      
      component.onSubmit();
      
      expect(courseContentService.updateModule).toHaveBeenCalledWith(
        mockModule.id,
        jasmine.objectContaining({
          title: 'Updated Module',
          description: 'Updated Description'
        })
      );
      expect(dialogRef.close).toHaveBeenCalledWith(updatedModule);
    });

    it('should handle update module error', () => {
      courseContentService.updateModule.and.returnValue(throwError({ error: { detail: 'Error message' } }));
      
      component.onSubmit();
      
      expect(courseContentService.updateModule).toHaveBeenCalled();
      expect(component.isSubmitting).toBe(false);
    });
  });

  describe('Form Actions', () => {
    it('should not submit if form is invalid', () => {
      component.ngOnInit();
      component.moduleForm.patchValue({ title: '' });
      
      component.onSubmit();
      
      expect(courseContentService.createModule).not.toHaveBeenCalled();
      expect(courseContentService.updateModule).not.toHaveBeenCalled();
    });

    it('should close dialog on cancel', () => {
      component.onCancel();
      expect(dialogRef.close).toHaveBeenCalled();
    });

    it('should prevent multiple submissions', () => {
      component.data = mockDialogData;
      component.ngOnInit();
      component.moduleForm.patchValue({ title: 'Test' });
      component.isSubmitting = true;
      
      component.onSubmit();
      
      expect(courseContentService.createModule).not.toHaveBeenCalled();
    });
  });
});

