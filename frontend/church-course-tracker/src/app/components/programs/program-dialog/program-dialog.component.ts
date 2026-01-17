import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, FormControl, AbstractControl } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { finalize } from 'rxjs/operators';
import { ProgramService } from '../../../services/program.service';
import { CourseService } from '../../../services/course.service';
import { AutocompleteSuggestionService } from '../../../services/autocomplete-suggestion.service';
import { LoggerService } from '../../../services/logger.service';
import { Program, ProgramCreate, ProgramUpdate, RoleDefinition, RelationshipConfig } from '../../../models/program.model';
import { Course, PlanningCenterImportData } from '../../../models';
import { MatDialog } from '@angular/material/dialog';
import { ParticipantsManagementComponent } from '../participants-management/participants-management.component';
import { PairingsManagementComponent } from '../pairings-management/pairings-management.component';
import { SessionsManagementComponent } from '../sessions-management/sessions-management.component';
import { ProgressManagementComponent } from '../progress-management/progress-management.component';

@Component({
  selector: 'app-program-dialog',
  templateUrl: './program-dialog.component.html',
  styleUrls: ['./program-dialog.component.scss']
})
export class ProgramDialogComponent implements OnInit {
  programForm: FormGroup;
  isEditMode = false;
  viewMode = false;
  program: Program | null = null;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  
  // For chip inputs
  locationInput = '';
  deliveryModeInput = '';
  
  // Autocomplete suggestions
  locationSuggestions: string[] = [];
  deliveryModeSuggestions: string[] = [];
  filteredLocationSuggestions: string[] = [];
  filteredDeliveryModeSuggestions: string[] = [];
  
