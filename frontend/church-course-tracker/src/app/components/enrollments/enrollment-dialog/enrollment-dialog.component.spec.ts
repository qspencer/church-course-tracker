import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError, forkJoin } from 'rxjs';
import { fakeAsync, tick } from '@angular/core/testing';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatCardModule } from '@angular/material/card';

import { EnrollmentDialogComponent, EnrollmentDialogData } from './enrollment-dialog.component';
import { EnrollmentService } from '../../../services/enrollment.service';
import { CourseService } from '../../../services/course.service';
import { MemberService } from '../../../services/member.service';
import { Enrollment, EnrollmentStatus, Course, Person } from '../../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('EnrollmentDialogComponent', () => {
  let component: EnrollmentDialogComponent;
  let fixture: ComponentFixture<EnrollmentDialogComponent>;
  let enrollmentServiceSpy: jasmine.SpyObj<EnrollmentService>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let memberServiceSpy: jasmine.SpyObj<MemberService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<EnrollmentDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockCourse: Course = {
    id: 1,
    title: 'Test Course',
    description: 'Test Description',
    duration_weeks: 12,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockMember: Person = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    planning_center_id: 'pc123',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockEnrollment: Enrollment = {
    id: 1,
    person_id: 1,
    course_id: 1,
    status: EnrollmentStatus.ENROLLED,
    progress_percentage: 50,
    enrolled_at: '2023-01-01T00:00:00Z',
    completion_date: null,
    notes: null,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    person: mockMember,
    course: mockCourse
  };

  beforeEach(async () => {
    const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    enrollmentSpy.createEnrollment.and.returnValue(of(mockEnrollment));
    enrollmentSpy.updateEnrollment.and.returnValue(of(mockEnrollment));
    courseSpy.getCourses.and.returnValue(of([mockCourse]));
    memberSpy.getMembers.and.returnValue(of([mockMember]));

    await TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: null, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

    fixture = TestBed.createComponent(EnrollmentDialogComponent);
    component = fixture.componentInstance;
    enrollmentServiceSpy = TestBed.inject(EnrollmentService) as jasmine.SpyObj<EnrollmentService>;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    memberServiceSpy = TestBed.inject(MemberService) as jasmine.SpyObj<MemberService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<EnrollmentDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Initialization', () => {
    it('should initialize in create mode when no enrollment provided', () => {
      // Component already initialized with null enrollment in beforeEach
      expect(component.isEditing).toBe(false);
      expect(component.viewMode).toBe(false);
      expect(component.enrollmentForm).toBeDefined();
    });

    it('should initialize in edit mode when enrollment provided', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseSpy.getCourses.and.returnValue(of([mockCourse]));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: mockEnrollment, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(true);
      expect(newComponent.viewMode).toBe(false);
    });

    it('should initialize in view mode when viewMode is true', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: mockEnrollment, viewMode: true } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.viewMode).toBe(true);
      expect(newComponent.enrollmentForm.disabled).toBe(true);
    });

    it('should load courses and members on init when not in view mode', fakeAsync(() => {
      // Component already initialized in beforeEach with detectChanges, so services should have been called
      tick(); // Process async operations
      
      expect(courseServiceSpy.getCourses).toHaveBeenCalledWith({ is_active: true });
      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
      expect(component.courses.length).toBeGreaterThan(0);
      expect(component.members.length).toBeGreaterThan(0);
    }));

    it('should not load data in view mode', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: mockEnrollment, viewMode: true } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      newFixture.detectChanges();

      expect(courseSpy.getCourses).not.toHaveBeenCalled();
      expect(memberSpy.getMembers).not.toHaveBeenCalled();
    });

    it('should patch form values when editing', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      courseSpy.getCourses.and.returnValue(of([mockCourse]));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: mockEnrollment, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.enrollmentForm.get('person_id')?.value).toBe(mockEnrollment.person_id);
      expect(newComponent.enrollmentForm.get('course_id')?.value).toBe(mockEnrollment.course_id);
      expect(newComponent.enrollmentForm.get('status')?.value).toBe(mockEnrollment.status);
    });
  });

  describe('loadData', () => {
    it('should load courses and members successfully', fakeAsync(() => {
      // Component already initialized in beforeEach with detectChanges, process async operations
      tick();
      
      expect(component.courses).toEqual([mockCourse]);
      expect(component.members).toEqual([mockMember]);
      expect(component.isLoading).toBe(false);
    }));

    it('should handle error loading data', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      const error = new Error('Failed to load');
      courseSpy.getCourses.and.returnValue(throwError(() => error));
      memberSpy.getMembers.and.returnValue(throwError(() => error));

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: null, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isLoading).toBe(false);
    });
  });

  describe('onSubmit', () => {
    // Component already initialized in main beforeEach with enrollment: null, viewMode: false

    it('should not submit in view mode', () => {
      component.viewMode = true;
      component.onSubmit();

      expect(enrollmentServiceSpy.createEnrollment).not.toHaveBeenCalled();
      expect(enrollmentServiceSpy.updateEnrollment).not.toHaveBeenCalled();
    });

    it('should mark form as submitted', () => {
      component.enrollmentForm.patchValue({
        person_id: '',
        course_id: '',
        status: EnrollmentStatus.ENROLLED
      });
      component.onSubmit();

      expect(component.isSubmitted).toBe(true);
    });

    it('should not submit invalid form', () => {
      component.enrollmentForm.patchValue({
        person_id: '',
        course_id: '',
        status: EnrollmentStatus.ENROLLED
      });
      component.onSubmit();

      expect(enrollmentServiceSpy.createEnrollment).not.toHaveBeenCalled();
    });

    it('should create enrollment when form is valid', () => {
      component.enrollmentForm.patchValue({
        person_id: 1,
        course_id: 1,
        status: EnrollmentStatus.ENROLLED
      });
      component.onSubmit();

      expect(enrollmentServiceSpy.createEnrollment).toHaveBeenCalledWith({
        person_id: 1,
        course_id: 1
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Enrollment created successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockEnrollment);
    });

    it('should update enrollment when editing', () => {
      TestBed.resetTestingModule();
      const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['createEnrollment', 'updateEnrollment']);
      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      enrollmentSpy.updateEnrollment.and.returnValue(of(mockEnrollment));
      courseSpy.getCourses.and.returnValue(of([mockCourse]));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      TestBed.configureTestingModule({
    imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatProgressBarModule,
        MatCardModule,
        EnrollmentDialogComponent
    ],
    providers: [
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { enrollment: mockEnrollment, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

      const newFixture = TestBed.createComponent(EnrollmentDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.enrollmentForm.patchValue({
        status: EnrollmentStatus.COMPLETED
      });
      newComponent.onSubmit();

      expect(enrollmentSpy.updateEnrollment).toHaveBeenCalledWith(mockEnrollment.id, {
        status: EnrollmentStatus.COMPLETED
      });
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Enrollment updated successfully', 'Close', { duration: 3000 });
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(mockEnrollment);
    });

    it('should handle create enrollment error', () => {
      const error = { error: { detail: 'Error creating enrollment' } };
      enrollmentServiceSpy.createEnrollment.and.returnValue(throwError(() => error));

      component.enrollmentForm.patchValue({
        person_id: 1,
        course_id: 1,
        status: EnrollmentStatus.ENROLLED
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
    });

    it('should handle update enrollment error', () => {
      const error = { error: { detail: 'Error updating enrollment' } };
      enrollmentServiceSpy.updateEnrollment.and.returnValue(throwError(() => error));

      component.data = { enrollment: mockEnrollment, viewMode: false };
      fixture.detectChanges();

      component.enrollmentForm.patchValue({
        status: EnrollmentStatus.COMPLETED
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
    });
  });

  describe('onCancel', () => {
    it('should close dialog', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });
  });

  describe('Helper methods', () => {
    it('should get error message for required field', () => {
      const field = component.enrollmentForm.get('person_id');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      const error = component.getErrorMessage('person_id');
      expect(error).toContain('person id');
    });

    it('should return empty string when no error', () => {
      // Form is valid by default in create mode, so no error
      component.enrollmentForm.patchValue({ person_id: 1, course_id: 1 });
      const error = component.getErrorMessage('person_id');
      expect(error).toBe('');
    });

    it('should show error when field is invalid and touched', () => {
      const field = component.enrollmentForm.get('person_id');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('person_id')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.enrollmentForm.get('person_id');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('person_id')).toBe(true);
    });

    it('should not show error when field is valid', () => {
      component.enrollmentForm.patchValue({ person_id: 1 });
      expect(component.shouldShowError('person_id')).toBe(false);
    });

    it('should get person display name', () => {
      const displayName = component.getPersonDisplayName(mockMember);
      expect(displayName).toBe('John Doe');
    });

    it('should get course display name with duration', () => {
      const displayName = component.getCourseDisplayName(mockCourse);
      expect(displayName).toBe('Test Course (12 weeks)');
    });

    it('should get course display name without duration', () => {
      const courseWithoutDuration = { ...mockCourse, duration_weeks: undefined as any };
      const displayName = component.getCourseDisplayName(courseWithoutDuration);
      expect(displayName).toBe('Test Course');
    });

    it('should get status label', () => {
      const label = component.getStatusLabel(EnrollmentStatus.COMPLETED);
      expect(label).toBe('Completed');
    });

    it('should return status as-is when not found', () => {
      const label = component.getStatusLabel('unknown_status');
      expect(label).toBe('unknown_status');
    });

    it('should get status color for completed', () => {
      const color = component.getStatusColor(EnrollmentStatus.COMPLETED);
      expect(color).toBe('primary');
    });

    it('should get status color for in_progress', () => {
      const color = component.getStatusColor(EnrollmentStatus.IN_PROGRESS);
      expect(color).toBe('accent');
    });

    it('should get status color for dropped', () => {
      const color = component.getStatusColor(EnrollmentStatus.DROPPED);
      expect(color).toBe('warn');
    });

    it('should return undefined for enrolled status', () => {
      const color = component.getStatusColor(EnrollmentStatus.ENROLLED);
      expect(color).toBeUndefined();
    });

    it('should return undefined for null status', () => {
      const color = component.getStatusColor(null as any);
      expect(color).toBeUndefined();
    });

    it('should format valid date', () => {
      const dateStr = '2023-01-15T10:30:00Z';
      const formatted = component.formatDate(dateStr);
      expect(formatted).toContain('January');
      expect(formatted).toContain('2023');
    });

    it('should format Date object', () => {
      const date = new Date('2023-01-15T10:30:00Z');
      const formatted = component.formatDate(date);
      expect(formatted).toContain('January');
      expect(formatted).toContain('2023');
    });

    it('should return N/A for null date', () => {
      const formatted = component.formatDate(null);
      expect(formatted).toBe('N/A');
    });

    it('should return N/A for undefined date', () => {
      const formatted = component.formatDate(undefined);
      expect(formatted).toBe('N/A');
    });

    it('should return N/A for invalid date string', () => {
      const formatted = component.formatDate('invalid-date');
      expect(formatted).toBe('N/A');
    });
  });
});
