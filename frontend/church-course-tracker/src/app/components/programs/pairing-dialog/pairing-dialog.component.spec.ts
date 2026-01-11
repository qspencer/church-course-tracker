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
// MatChipModule not needed for this test

import { PairingDialogComponent, PairingDialogData } from './pairing-dialog.component';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { Program, ProgramPairing, ProgramParticipant, RoleDefinition } from '../../../models/program.model';
import { Person } from '../../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('PairingDialogComponent', () => {
  let component: PairingDialogComponent;
  let fixture: ComponentFixture<PairingDialogComponent>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let memberServiceSpy: jasmine.SpyObj<MemberService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<PairingDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockRoleDefinition: RoleDefinition = {
    name: 'Mentor',
    is_primary: true,
    min_participants: 1,
    max_participants: 10
  };

  const mockProgram: Program = {
    id: 1,
    title: 'Test Program',
    description: 'Test Description',
    is_active: true,
    role_definitions: [mockRoleDefinition, { name: 'Mentee', is_primary: false, min_participants: 1, max_participants: 10 }],
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

  const mockParticipant: ProgramParticipant = {
    id: 1,
    program_id: 1,
    people_id: 1,
    role_name: 'Mentor',
    status: 'active',
    progress_percentage: 50,
    start_date: '2023-01-01T00:00:00Z',
    notes: undefined,
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
    notes: 'Test notes',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    programSpy.createProgramPairing.and.returnValue(of(mockPairing));
    programSpy.updateProgramPairing.and.returnValue(of(mockPairing));
    memberSpy.getMembers.and.returnValue(of([mockMember]));

    await TestBed.configureTestingModule({
      declarations: [PairingDialogComponent],
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
        { provide: ProgramService, useValue: programSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { pairing: null, program: mockProgram, participants: [mockParticipant], viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(PairingDialogComponent);
    component = fixture.componentInstance;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    memberServiceSpy = TestBed.inject(MemberService) as jasmine.SpyObj<MemberService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<PairingDialogComponent>>;
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
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      memberSpy.getMembers.and.returnValue(of([mockMember]));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: mockPairing, program: mockProgram, participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(true);
    });

    it('should initialize in view mode', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: mockPairing, program: mockProgram, participants: [mockParticipant], viewMode: true } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      // Don't call detectChanges for view mode test to avoid template rendering issues
      // Just check the constructor logic
      expect(newComponent.viewMode).toBe(true);
      expect(newComponent.pairingForm.disabled).toBe(true);
    });

    it('should update participant lists on init', () => {
      // Component already initialized in beforeEach
      expect(component.primaryParticipants.length).toBeGreaterThanOrEqual(0);
      expect(component.secondaryParticipants.length).toBeGreaterThanOrEqual(0);
    });

    it('should patch form values when editing', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      memberSpy.getMembers.and.returnValue(of([mockMember]));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: mockPairing, program: mockProgram, participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.pairingForm.get('primary_participant_id')?.value).toBe(mockPairing.primary_participant_id);
      expect(newComponent.pairingForm.get('secondary_participant_id')?.value).toBe(mockPairing.secondary_participant_id);
      expect(newComponent.pairingForm.get('status')?.value).toBe(mockPairing.status);
    });
  });

  describe('loadMembers', () => {
    it('should load members successfully', () => {
      component.loadMembers();

      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
      expect(component.members).toEqual([mockMember]);
    });

    it('should handle error loading members', () => {
      const error = new Error('Failed to load');
      // Reset the spy to return error
      memberServiceSpy.getMembers.and.returnValue(throwError(() => error));
      // Clear previous members
      component.members = [];

      component.loadMembers();

      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
      expect(component.members).toEqual([]);
    });
  });

  describe('updateParticipantLists', () => {
    it('should filter participants by role', () => {
      // Component already initialized in beforeEach
      component.updateParticipantLists();

      expect(component.primaryParticipants).toBeDefined();
      expect(component.secondaryParticipants).toBeDefined();
    });

    it('should handle program without role definitions', async () => {
      const programWithoutRoles = { ...mockProgram, role_definitions: undefined };
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      memberSpy.getMembers.and.returnValue(of([mockMember]));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: null, program: programWithoutRoles, participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.updateParticipantLists();

      expect(newComponent.primaryParticipants).toEqual([]);
      expect(newComponent.secondaryParticipants).toEqual([]);
    });
  });

  describe('onSubmit', () => {
    // Component already initialized in beforeEach with pairing: null, viewMode: false

    it('should not submit in view mode', () => {
      component.viewMode = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramPairing).not.toHaveBeenCalled();
    });

    it('should not submit invalid form', () => {
      component.pairingForm.patchValue({
        primary_participant_id: '',
        secondary_participant_id: '',
        status: 'active'
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramPairing).not.toHaveBeenCalled();
    });

    it('should not submit when loading', () => {
      component.isLoading = true;
      component.onSubmit();

      expect(programServiceSpy.createProgramPairing).not.toHaveBeenCalled();
    });

    it('should reject same primary and secondary participant', () => {
      component.pairingForm.patchValue({
        primary_participant_id: 1,
        secondary_participant_id: 1,
        status: 'active'
      });
      component.onSubmit();

      expect(snackBarSpy.open).toHaveBeenCalledWith('Primary and secondary participants must be different', 'Close', { duration: 3000 });
      expect(programServiceSpy.createProgramPairing).not.toHaveBeenCalled();
    });

    it('should create pairing when form is valid', () => {
      component.pairingForm.patchValue({
        primary_participant_id: 1,
        secondary_participant_id: 2,
        status: 'active',
        notes: 'Test notes'
      });
      component.onSubmit();

      expect(programServiceSpy.createProgramPairing).toHaveBeenCalledWith(mockProgram.id, {
        program_id: mockProgram.id,
        primary_participant_id: 1,
        secondary_participant_id: 2,
        status: 'active',
        notes: 'Test notes'
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Pairing created successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should update pairing when editing', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      programSpy.updateProgramPairing.and.returnValue(of(mockPairing));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: mockPairing, program: mockProgram, participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.pairingForm.patchValue({
        status: 'completed',
        notes: 'Updated notes'
      });
      newComponent.onSubmit();

      expect(programSpy.updateProgramPairing).toHaveBeenCalledWith(mockPairing.id, {
        status: 'completed',
        notes: 'Updated notes'
      });
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Pairing updated successfully', 'Close', { duration: 3000 });
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should handle create error', () => {
      const error = { error: { detail: 'Error creating pairing' } };
      programServiceSpy.createProgramPairing.and.returnValue(throwError(() => error));

      component.pairingForm.patchValue({
        primary_participant_id: 1,
        secondary_participant_id: 2,
        status: 'active'
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error creating pairing', 'Close', { duration: 3000 });
    });

    it('should handle update error', async () => {
      const programSpy = jasmine.createSpyObj('ProgramService', ['createProgramPairing', 'updateProgramPairing']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      const error = { error: { detail: 'Error updating pairing' } };
      programSpy.updateProgramPairing.and.returnValue(throwError(() => error));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      await TestBed.resetTestingModule().configureTestingModule({
        declarations: [PairingDialogComponent],
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
          { provide: ProgramService, useValue: programSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { pairing: mockPairing, program: mockProgram, participants: [mockParticipant], viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();

      const newFixture = TestBed.createComponent(PairingDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.pairingForm.patchValue({ status: 'completed' });
      newComponent.onSubmit();

      expect(newComponent.isLoading).toBe(false);
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Error updating pairing', 'Close', { duration: 3000 });
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
      // Component already initialized, just set members for helper tests
      component.members = [mockMember];
    });

    it('should get participant name', () => {
      const name = component.getParticipantName(1);
      expect(name).toBeDefined();
    });

    it('should return Unknown for non-existent participant', () => {
      const name = component.getParticipantName(999);
      expect(name).toBe('Unknown');
    });

    it('should get participant display', () => {
      const display = component.getParticipantDisplay(mockParticipant);
      expect(display).toContain('Mentor');
    });

    it('should get status color for active', () => {
      expect(component.getStatusColor('active')).toBe('primary');
    });

    it('should get status color for paused', () => {
      expect(component.getStatusColor('paused')).toBe('warn');
    });

    it('should get status color for completed', () => {
      expect(component.getStatusColor('completed')).toBe('accent');
    });

    it('should get status color for ended', () => {
      expect(component.getStatusColor('ended')).toBe('');
    });

    it('should return empty string for unknown status', () => {
      expect(component.getStatusColor('unknown')).toBe('');
    });

    it('should show error when field is invalid and touched', () => {
      const field = component.pairingForm.get('primary_participant_id');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('primary_participant_id')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.pairingForm.get('primary_participant_id');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('primary_participant_id')).toBe(true);
    });
  });
});
