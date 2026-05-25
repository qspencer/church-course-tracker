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

import { SessionDialogComponent, SessionDialogData } from './session-dialog.component';
import { ProgramService } from '../../../services/program.service';
import { Program, ProgramSession, ProgramPairing, ProgramParticipant } from '../../../models/program.model';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('SessionDialogComponent', () => {
  let component: SessionDialogComponent;
  let fixture: ComponentFixture<SessionDialogComponent>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<SessionDialogComponent>>;
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

  const mockPairing: ProgramPairing = {
    id: 1,
    program_id: 1,
    primary_participant_id: 1,
    secondary_participant_id: 2,
    status: 'active',
    start_date: '2023-01-01T00:00:00Z',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockSession: ProgramSession = {
    id: 1,
    program_id: 1,
    pairing_id: 1,
    session_date: '2023-01-15T10:00:00Z',
    duration_minutes: 60,
    location: 'Office',
    session_type: 'in_person',
    participant_ids: [1, 2],
    topics_covered: 'Introduction',
    notes: 'Test notes',
    content_completed: [],
    milestones_achieved: [],
    created_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    programSpy.createProgramSession.and.returnValue(of(mockSession));
    programSpy.updateProgramSession.and.returnValue(of(mockSession));

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
        SessionDialogComponent
    ],
    providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { session: null, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

    fixture = TestBed.createComponent(SessionDialogComponent);
    component = fixture.componentInstance;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<SessionDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Initialization', () => {
    it('should initialize in create mode', () => {
      // Component already initialized in beforeEach
      expect(component.isEditing).toBe(false);
      expect(component.viewMode).toBe(false);
    });

    it('should initialize in edit mode', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      await TestBed.resetTestingModule().configureTestingModule({
        imports: [
          SessionDialogComponent,
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
          MatNativeDateModule
        ],
        providers: [
          { provide: ProgramService, useValue: programSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { session: mockSession, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(SessionDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(true);
    });

    it('should initialize in view mode', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      await TestBed.resetTestingModule().configureTestingModule({
        imports: [
          SessionDialogComponent,
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
          MatNativeDateModule
        ],
        providers: [
          { provide: ProgramService, useValue: programSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { session: mockSession, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: true } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(SessionDialogComponent);
      const newComponent = newFixture.componentInstance;
      // Don't call detectChanges to avoid template rendering issues
      expect(newComponent.viewMode).toBe(true);
      expect(newComponent.sessionForm.disabled).toBe(true);
    });

    it('should patch form values when editing', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      await TestBed.resetTestingModule().configureTestingModule({
        imports: [
          SessionDialogComponent,
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
          MatNativeDateModule
        ],
        providers: [
          { provide: ProgramService, useValue: programSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { session: mockSession, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(SessionDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.sessionForm.get('session_date')?.value).toBeInstanceOf(Date);
      expect(newComponent.sessionForm.get('duration_minutes')?.value).toBe(mockSession.duration_minutes);
      expect(newComponent.sessionForm.get('location')?.value).toBe(mockSession.location);
    });

    it('should set default date to today when creating', () => {
      // Component already initialized in beforeEach
      const sessionDate = component.sessionForm.get('session_date')?.value;
      expect(sessionDate).toBeInstanceOf(Date);
    });
  });

  describe('onSubmit', () => {
    // Component already initialized in beforeEach with session: null, viewMode: false

    it('should not submit in view mode', () => {
      component.viewMode = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramSession).not.toHaveBeenCalled();
    });

    it('should not submit invalid form', () => {
      component.sessionForm.patchValue({
        session_date: null
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramSession).not.toHaveBeenCalled();
    });

    it('should not submit when loading', () => {
      component.isLoading = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramSession).not.toHaveBeenCalled();
    });

    it('should create session when form is valid', () => {
      const sessionDate = new Date();
      component.sessionForm.patchValue({
        session_date: sessionDate,
        duration_minutes: 60,
        location: 'Office',
        session_type: 'in_person',
        participant_ids: [1, 2],
        topics_covered: 'Introduction',
        notes: 'Test notes'
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramSession).toHaveBeenCalled();
      expect(snackBarSpy.open).toHaveBeenCalledWith('Session logged successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should update session when editing', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      programSpy.updateProgramSession.and.returnValue(of(mockSession));

      await TestBed.resetTestingModule().configureTestingModule({
        imports: [
          SessionDialogComponent,
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
          MatNativeDateModule
        ],
        providers: [
          { provide: ProgramService, useValue: programSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { session: mockSession, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(SessionDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.sessionForm.patchValue({
        duration_minutes: 90,
        notes: 'Updated notes'
      });
      newComponent.onSubmit();

      expect(programSpy.updateProgramSession).toHaveBeenCalled();
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Session updated successfully', 'Close', { duration: 3000 });
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should convert Date to ISO string', () => {
      const sessionDate = new Date('2023-01-15T10:00:00Z');
      component.sessionForm.patchValue({
        session_date: sessionDate,
        duration_minutes: 60
      });
      component.onSubmit();

      const callArgs = programServiceSpy.createProgramSession.calls.mostRecent().args[1];
      expect(callArgs.session_date).toBe(sessionDate.toISOString());
    });

    it('should handle create error', () => {
      const error = { error: { detail: 'Error creating session' } };
      programServiceSpy.createProgramSession.and.returnValue(throwError(() => error));

      component.sessionForm.patchValue({
        session_date: new Date(),
        duration_minutes: 60
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error creating session', 'Close', { duration: 3000 });
    });

    it('should handle update error', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramSession', 'updateProgramSession']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      const error = { error: { detail: 'Error updating session' } };
      programSpy.updateProgramSession.and.returnValue(throwError(() => error));

      await TestBed.resetTestingModule().configureTestingModule({
        imports: [
          SessionDialogComponent,
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
          MatNativeDateModule
        ],
        providers: [
          { provide: ProgramService, useValue: programSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { session: mockSession, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(SessionDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.sessionForm.patchValue({ duration_minutes: 90 });
      newComponent.onSubmit();

      expect(newComponent.isLoading).toBe(false);
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Error updating session', 'Close', { duration: 3000 });
    });
  });

  describe('onCancel', () => {
    it('should close dialog with false', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalledWith(false);
    });
  });

  describe('Helper methods', () => {
    beforeEach(() => {
      component.data = { session: null, program: mockProgram, pairings: [mockPairing], participants: [mockParticipant], viewMode: false };
      fixture.detectChanges();
    });

    it('should get pairing display', () => {
      const display = component.getPairingDisplay(mockPairing);
      expect(display).toContain('Pairing');
    });

    it('should get participant display', () => {
      const display = component.getParticipantDisplay(mockParticipant);
      expect(display).toContain('Mentor');
    });

    it('should show error when field is invalid and touched', () => {
      const field = component.sessionForm.get('session_date');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('session_date')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.sessionForm.get('session_date');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('session_date')).toBe(true);
    });
  });
});
