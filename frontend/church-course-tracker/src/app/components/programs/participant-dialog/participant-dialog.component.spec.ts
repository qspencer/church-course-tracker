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
import { MatChipsModule } from '@angular/material/chips';

import { ParticipantDialogComponent, ParticipantDialogData } from './participant-dialog.component';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { Program, ProgramParticipant, RoleDefinition } from '../../../models/program.model';
import { Person } from '../../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('ParticipantDialogComponent', () => {
  let component: ParticipantDialogComponent;
  let fixture: ComponentFixture<ParticipantDialogComponent>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let memberServiceSpy: jasmine.SpyObj<MemberService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ParticipantDialogComponent>>;
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

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', ['addProgramParticipant', 'updateProgramParticipant']);
    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    programSpy.addProgramParticipant.and.returnValue(of(mockParticipant));
    programSpy.updateProgramParticipant.and.returnValue(of(mockParticipant));
    memberSpy.getMembers.and.returnValue(of([mockMember]));

    await TestBed.configureTestingModule({
      declarations: [ParticipantDialogComponent],
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
        MatChipsModule
      ],
      providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { participant: null, program: mockProgram, viewMode: false } },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ParticipantDialogComponent);
    component = fixture.componentInstance;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    memberServiceSpy = TestBed.inject(MemberService) as jasmine.SpyObj<MemberService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<ParticipantDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    fixture.detectChanges(); // Trigger ngOnInit
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Initialization', () => {
    it('should initialize in create mode', () => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: programServiceSpy },
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: null, program: mockProgram, viewMode: false } },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(false);
      expect(newComponent.viewMode).toBe(false);
    });

    it('should initialize in edit mode', () => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: programServiceSpy },
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: mockParticipant, program: mockProgram, viewMode: false } },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.isEditing).toBe(true);
    });

    it('should initialize in view mode', () => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: programServiceSpy },
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: mockParticipant, program: mockProgram, viewMode: true } },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.viewMode).toBe(true);
      expect(newComponent.participantForm.disabled).toBe(true);
    });

    it('should extract role options from program', () => {
      expect(component.roleOptions.length).toBeGreaterThan(0);
    });

    it('should use default roles when program has no role definitions', () => {
      const programWithoutRoles = { ...mockProgram, role_definitions: undefined };
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: programServiceSpy },
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: null, program: programWithoutRoles, viewMode: false } },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.roleOptions).toEqual(['Mentor', 'Mentee']);
    });

    it('should load members on init when not in view mode', () => {
      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
    });

    it('should patch form values when editing', () => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: programServiceSpy },
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: mockParticipant, program: mockProgram, viewMode: false } },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      expect(newComponent.participantForm.get('people_id')?.value).toBe(mockParticipant.people_id);
      expect(newComponent.participantForm.get('role_name')?.value).toBe(mockParticipant.role_name);
      expect(newComponent.participantForm.get('status')?.value).toBe(mockParticipant.status);
    });
  });

  describe('loadMembers', () => {
    it('should load members successfully', () => {
      component.loadMembers();

      expect(memberServiceSpy.getMembers).toHaveBeenCalled();
      expect(component.members).toEqual([mockMember]);
      expect(component.isLoading).toBe(false);
    });

    it('should handle error loading members', () => {
      const error = new Error('Failed to load');
      memberServiceSpy.getMembers.and.returnValue(throwError(() => error));

      component.loadMembers();

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error loading members', 'Close', { duration: 3000 });
    });
  });

  describe('onSubmit', () => {
    beforeEach(() => {
      component.data = { participant: null, program: mockProgram, viewMode: false };
      fixture.detectChanges();
    });

    it('should not submit in view mode', () => {
      component.viewMode = true;
      component.onSubmit();

      expect(programServiceSpy.addProgramParticipant).not.toHaveBeenCalled();
    });

    it('should not submit invalid form', () => {
      component.participantForm.patchValue({
        people_id: '',
        role_name: '',
        status: 'active'
      });
      component.onSubmit();

      expect(programServiceSpy.addProgramParticipant).not.toHaveBeenCalled();
    });

    it('should not submit when loading', () => {
      component.isLoading = true;
      component.onSubmit();

      expect(programServiceSpy.addProgramParticipant).not.toHaveBeenCalled();
    });

    it('should create participant when form is valid', () => {
      component.participantForm.patchValue({
        people_id: 1,
        role_name: 'Mentor',
        status: 'active',
        notes: 'Test notes',
        progress_percentage: 0
      });
      component.onSubmit();

      expect(programServiceSpy.addProgramParticipant).toHaveBeenCalledWith(mockProgram.id, {
        program_id: mockProgram.id,
        people_id: 1,
        role_name: 'Mentor',
        status: 'active',
        notes: 'Test notes',
        progress_percentage: 0
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Participant added successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should update participant when editing', () => {
      // Create a new component instance with participant data
      TestBed.resetTestingModule();
      const updateSpy = jasmine.createSpyObj('ProgramService', ['addProgramParticipant', 'updateProgramParticipant']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      updateSpy.updateProgramParticipant.and.returnValue(of(mockParticipant));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: updateSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: mockParticipant, program: mockProgram, viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.participantForm.patchValue({
        status: 'completed',
        notes: 'Updated notes',
        progress_percentage: 100
      });
      newComponent.onSubmit();

      expect(updateSpy.updateProgramParticipant).toHaveBeenCalledWith(mockParticipant.id, {
        role_name: mockParticipant.role_name,
        status: 'completed',
        notes: 'Updated notes',
        progress_percentage: 100
      });
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Participant updated successfully', 'Close', { duration: 3000 });
      expect(matDialogRefSpy.close).toHaveBeenCalledWith(true);
    });

    it('should handle create error', () => {
      const error = { error: { detail: 'Error adding participant' } };
      programServiceSpy.addProgramParticipant.and.returnValue(throwError(() => error));

      component.participantForm.patchValue({
        people_id: 1,
        role_name: 'Mentor',
        status: 'active'
      });
      component.onSubmit();

      expect(component.isLoading).toBe(false);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Error adding participant', 'Close', { duration: 3000 });
    });

    it('should handle update error', () => {
      // Create a new component instance with participant data
      TestBed.resetTestingModule();
      const updateSpy = jasmine.createSpyObj('ProgramService', ['addProgramParticipant', 'updateProgramParticipant']);
      const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      const error = { error: { detail: 'Error updating participant' } };
      updateSpy.updateProgramParticipant.and.returnValue(throwError(() => error));
      memberSpy.getMembers.and.returnValue(of([mockMember]));

      TestBed.configureTestingModule({
        declarations: [ParticipantDialogComponent],
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
          MatChipsModule
        ],
        providers: [
          { provide: ProgramService, useValue: updateSpy },
          { provide: MemberService, useValue: memberSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { participant: mockParticipant, program: mockProgram, viewMode: false } },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ]
      }).compileComponents();
      
      const newFixture = TestBed.createComponent(ParticipantDialogComponent);
      const newComponent = newFixture.componentInstance;
      newFixture.detectChanges();

      newComponent.participantForm.patchValue({ status: 'completed' });
      newComponent.onSubmit();

      expect(newComponent.isLoading).toBe(false);
      expect(matSnackBarSpy.open).toHaveBeenCalledWith('Error updating participant', 'Close', { duration: 3000 });
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
      component.data = { participant: null, program: mockProgram, viewMode: false };
      component.members = [mockMember];
      fixture.detectChanges();
    });

    it('should get member name', () => {
      const name = component.getMemberName(1);
      expect(name).toBe('John Doe');
    });

    it('should return Unknown for non-existent member', () => {
      const name = component.getMemberName(999);
      expect(name).toBe('Unknown');
    });

    it('should get role color for primary role', () => {
      const color = component.getRoleColor('Mentor');
      expect(color).toBe('primary');
    });

    it('should get role color for secondary role', () => {
      const color = component.getRoleColor('Mentee');
      expect(color).toBe('accent');
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
      const field = component.participantForm.get('people_id');
      field?.markAsTouched();
      field?.setErrors({ required: true });

      expect(component.shouldShowError('people_id')).toBe(true);
    });

    it('should show error when field is invalid and form submitted', () => {
      const field = component.participantForm.get('people_id');
      field?.setErrors({ required: true });
      component.isSubmitted = true;

      expect(component.shouldShowError('people_id')).toBe(true);
    });
  });
});
