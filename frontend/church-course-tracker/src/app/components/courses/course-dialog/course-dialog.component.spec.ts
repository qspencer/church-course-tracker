import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { CourseDialogComponent, CourseDialogData } from './course-dialog.component';
import { CourseService } from '../../../services/course.service';
import { Course } from '../../../models';

describe('CourseDialogComponent', () => {
  let component: CourseDialogComponent;
  let fixture: ComponentFixture<CourseDialogComponent>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<CourseDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockCourse: Course = {
    id: 1,
    title: 'Test Course',
    description: 'Test Description',
    duration_weeks: 4,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const createMockDialogData = (): CourseDialogData => ({
    course: { ...mockCourse }
  });

  beforeEach(async () => {
    const courseSpy = jasmine.createSpyObj('CourseService', ['createCourse', 'updateCourse']);
    // Set up default return values for the service methods
    courseSpy.createCourse.and.returnValue(of(mockCourse));
    courseSpy.updateCourse.and.returnValue(of(mockCourse));
    
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [CourseDialogComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatProgressSpinnerModule
      ],
      providers: [
        { provide: CourseService, useValue: courseSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useFactory: createMockDialogData },
        { provide: MatSnackBar, useValue: matSnackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(CourseDialogComponent);
    component = fixture.componentInstance;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<CourseDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize in editing mode when course provided', () => {
    // Verify the data was injected correctly
    expect(component.data).toBeDefined();
    expect(component.data.course).toBeDefined();
    expect(component.data.course).toEqual(mockCourse);
    
    // Trigger change detection to ensure component is fully initialized
    fixture.detectChanges();
    
    // The component should be in editing mode because mockDialogData.course is set
    // isEditing is set in constructor based on data.course
    expect(component.isEditing).toBe(true);
    expect(component.course).toEqual(mockCourse);
    
    // Check that the form exists and is populated with course data after ngOnInit
    expect(component.courseForm).toBeDefined();
    const titleControl = component.courseForm.get('title');
    const descriptionControl = component.courseForm.get('description');
    const durationControl = component.courseForm.get('duration_weeks');
    
    expect(titleControl).toBeDefined();
    expect(descriptionControl).toBeDefined();
    expect(durationControl).toBeDefined();
    
    expect(titleControl?.value).toBe(mockCourse.title);
    expect(descriptionControl?.value).toBe(mockCourse.description);
    expect(durationControl?.value).toBe(mockCourse.duration_weeks);
  });

  describe('form initialization', () => {
    it('should initialize form with validators', () => {
      // Don't call detectChanges() as it triggers ngOnInit which patches the form
      // Check the form state before ngOnInit is called
      expect(component.courseForm.get('title')?.hasError('required')).toBe(true);
      expect(component.courseForm.get('description')?.hasError('required')).toBe(true);
      expect(component.courseForm.get('duration_weeks')?.hasError('required')).toBe(false);
    });

    it('should patch form values when editing', () => {
      // Recreate component with edit mode data
      TestBed.resetTestingModule();
      const editDialogData = { course: { ...mockCourse } };
      const editCourseSpy = jasmine.createSpyObj('CourseService', ['createCourse', 'updateCourse']);
      const editMatDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const editMatSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
      
      TestBed.configureTestingModule({
        declarations: [CourseDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule
        ],
        providers: [
          { provide: CourseService, useValue: editCourseSpy },
          { provide: MatDialogRef, useValue: editMatDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: editDialogData },
          { provide: MatSnackBar, useValue: editMatSnackBarSpy }
        ]
      }).compileComponents();
      
      const editFixture = TestBed.createComponent(CourseDialogComponent);
      const editComponent = editFixture.componentInstance;
      editFixture.detectChanges();

      expect(editComponent.courseForm.get('title')?.value).toBe(mockCourse.title);
      expect(editComponent.courseForm.get('description')?.value).toBe(mockCourse.description);
      expect(editComponent.courseForm.get('duration_weeks')?.value).toBe(mockCourse.duration_weeks);
    });
  });

  describe('onSubmit for editing', () => {
    beforeEach(() => {
      // Ensure component is in editing mode
      component.isEditing = true;
      component.data.course = { ...mockCourse };
      
      component.courseForm.patchValue({
        title: 'Updated Course',
        description: 'Updated Description',
        duration_weeks: 6
      });
    });

    it('should update course when editing', () => {
      courseServiceSpy.updateCourse.and.returnValue(of(mockCourse));

      component.onSubmit();

      expect(courseServiceSpy.updateCourse).toHaveBeenCalledWith(1, {
        title: 'Updated Course',
        description: 'Updated Description',
        duration_weeks: 6
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Course updated successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockCourse);
    });

    it('should handle update error', () => {
      courseServiceSpy.updateCourse.and.returnValue(throwError(() => new Error('Update error')));
      spyOn(console, 'error');

      component.onSubmit();

      expect(console.error).toHaveBeenCalledWith('Error updating course:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('onSubmit for creating', () => {
    beforeEach(() => {
      // Reset to create mode
      component.data.course = null;
      component.isEditing = false;
      component.courseForm.patchValue({
        title: 'New Course',
        description: 'New Description',
        duration_weeks: 8
      });
    });

    it('should create course when not editing', () => {
      courseServiceSpy.createCourse.and.returnValue(of(mockCourse));

      component.onSubmit();

      expect(courseServiceSpy.createCourse).toHaveBeenCalledWith({
        title: 'New Course',
        description: 'New Description',
        duration_weeks: 8
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Course created successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockCourse);
    });

    it('should handle create error', () => {
      courseServiceSpy.createCourse.and.returnValue(throwError(() => new Error('Create error')));
      spyOn(console, 'error');

      component.onSubmit();

      expect(console.error).toHaveBeenCalledWith('Error creating course:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('form validation', () => {
    it('should not submit if form is invalid', () => {
      component.courseForm.patchValue({
        title: '',
        description: '',
        duration_weeks: null
      });

      component.onSubmit();

      expect(courseServiceSpy.createCourse).not.toHaveBeenCalled();
      expect(courseServiceSpy.updateCourse).not.toHaveBeenCalled();
    });

    it('should validate minimum duration', () => {
      component.courseForm.patchValue({
        duration_weeks: 0
      });

      expect(component.courseForm.get('duration_weeks')?.hasError('min')).toBe(true);
    });

    it('should validate maximum duration', () => {
      component.courseForm.patchValue({
        duration_weeks: 60
      });

      expect(component.courseForm.get('duration_weeks')?.hasError('max')).toBe(true);
    });
  });

  describe('getErrorMessage', () => {
    it('should return required error message', () => {
      const message = component.getErrorMessage('title');
      expect(message).toBe('title is required');
    });

    it('should return minlength error message', () => {
      component.courseForm.get('title')?.setValue('ab');
      const message = component.getErrorMessage('title');
      expect(message).toBe('title must be at least 3 characters');
    });

    it('should return min value error message', () => {
      component.courseForm.get('duration_weeks')?.setValue(0);
      const message = component.getErrorMessage('duration_weeks');
      expect(message).toBe('duration_weeks must be at least 1');
    });

    it('should return max value error message', () => {
      component.courseForm.get('duration_weeks')?.setValue(60);
      const message = component.getErrorMessage('duration_weeks');
      expect(message).toBe('duration_weeks must be at most 52');
    });
  });

  describe('onCancel', () => {
    it('should close dialog without data', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalledWith();
    });
  });

  describe('template rendering', () => {
    let editComponent: CourseDialogComponent;
    let editFixture: ComponentFixture<CourseDialogComponent>;

    beforeEach(async () => {
      // Recreate component with edit mode data
      TestBed.resetTestingModule();
      const editDialogData = { course: { ...mockCourse } };
      const editCourseSpy = jasmine.createSpyObj('CourseService', ['createCourse', 'updateCourse']);
      const editMatDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const editMatSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
      
      await TestBed.configureTestingModule({
        declarations: [CourseDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule
        ],
        providers: [
          { provide: CourseService, useValue: editCourseSpy },
          { provide: MatDialogRef, useValue: editMatDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: editDialogData },
          { provide: MatSnackBar, useValue: editMatSnackBarSpy }
        ]
      }).compileComponents();
      
      editFixture = TestBed.createComponent(CourseDialogComponent);
      editComponent = editFixture.componentInstance;
      editFixture.detectChanges();
    });

    it('should display correct title for editing', () => {
      const compiled = editFixture.nativeElement;
      const titleElement = compiled.querySelector('h2');
      expect(titleElement).toBeTruthy();
      expect(titleElement.textContent.trim()).toBe('Edit Course');
    });

    it('should display correct button text for editing', () => {
      const compiled = editFixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton).toBeTruthy();
      expect(submitButton.textContent.trim()).toBe('Update');
    });

    it('should show loading spinner when loading', () => {
      editComponent.isLoading = true;
      editFixture.detectChanges();

      const compiled = editFixture.nativeElement;
      const spinner = compiled.querySelector('mat-spinner');
      expect(spinner).toBeTruthy();
    });
  });

  describe('create mode', () => {
    let createComponent: CourseDialogComponent;
    let createFixture: ComponentFixture<CourseDialogComponent>;

    beforeEach(async () => {
      // Reset TestBed
      TestBed.resetTestingModule();
      
      // Create a separate test setup for create mode
      const createDialogData = { course: null };
      const createCourseSpy = jasmine.createSpyObj('CourseService', ['createCourse', 'updateCourse']);
      const createMatDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const createMatSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
      
      await TestBed.configureTestingModule({
        declarations: [CourseDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule
        ],
        providers: [
          { provide: CourseService, useValue: createCourseSpy },
          { provide: MatDialogRef, useValue: createMatDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: createDialogData },
          { provide: MatSnackBar, useValue: createMatSnackBarSpy }
        ]
      }).compileComponents();

      createFixture = TestBed.createComponent(CourseDialogComponent);
      createComponent = createFixture.componentInstance;
      createFixture.detectChanges();
    });

    it('should initialize in create mode', () => {
      expect(createComponent.isEditing).toBe(false);
    });

    it('should display correct title for creating', () => {
      const compiled = createFixture.nativeElement;
      expect(compiled.querySelector('h2').textContent.trim()).toBe('Create New Course');
    });

    it('should display correct button text for creating', () => {
      const compiled = createFixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton.textContent.trim()).toBe('Create');
    });
  });
});