  // Available courses for prerequisites
  availableCourses: Course[] = [];
  loadingCourses = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ProgramDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { program: Program | null; viewMode?: boolean; importData?: PlanningCenterImportData },
    private programService: ProgramService,
    private courseService: CourseService,
    private autocompleteService: AutocompleteSuggestionService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private router: Router,
    private logger: LoggerService
  ) {
    this.program = data.program;
    this.viewMode = data.viewMode || false;
    this.isEditMode = !!data.program && !this.viewMode;
    
    this.programForm = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(200)]],
      description: [''],
      is_active: [true],
      role_definitions: this.fb.array([]),
      relationship_config: this.fb.group({
        allow_multiple_secondary: [true],
        max_secondary_per_primary: [null],
        require_pairing: [true],
        progress_calculation: ['content_based']
      }),
      locations: [[]],
      delivery_modes: [[]],
      prerequisites: [[]]
    });
  }

  ngOnInit(): void {
    this.loadAvailableCourses();
    this.loadAutocompleteSuggestions();
    
    // If import data is provided, populate form with it
    if (this.data.importData) {
      const importData = this.data.importData.previewData;
      this.programForm.patchValue({
        title: importData.title || '',
        description: importData.description || '',
        is_active: true,
        locations: importData.locations || [],
        delivery_modes: importData.delivery_modes || [],
        prerequisites: []
      });
      // Store PC list/event data for later use in submission
      (this.programForm as any).pcData = {
        planning_center_list_id: importData.planning_center_list_id,
        planning_center_list_name: importData.planning_center_list_name,
        planning_center_event_id: importData.planning_center_event_id,
        planning_center_event_name: importData.planning_center_event_name
      };
      // Add default roles if not editing
      if (!this.isEditMode) {
        this.addRoleDefinition({
          name: 'Mentor',
          min_participants: 1,
          max_participants: 1,
          is_primary: true
        });
        this.addRoleDefinition({
          name: 'Mentee',
          min_participants: 1,
          max_participants: 3,
          is_primary: false
        });
      }
    } else if (this.program) {
      // Populate role definitions
      if (this.program.role_definitions && this.program.role_definitions.length > 0) {
        this.program.role_definitions.forEach(role => {
          this.addRoleDefinition(role);
        });
      } else if (!this.viewMode) {
        // Default roles for new programs
        this.addRoleDefinition({
          name: 'Mentor',
          min_participants: 1,
          max_participants: 1,
          is_primary: true
        });
        this.addRoleDefinition({
          name: 'Mentee',
          min_participants: 1,
          max_participants: 3,
          is_primary: false
        });
      }
      
      // Populate relationship config
      if (this.program.relationship_config) {
        this.programForm.patchValue({
          relationship_config: {
            allow_multiple_secondary: this.program.relationship_config.allow_multiple_secondary ?? true,
            max_secondary_per_primary: this.program.relationship_config.max_secondary_per_primary ?? null,
            require_pairing: this.program.relationship_config.require_pairing ?? true,
            progress_calculation: this.program.relationship_config.progress_calculation ?? 'content_based'
          }
        });
      }
      
      this.programForm.patchValue({
        title: this.program.title,
        description: this.program.description || '',
        is_active: this.program.is_active,
        locations: this.program.locations || [],
        delivery_modes: this.program.delivery_modes || [],
        prerequisites: this.program.prerequisites || []
      });
      
      if (this.viewMode) {
        this.programForm.disable();
      }
    } else if (!this.viewMode) {
      // Default roles for new programs
      this.addRoleDefinition({
        name: 'Mentor',
        min_participants: 1,
        max_participants: 1,
        is_primary: true
      });
      this.addRoleDefinition({
        name: 'Mentee',
        min_participants: 1,
        max_participants: 3,
        is_primary: false
      });
    }
  }

  get roleDefinitions(): FormArray {
    return this.programForm.get('role_definitions') as FormArray;
  }

  get relationshipConfig(): FormGroup {
    return this.programForm.get('relationship_config') as FormGroup;
  }

  addRoleDefinition(role?: RoleDefinition): void {
    const roleGroup = this.fb.group({
      name: [role?.name || '', [Validators.required]],
      min_participants: [role?.min_participants ?? 1, [Validators.required, Validators.min(0)]],
      max_participants: [role?.max_participants ?? 1, [Validators.required, Validators.min(1)]],
      is_primary: [role?.is_primary ?? false]
    });
    this.roleDefinitions.push(roleGroup);
  }

  removeRoleDefinition(index: number): void {
    this.roleDefinitions.removeAt(index);
  }

  loadAvailableCourses(): void {
    if (this.viewMode) return;

    this.loadingCourses = true;
    this.courseService.getCourses()
      .pipe(finalize(() => this.loadingCourses = false))
      .subscribe({
        next: (courses) => {
          this.availableCourses = courses.filter(c => c.is_active);
        },
        error: (error) => {
          this.logger.error('Error loading courses', error, { component: 'ProgramDialogComponent' });
          this.snackBar.open('Failed to load courses', 'Close', { duration: 5000 });
        }
      });
  }

  // Load autocomplete suggestions
  loadAutocompleteSuggestions(): void {
    // Load location suggestions
    this.autocompleteService.getSuggestions('location').subscribe({
      next: (suggestions) => {
        this.locationSuggestions = suggestions;
        this.filteredLocationSuggestions = suggestions;
      },
      error: (error) => {
        this.logger.error('Error loading location suggestions', error);
      }
    });

    // Load delivery mode suggestions
    this.autocompleteService.getSuggestions('delivery_mode').subscribe({
      next: (suggestions) => {
        this.deliveryModeSuggestions = suggestions;
        this.filteredDeliveryModeSuggestions = suggestions;
      },
      error: (error) => {
        this.logger.error('Error loading delivery mode suggestions', error);
      }
    });
  }

  // Filter location suggestions based on input
  filterLocationSuggestions(): void {
    const filterValue = this.locationInput.toLowerCase();
    this.filteredLocationSuggestions = this.locationSuggestions.filter(
      suggestion => suggestion.toLowerCase().includes(filterValue)
    );
  }

  // Filter delivery mode suggestions based on input
  filterDeliveryModeSuggestions(): void {
    const filterValue = this.deliveryModeInput.toLowerCase();
    this.filteredDeliveryModeSuggestions = this.deliveryModeSuggestions.filter(
      suggestion => suggestion.toLowerCase().includes(filterValue)
    );
  }

  addLocation(): void {
    const location = this.locationInput.trim();
    if (location && !this.programForm.value.locations.includes(location)) {
      const currentLocations = this.programForm.value.locations || [];
      this.programForm.patchValue({
        locations: [...currentLocations, location]
      });
      
      // Save to autocomplete suggestions
      this.autocompleteService.addSuggestion('location', location).subscribe({
        next: () => {
          // Reload suggestions to include the new one
          this.loadAutocompleteSuggestions();
        },
        error: (error) => {
          this.logger.error('Error saving location suggestion', error);
        }
      });
      
      this.locationInput = '';
      this.filteredLocationSuggestions = this.locationSuggestions;
    }
  }

  removeLocation(location: string): void {
    const locations = this.programForm.get('locations')?.value || [];
    this.programForm.patchValue({
      locations: locations.filter((l: string) => l !== location)
    });
  }

  addDeliveryMode(): void {
    const mode = this.deliveryModeInput.trim();
    if (mode && !this.programForm.value.delivery_modes.includes(mode)) {
      const currentModes = this.programForm.value.delivery_modes || [];
      this.programForm.patchValue({
        delivery_modes: [...currentModes, mode]
      });
      
      // Save to autocomplete suggestions
      this.autocompleteService.addSuggestion('delivery_mode', mode).subscribe({
        next: () => {
          // Reload suggestions to include the new one
          this.loadAutocompleteSuggestions();
        },
        error: (error) => {
          this.logger.error('Error saving delivery mode suggestion', error);
        }
      });
      
      this.deliveryModeInput = '';
      this.filteredDeliveryModeSuggestions = this.deliveryModeSuggestions;
    }
  }

  // Select suggestion from autocomplete
  selectLocationSuggestion(suggestion: string): void {
    this.locationInput = suggestion;
    this.addLocation();
  }

  selectDeliveryModeSuggestion(suggestion: string): void {
    this.deliveryModeInput = suggestion;
    this.addDeliveryMode();
  }

  removeDeliveryMode(mode: string): void {
    const modes = this.programForm.get('delivery_modes')?.value || [];
    this.programForm.patchValue({
      delivery_modes: modes.filter((m: string) => m !== mode)
    });
  }

  getLocations(): string[] {
    return this.program?.locations || [];
  }

  getDeliveryModes(): string[] {
    return this.program?.delivery_modes || [];
  }

  getPrerequisites(): number[] {
    return this.program?.prerequisites || [];
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    if (this.programForm.invalid || this.viewMode || this.isLoading) {
      return;
    }

    this.isLoading = true;

    // Build role definitions
    const roleDefinitions: RoleDefinition[] = this.roleDefinitions.controls.map(control => ({
      name: control.get('name')?.value,
      min_participants: control.get('min_participants')?.value,
      max_participants: control.get('max_participants')?.value,
      is_primary: control.get('is_primary')?.value
    }));

    // Build relationship config
    const relationshipConfig: RelationshipConfig = {
      allow_multiple_secondary: this.relationshipConfig.get('allow_multiple_secondary')?.value,
      max_secondary_per_primary: this.relationshipConfig.get('max_secondary_per_primary')?.value || null,
      require_pairing: this.relationshipConfig.get('require_pairing')?.value,
      progress_calculation: this.relationshipConfig.get('progress_calculation')?.value
    };

    if (this.isEditMode && this.program) {
      const updateData: ProgramUpdate = {
        title: this.programForm.value.title,
        description: this.programForm.value.description,
        is_active: this.programForm.value.is_active,
        role_definitions: roleDefinitions,
        relationship_config: relationshipConfig,
        locations: this.programForm.value.locations || [],
        delivery_modes: this.programForm.value.delivery_modes || [],
        prerequisites: this.programForm.value.prerequisites || []
      };

      this.programService.updateProgram(this.program.id, updateData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: () => {
            this.snackBar.open('Program updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.logger.error('Error updating program', error, { component: 'ProgramDialogComponent', programId: this.program?.id });
            this.snackBar.open('Error updating program', 'Close', { duration: 5000 });
          }
        });
    } else {
      const createData: ProgramCreate = {
        title: this.programForm.value.title,
        description: this.programForm.value.description,
        is_active: this.programForm.value.is_active,
        role_definitions: roleDefinitions,
        relationship_config: relationshipConfig,
        locations: this.programForm.value.locations || [],
        delivery_modes: this.programForm.value.delivery_modes || [],
        prerequisites: this.programForm.value.prerequisites || []
      };

      // If this is from an import, add PC event/list data
      if ((this.programForm as any).pcData) {
        const pcData = (this.programForm as any).pcData;
        if (pcData.planning_center_event_id) {
          createData.planning_center_event_id = pcData.planning_center_event_id;
          createData.planning_center_event_name = pcData.planning_center_event_name;
        }
        // Note: Programs don't currently have planning_center_list_id field in the schema
        // If needed, this could be stored as a custom attribute
      }

      this.programService.createProgram(createData)
        .pipe(finalize(() => this.isLoading = false))
        .subscribe({
          next: () => {
            this.snackBar.open('Program created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            this.logger.error('Error creating program', error, { component: 'ProgramDialogComponent' });
            this.snackBar.open('Error creating program', 'Close', { duration: 5000 });
          }
        });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  manageParticipants(): void {
    if (!this.program) return;
    
    this.dialog.open(ParticipantsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: this.program }
    });
  }

  managePairings(): void {
    if (!this.program) return;
    
    this.dialog.open(PairingsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: this.program }
    });
  }

  manageSessions(): void {
    if (!this.program) return;
    
    this.dialog.open(SessionsManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: this.program }
    });
  }

  manageProgress(): void {
    if (!this.program) return;
    
    this.dialog.open(ProgressManagementComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { program: this.program }
    });
  }

  manageContent(): void {
    if (!this.program) return;
    
    // Close the dialog and navigate to program content page
    this.dialogRef.close();
    this.router.navigate(['/churchcoursetracker/programs', this.program.id, 'content']);
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.programForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }

  shouldShowRoleError(roleFormGroup: AbstractControl | FormGroup, fieldName: string): boolean {
    if (!(roleFormGroup instanceof FormGroup)) {
      return false;
    }
    const field = roleFormGroup.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}

