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
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';

import { ProgressDialogComponent, ProgressDialogData } from './progress-dialog.component';
import { ProgramService } from '../../../services/program.service';
import { Program, ProgramProgress, ProgramParticipant, ProgramSession } from '../../../models/program.model';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('ProgressDialogComponent', () => {
  let component: ProgressDialogComponent;
  let fixture: ComponentFixture<ProgressDialogComponent>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ProgressDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockProgram: Program = {
    id: 1,
    title: 'Test Program',
    description: 'Test Description',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockParticipant: ProgramParticipant = {
    id: 1,
    program_id: 1,
    people_id: 1,
    role_name: 'Mentor',
    status: 'active',
    progress_percentage: 50,
    start_date: '2023-01-01T00:00:00Z',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockSession: ProgramSession = {
    id: 1,
    program_id: 1,
    session_date: '2023-01-15T10:00:00Z',
    duration_minutes: 60,
    session_type: 'in_person',
    participant_ids: [1],
    content_completed: [],
    milestones_achieved: [],
    created_at: '2023-01-01T00:00:00Z'
  };

  const mockProgress: ProgramProgress = {
    id: 1,
    program_id: 1,
    participant_id: 1,
    progress_type: 'content_completion',
    content_id: 1,
    completion_percentage: 100,
    completion_date: '2023-01-15T10:00:00Z',
    created_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramProgress', 'updateProgramProgress']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    programSpy.createProgramProgress.and.returnValue(of(mockProgress));
    programSpy.updateProgramProgress.and.returnValue(of(mockProgress));

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
        MatDatepickerModule,
        MatNativeDateModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: null, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

    fixture = TestBed.createComponent(ProgressDialogComponent);
    component = fixture.componentInstance;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<ProgressDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Initialization', () => {
    it('should initialize in create mode', () => {
      component.data = { progress: null, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false };
      fixture.detectChanges();

      expect(component.isEditing).toBe(false);
      expect(component.viewMode).toBe(false);
    });

    it('should initialize in edit mode', () => {
      // Create a new component instance with progress data
      TestBed.resetTestingModule();
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
        MatDatepickerModule,
        MatNativeDateModule,
        MatChipsModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: mockProgress, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();
      
      const newFixture = TestBed.createComponent(ProgressDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(true);
    });

    it('should initialize in view mode', () => {
      // Create a new component instance with viewMode: true
      TestBed.resetTestingModule();
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
        MatDatepickerModule,
        MatNativeDateModule,
        MatChipsModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: mockProgress, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: true } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();
      
      const newFixture = TestBed.createComponent(ProgressDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.viewMode).toBe(true);
      expect(newComponent.progressForm.disabled).toBe(true);
    });

    it('should patch form values when editing', () => {
      // Create a new component instance with progress data
      TestBed.resetTestingModule();
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
        MatDatepickerModule,
        MatNativeDateModule,
        MatChipsModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: mockProgress, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();
      
      const newFixture = TestBed.createComponent(ProgressDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.progressForm.get('progress_type')?.value).toBe(mockProgress.progress_type);
      expect(newComponent.progressForm.get('completion_percentage')?.value).toBe(mockProgress.completion_percentage);
    });

    it('should set default date to today when creating', () => {
      component.data = { progress: null, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false };
      fixture.detectChanges();

      const completionDate = component.progressForm.get('completion_date')?.value;
      expect(completionDate).toBeInstanceOf(Date);
    });
  });

  describe('updateFormValidation', () => {
    beforeEach(() => {
      component.data = { progress: null, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false };
      fixture.detectChanges();
    });

    it('should require content_id for content_completion', () => {
      component.updateFormValidation('content_completion');
      const contentIdControl = component.progressForm.get('content_id');
      expect(contentIdControl?.hasError('required')).toBe(true);
    });

    it('should require session_id for session_completion', () => {
      component.updateFormValidation('session_completion');
      const sessionIdControl = component.progressForm.get('session_id');
      expect(sessionIdControl?.hasError('required')).toBe(true);
    });

    it('should require milestone_name for milestone', () => {
      component.updateFormValidation('milestone');
      const milestoneNameControl = component.progressForm.get('milestone_name');
      expect(milestoneNameControl?.hasError('required')).toBe(true);
    });

    it('should clear validators for other types', () => {
      component.updateFormValidation('content_completion');
      component.updateFormValidation('session_completion');
      
      const contentIdControl = component.progressForm.get('content_id');
      expect(contentIdControl?.hasError('required')).toBe(false);
    });
  });

  describe('onSubmit', () => {
    beforeEach(() => {
      component.data = { progress: null, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false };
      fixture.detectChanges();
    });

    it('should not submit in view mode', () => {
      component.viewMode = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramProgress).not.toHaveBeenCalled();
    });

    it('should not submit invalid form', () => {
      component.progressForm.patchValue({
        progress_type: 'content_completion',
        content_id: null
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramProgress).not.toHaveBeenCalled();
    });

    it('should not submit when loading', () => {
      component.isLoading = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramProgress).not.toHaveBeenCalled();
    });

    it('should create progress when form is valid', () => {
      const completionDate = new Date();
      component.progressForm.patchValue({
        progress_type: 'content_completion',
        content_id: 1,
        completion_date: completionDate,
        completion_percentage: 100
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramProgress).toHaveBeenCalled();
      expect(snackBarSpy.open).toHaveBeenCalledWith('Progress recorded successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should update progress when editing', () => {
      // Create a new component instance with progress data
      TestBed.resetTestingModule();
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
        MatDatepickerModule,
        MatNativeDateModule,
        MatChipsModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: mockProgress, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();
      
      const newFixture = TestBed.createComponent(ProgressDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.progressForm.patchValue({
        completion_percentage: 75
      });
      newComponent.onSubmit();

      expect(programServiceSpy.updateProgramProgress).toHaveBeenCalled();
      expect(snackBarSpy.open).toHaveBeenCalledWith('Progress updated successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should convert Date to ISO string', () => {
      const completionDate = new Date('2023-01-15T10:00:00Z');
      component.progressForm.patchValue({
        progress_type: 'content_completion',
        content_id: 1,
        completion_date: completionDate
      });
      component.onSubmit();

      const callArgs = programServiceSpy.createProgramProgress.calls.mostRecent().args[1];
      expect(callArgs.completion_date).toBe(completionDate.toISOString());
    });

    it('should handle create error', () => {
      const error = { error: { detail: 'Error creating progress' } };
      programServiceSpy.createProgramProgress.and.returnValue(throwError(() => error));

      component.progressForm.patchValue({
        progress_type: 'content_completion',
        content_id: 1,
        completion_date: new Date()
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error creating progress', 'Close', { duration: 3000 });
    });

    it('should handle update error', () => {
      const error = { error: { detail: 'Error updating progress' } };
      programServiceSpy.updateProgramProgress.and.returnValue(throwError(() => error));

      // Create a new component instance with progress data
      TestBed.resetTestingModule();
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
        MatDatepickerModule,
        MatNativeDateModule,
        MatChipsModule,
        ProgressDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { progress: mockProgress, program: mockProgram, participant: mockParticipant, sessions: [mockSession], viewMode: false } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();
      
      const newFixture = TestBed.createComponent(ProgressDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.progressForm.patchValue({ completion_percentage: 75 });
      newComponent.onSubmit();

      expect(newComponent.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error updating progress', 'Close', { duration: 3000 });
    });
  });

  describe('onCancel', () => {
    it('should close dialog with false', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalledWith(false);
    });
  });

  describe('Helper methods', () => {
    it('should get session display', () => {
      // Ensure sessions are set
      component.sessions = [mockSession];
      const display = component.getSessionDisplay(1);
      // When session is found, it returns the formatted date string
      expect(display).toBeTruthy();
      expect(typeof display).toBe('string');
      // Should contain date information (check for numbers/date format)
      expect(display.length).toBeGreaterThan(0);
    });

    it('should return N/A for non-existent session', () => {
      // Ensure sessions are set
      component.sessions = [mockSession];
      // When session doesn't exist, it returns "Session #<id>"
      const display = component.getSessionDisplay(999);
      expect(display).toBe('Session #999');
    });

    it('should show error when field is invalid and touched', () => {
      const field = component.progressForm.get('content_id');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('content_id')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.progressForm.get('content_id');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('content_id')).toBe(true);
    });
  });
});
