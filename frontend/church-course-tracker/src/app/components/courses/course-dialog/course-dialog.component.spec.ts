import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { CourseDialogComponent } from './course-dialog.component';
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

  const mockDialogData = {
    course: mockCourse
  };

  beforeEach(async () => {
    const courseSpy = jasmine.createSpyObj('CourseService', ['createCourse', 'updateCourse']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [CourseDialogComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatProgressSpinnerModule
      ],
      providers: [
        { provide: CourseService, useValue: courseSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
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
    expect(component.isEditing).toBe(true);
  });

  describe('form initialization', () => {
    it('should initialize form with validators', () => {
      fixture.detectChanges();
      
      expect(component.courseForm.get('title')?.hasError('required')).toBe(true);
      expect(component.courseForm.get('description')?.hasError('required')).toBe(true);
      expect(component.courseForm.get('duration_weeks')?.hasError('required')).toBe(true);
    });

    it('should patch form values when editing', () => {
      component.ngOnInit();

      expect(component.courseForm.get('title')?.value).toBe(mockCourse.title);
      expect(component.courseForm.get('description')?.value).toBe(mockCourse.description);
      expect(component.courseForm.get('duration_weeks')?.value).toBe(mockCourse.duration_weeks);
    });
  });

  describe('onSubmit for editing', () => {
    beforeEach(() => {
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
    beforeEach(() => {
      fixture.detectChanges();
    });

    it('should display correct title for editing', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('h2').textContent).toBe('Edit Course');
    });

    it('should display correct button text for editing', () => {
      const compiled = fixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton.textContent.trim()).toBe('Update');
    });

    it('should show loading spinner when loading', () => {
      component.isLoading = true;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-spinner')).toBeTruthy();
    });
  });

  describe('create mode', () => {
    beforeEach(async () => {
      // Recreate component in create mode
      const createDialogData = { course: null };
      
      TestBed.overrideProvider(MAT_DIALOG_DATA, { useValue: createDialogData });
      fixture = TestBed.createComponent(CourseDialogComponent);
      component = fixture.componentInstance;
      fixture.detectChanges();
    });

    it('should initialize in create mode', () => {
      expect(component.isEditing).toBe(false);
    });

    it('should display correct title for creating', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('h2').textContent).toBe('Create New Course');
    });

    it('should display correct button text for creating', () => {
      const compiled = fixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton.textContent.trim()).toBe('Create');
    });
  });
});
