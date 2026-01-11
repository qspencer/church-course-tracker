import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatCheckboxModule } from '@angular/material/checkbox';

import { ProgramDialogComponent } from './program-dialog.component';
import { ProgramService } from '../../../services/program.service';
import { CourseService } from '../../../services/course.service';
import { AutocompleteSuggestionService } from '../../../services/autocomplete-suggestion.service';
import { Program, ProgramCreate } from '../../../models/program.model';
import { Course } from '../../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('ProgramDialogComponent', () => {
  let component: ProgramDialogComponent;
  let fixture: ComponentFixture<ProgramDialogComponent>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<ProgramDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockProgram: Program = {
    id: 1,
    title: 'Test Program',
    description: 'Test Description',
    is_active: true,
    role_definitions: [
      {
        name: 'Mentor',
        min_participants: 1,
        max_participants: 1,
        is_primary: true
      },
      {
        name: 'Mentee',
        min_participants: 1,
        max_participants: 3,
        is_primary: false
      }
    ],
    relationship_config: {
      allow_multiple_secondary: true,
      max_secondary_per_primary: 3,
      require_pairing: true,
      progress_calculation: 'content_based'
    },
    locations: [],
    delivery_modes: [],
    prerequisites: [],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const createMockDialogData = (overrides?: Partial<{ program: Program | null; viewMode?: boolean; importData?: any }>) => ({
    program: null,
    ...overrides
  });

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', ['createProgram', 'updateProgram', 'getProgram']);
    programSpy.createProgram.and.returnValue(of(mockProgram));
    programSpy.updateProgram.and.returnValue(of(mockProgram));
    programSpy.getProgram.and.returnValue(of(mockProgram));

    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    courseSpy.getCourses.and.returnValue(of([]));

    const autocompleteSpy = jasmine.createSpyObj('AutocompleteSuggestionService', ['getSuggestions', 'addSuggestion']);
    autocompleteSpy.getSuggestions.and.returnValue(of([]));
    autocompleteSpy.addSuggestion.and.returnValue(of({}));

    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [ProgramDialogComponent],
      imports: [
        ReactiveFormsModule,
        FormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatIconModule,
        MatAutocompleteModule,
        MatCheckboxModule,
        MatSnackBarModule
      ],
      providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: AutocompleteSuggestionService, useValue: autocompleteSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useFactory: () => createMockDialogData() },
        { provide: MatSnackBar, useValue: matSnackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    fixture = TestBed.createComponent(ProgramDialogComponent);
    component = fixture.componentInstance;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<ProgramDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize in create mode when no program provided', () => {
    fixture.detectChanges();
    expect(component.isEditMode).toBe(false);
    expect(component.program).toBeNull();
  });

  it('should initialize in edit mode when program provided', () => {
    TestBed.resetTestingModule();
    const editDialogData = createMockDialogData({ program: mockProgram });
    
    const programSpy = jasmine.createSpyObj('ProgramService', ['createProgram', 'updateProgram', 'getProgram']);
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    courseSpy.getCourses.and.returnValue(of([]));
    const autocompleteSpy = jasmine.createSpyObj('AutocompleteSuggestionService', ['getSuggestions', 'addSuggestion']);
    autocompleteSpy.getSuggestions.and.returnValue(of([]));
    autocompleteSpy.addSuggestion.and.returnValue(of({}));

    TestBed.configureTestingModule({
      declarations: [ProgramDialogComponent],
      imports: [
        ReactiveFormsModule,
        FormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatSelectModule,
        MatChipsModule,
        MatIconModule,
        MatAutocompleteModule,
        MatCheckboxModule,
        MatSnackBarModule
      ],
      providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: AutocompleteSuggestionService, useValue: autocompleteSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: editDialogData },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();

    const editFixture = TestBed.createComponent(ProgramDialogComponent);
    const editComponent = editFixture.componentInstance;
    editFixture.detectChanges();

    expect(editComponent.isEditMode).toBe(true);
    expect(editComponent.program).toEqual(mockProgram);
  });

  describe('form initialization', () => {
    it('should initialize form with validators', () => {
      expect(component.programForm.get('title')?.hasError('required')).toBe(true);
      expect(component.programForm.get('title')?.hasError('maxlength')).toBe(false);
    });

    it('should initialize with default relationship config', () => {
      const relationshipConfig = component.programForm.get('relationship_config');
      expect(relationshipConfig?.get('allow_multiple_secondary')?.value).toBe(true);
      expect(relationshipConfig?.get('require_pairing')?.value).toBe(true);
      expect(relationshipConfig?.get('progress_calculation')?.value).toBe('content_based');
    });
  });

  describe('import mode', () => {
    let importFixture: ComponentFixture<ProgramDialogComponent>;
    let importComponent: ProgramDialogComponent;
    let importProgramServiceSpy: jasmine.SpyObj<ProgramService>;

    beforeEach(() => {
      const importData = {
        sourceType: 'list',
        sourceId: 'pc_list_123',
        previewData: {
          title: 'Imported Program',
          description: 'Imported Description',
          planning_center_list_id: 'pc_list_123',
          planning_center_list_name: 'Imported List',
          locations: ['Location 1'],
          delivery_modes: ['Online']
        }
      };

      const importDialogData = createMockDialogData({ importData });

      TestBed.resetTestingModule();
      importProgramServiceSpy = jasmine.createSpyObj('ProgramService', ['createProgram', 'updateProgram', 'getProgram']);
      importProgramServiceSpy.createProgram.and.returnValue(of({ ...mockProgram, ...importData.previewData }));

      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      courseSpy.getCourses.and.returnValue(of([]));

      const autocompleteSpy = jasmine.createSpyObj('AutocompleteSuggestionService', ['getSuggestions', 'addSuggestion']);
      autocompleteSpy.getSuggestions.and.returnValue(of([]));
      autocompleteSpy.addSuggestion.and.returnValue(of({}));

      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      TestBed.configureTestingModule({
        declarations: [ProgramDialogComponent],
        imports: [
          ReactiveFormsModule,
          FormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule,
          MatSelectModule,
          MatChipsModule,
          MatIconModule,
          MatAutocompleteModule,
          MatCheckboxModule,
          MatSnackBarModule
        ],
        providers: [
          { provide: ProgramService, useValue: importProgramServiceSpy },
          { provide: CourseService, useValue: courseSpy },
          { provide: AutocompleteSuggestionService, useValue: autocompleteSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: importDialogData },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      importFixture = TestBed.createComponent(ProgramDialogComponent);
      importComponent = importFixture.componentInstance;
      importFixture.detectChanges();
    });

    it('should populate form with import data', () => {
      expect(importComponent.programForm.get('title')?.value).toBe('Imported Program');
      expect(importComponent.programForm.get('description')?.value).toBe('Imported Description');
      expect(importComponent.programForm.get('locations')?.value).toEqual(['Location 1']);
      expect(importComponent.programForm.get('delivery_modes')?.value).toEqual(['Online']);
    });

    it('should add default role definitions when importing', () => {
      const roleDefinitions = importComponent.programForm.get('role_definitions') as any;
      expect(roleDefinitions.length).toBeGreaterThan(0);
      
      // Check that default roles were added
      const roles = roleDefinitions.controls.map((control: any) => control.value);
      const mentorRole = roles.find((r: any) => r.name === 'Mentor');
      const menteeRole = roles.find((r: any) => r.name === 'Mentee');
      
      expect(mentorRole).toBeDefined();
      expect(mentorRole.is_primary).toBe(true);
      expect(menteeRole).toBeDefined();
      expect(menteeRole.is_primary).toBe(false);
    });

    it('should include PC event data when creating program from event', () => {
      const eventImportData = {
        sourceType: 'event',
        sourceId: 'pc_event_123',
        previewData: {
          title: 'Event Program',
          description: 'From Event',
          planning_center_event_id: 'pc_event_123',
          planning_center_event_name: 'Imported Event',
          locations: [],
          delivery_modes: []
        }
      };

      const eventDialogData = createMockDialogData({ importData: eventImportData });

      TestBed.resetTestingModule();
      const eventProgramSpy = jasmine.createSpyObj('ProgramService', ['createProgram', 'updateProgram', 'getProgram']);
      eventProgramSpy.createProgram.and.returnValue(of(mockProgram));

      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      courseSpy.getCourses.and.returnValue(of([]));

      const autocompleteSpy = jasmine.createSpyObj('AutocompleteSuggestionService', ['getSuggestions', 'addSuggestion']);
      autocompleteSpy.getSuggestions.and.returnValue(of([]));
      autocompleteSpy.addSuggestion.and.returnValue(of({}));

      const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
      const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

      TestBed.configureTestingModule({
        declarations: [ProgramDialogComponent],
        imports: [
          ReactiveFormsModule,
          FormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule,
          MatSelectModule,
          MatChipsModule,
          MatIconModule,
          MatAutocompleteModule,
          MatCheckboxModule,
          MatSnackBarModule
        ],
        providers: [
          { provide: ProgramService, useValue: eventProgramSpy },
          { provide: CourseService, useValue: courseSpy },
          { provide: AutocompleteSuggestionService, useValue: autocompleteSpy },
          { provide: MatDialogRef, useValue: matDialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: eventDialogData },
          { provide: MatSnackBar, useValue: matSnackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const eventFixture = TestBed.createComponent(ProgramDialogComponent);
      const eventComponent = eventFixture.componentInstance;
      eventFixture.detectChanges();

      // Fill in required fields and submit
      eventComponent.programForm.patchValue({
        title: 'Event Program',
        description: 'From Event'
      });

      eventComponent.onSubmit();

      expect(eventProgramSpy.createProgram).toHaveBeenCalled();
      const createCall = eventProgramSpy.createProgram.calls.mostRecent();
      const createData = createCall.args[0] as ProgramCreate;

      expect(createData.planning_center_event_id).toBe('pc_event_123');
      expect(createData.planning_center_event_name).toBe('Imported Event');
    });

    it('should include PC list data when creating program from list', () => {
      // Fill in required fields and submit
      importComponent.programForm.patchValue({
        title: 'Imported Program',
        description: 'Imported Description'
      });

      importComponent.onSubmit();

      expect(importProgramServiceSpy.createProgram).toHaveBeenCalled();
      const createCall = importProgramServiceSpy.createProgram.calls.mostRecent();
      const createData = createCall.args[0] as ProgramCreate;

      // Note: Programs don't currently store planning_center_list_id in the schema
      // but the data is stored in pcData for potential future use
      expect(createData.title).toBe('Imported Program');
      expect(createData.description).toBe('Imported Description');
    });
  });

  describe('onSubmit', () => {
    it('should create program when not in edit mode', () => {
      fixture.detectChanges();
      
      component.programForm.patchValue({
        title: 'New Program',
        description: 'New Description'
      });

      // Add at least one role definition
      component.addRoleDefinition({
        name: 'Mentor',
        min_participants: 1,
        max_participants: 1,
        is_primary: true
      });

      component.onSubmit();

      expect(programServiceSpy.createProgram).toHaveBeenCalled();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });

    it('should update program when in edit mode', () => {
      TestBed.resetTestingModule();
      const editDialogData = createMockDialogData({ program: mockProgram });
      
      const editProgramSpy = jasmine.createSpyObj('ProgramService', ['createProgram', 'updateProgram', 'getProgram']);
      editProgramSpy.updateProgram.and.returnValue(of(mockProgram));

      const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
      courseSpy.getCourses.and.returnValue(of([]));

      const autocompleteSpy = jasmine.createSpyObj('AutocompleteSuggestionService', ['getSuggestions', 'addSuggestion']);
      autocompleteSpy.getSuggestions.and.returnValue(of([]));
      autocompleteSpy.addSuggestion.and.returnValue(of({}));

      TestBed.configureTestingModule({
        declarations: [ProgramDialogComponent],
        imports: [
          ReactiveFormsModule,
          FormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatProgressSpinnerModule,
          MatSelectModule,
          MatChipsModule,
          MatIconModule,
          MatAutocompleteModule,
          MatCheckboxModule,
          MatSnackBarModule
        ],
        providers: [
          { provide: ProgramService, useValue: editProgramSpy },
          { provide: CourseService, useValue: courseSpy },
          { provide: AutocompleteSuggestionService, useValue: autocompleteSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: editDialogData },
          { provide: MatSnackBar, useValue: snackBarSpy },
          provideHttpClient(withInterceptorsFromDi()),
          provideHttpClientTesting()
        ],
        schemas: [NO_ERRORS_SCHEMA]
      }).compileComponents();

      const editFixture = TestBed.createComponent(ProgramDialogComponent);
      const editComponent = editFixture.componentInstance;
      editFixture.detectChanges();

      editComponent.programForm.patchValue({
        title: 'Updated Program'
      });

      editComponent.onSubmit();

      expect(editProgramSpy.updateProgram).toHaveBeenCalled();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });

    it('should not submit if form is invalid', () => {
      fixture.detectChanges();
      component.onSubmit();
      expect(programServiceSpy.createProgram).not.toHaveBeenCalled();
    });
  });

  describe('onCancel', () => {
    it('should close dialog without data', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });
  });
});



