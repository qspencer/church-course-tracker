import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseService } from '../../../services/course.service';
import { UserService } from '../../../services/user.service';
import { AutocompleteSuggestionService } from '../../../services/autocomplete-suggestion.service';
import { Course, CourseCreate, CourseUpdate, User } from '../../../models';
import { EventRegistrationsDialogComponent } from '../event-registrations-dialog/event-registrations-dialog.component';

export interface CourseDialogData {
  course: Course | null;
  viewMode?: boolean; // If true, show read-only view
  importData?: any; // Data from Planning Center import
}

@Component({
  selector: 'app-course-dialog',
  templateUrl: './course-dialog.component.html',
  styleUrls: ['./course-dialog.component.scss']
})
export class CourseDialogComponent implements OnInit {
  courseForm: FormGroup;
  isEditing: boolean;
  viewMode: boolean;
  isLoading = false;
  isSubmitted = false; // Track if form has been submitted
  course: Course | null = null;
  availablePrerequisites: Course[] = [];
  loadingPrerequisites = false;
  availableUsers: User[] = [];
  loadingUsers = false;
  
  // For chip inputs (locations and delivery modes)
  locationInput = '';
  deliveryModeInput = '';
  
  // Autocomplete suggestions
  locationSuggestions: string[] = [];
  deliveryModeSuggestions: string[] = [];
  filteredLocationSuggestions: string[] = [];
  filteredDeliveryModeSuggestions: string[] = [];

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    private userService: UserService,
    private autocompleteService: AutocompleteSuggestionService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<CourseDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CourseDialogData
  ) {
    this.viewMode = data.viewMode || false;
    this.isEditing = !!data.course && !this.viewMode;
    this.course = data.course || null;
    
    this.courseForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(10)]],
      duration_weeks: [1, [Validators.required, Validators.min(1), Validators.max(52)]],
      prerequisites: [[]],
      instructors: [[]],
      locations: [[]],
      delivery_modes: [[]]
    });
  }

  ngOnInit(): void {
    this.loadAvailablePrerequisites();
    // Load users for both view and edit modes (needed for instructor display)
    this.loadAvailableUsers();
    this.loadAutocompleteSuggestions();
    
    // If import data is provided, populate form with it
    if (this.data.importData) {
      const importData = this.data.importData.previewData;
      this.courseForm.patchValue({
        title: importData.title || '',
        description: importData.description || '',
        duration_weeks: importData.duration_weeks || 1,
        prerequisites: [],
        instructors: [],
        locations: importData.locations || [],
        delivery_modes: importData.delivery_modes || []
      });
      // Store PC event data for later use in submission
      (this.courseForm as any).pcEventData = {
        planning_center_event_id: importData.planning_center_event_id,
        planning_center_event_name: importData.planning_center_event_name,
        event_start_date: importData.event_start_date,
        event_end_date: importData.event_end_date,
        max_capacity: importData.max_capacity
      };
    } else if (this.data.course) {
      if (this.viewMode) {
        // In view mode, just store the course data
        this.course = this.data.course;
      } else {
        // In edit mode, populate the form
        const prerequisites = Array.isArray(this.data.course.prerequisites) 
          ? this.data.course.prerequisites 
          : [];
        const instructors = Array.isArray(this.data.course.instructors)
          ? this.data.course.instructors
          : [];
        const locations = Array.isArray(this.data.course.locations)
          ? this.data.course.locations
          : [];
        const deliveryModes = Array.isArray(this.data.course.delivery_modes)
          ? this.data.course.delivery_modes
          : [];
        this.courseForm.patchValue({
          title: this.data.course.title,
          description: this.data.course.description,
          duration_weeks: this.data.course.duration_weeks,
          prerequisites: prerequisites,
          instructors: instructors,
          locations: locations,
          delivery_modes: deliveryModes
        });
      }
    }
  }

  loadAvailablePrerequisites(): void {
    if (this.viewMode) return;
    
    this.loadingPrerequisites = true;
    this.courseService.getAvailablePrerequisites().subscribe({
      next: (courses) => {
        // Filter out the current course if editing
        if (this.isEditing && this.data.course) {
          this.availablePrerequisites = courses.filter(c => c.id !== this.data.course!.id);
        } else {
          this.availablePrerequisites = courses;
        }
        this.loadingPrerequisites = false;
      },
      error: (error) => {
        console.error('Error loading prerequisites:', error);
        this.loadingPrerequisites = false;
      }
    });
  }

  loadAvailableUsers(): void {
    this.loadingUsers = true;
    // Load only instructors for the instructors dropdown
    this.userService.getInstructors().subscribe({
      next: (users) => {
        this.availableUsers = users.filter(u => u.is_active);
        this.loadingUsers = false;
      },
      error: (error) => {
        console.error('Error loading instructors:', error);
        // Fallback to all users if instructor filter fails
        this.userService.getUsers().subscribe({
          next: (users) => {
            this.availableUsers = users.filter(u => u.is_active);
            this.loadingUsers = false;
          },
          error: (err) => {
            console.error('Error loading users:', err);
            this.loadingUsers = false;
          }
        });
      }
    });
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;
    
    // Prevent multiple submissions
    if (this.isLoading || !this.courseForm.valid) {
      return;
    }
    
    this.isLoading = true;
    const formValue = this.courseForm.value;

    if (this.isEditing && this.data.course) {
      // Update existing course
      const updateData: CourseUpdate = {
        title: formValue.title,
        description: formValue.description,
        duration_weeks: formValue.duration_weeks,
        prerequisites: formValue.prerequisites || [],
        instructors: formValue.instructors || [],
        locations: formValue.locations || [],
        delivery_modes: formValue.delivery_modes || []
      };

      this.courseService.updateCourse(this.data.course.id, updateData).subscribe({
        next: (course) => {
          this.isLoading = false;
          this.snackBar.open('Course updated successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(course);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error updating course:', error);
          // Extract error message
          let errorMessage = 'Failed to update course. Please try again.';
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to update courses.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid course data. Please check your input.';
          }
          // Error interceptor will also show a snackbar, but we show a more specific one here
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    } else {
      // Create new course
      const createData: CourseCreate = {
        title: formValue.title,
        description: formValue.description,
        duration_weeks: formValue.duration_weeks,
        prerequisites: formValue.prerequisites || [],
        instructors: formValue.instructors || [],
        locations: formValue.locations || [],
        delivery_modes: formValue.delivery_modes || []
      };

      // If this is from an import, add PC event data
      if ((this.courseForm as any).pcEventData) {
        const pcData = (this.courseForm as any).pcEventData;
        createData.planning_center_event_id = pcData.planning_center_event_id;
        createData.planning_center_event_name = pcData.planning_center_event_name;
        createData.event_start_date = pcData.event_start_date;
        createData.event_end_date = pcData.event_end_date;
        createData.max_capacity = pcData.max_capacity;
      }

      this.courseService.createCourse(createData).subscribe({
        next: (course) => {
          this.isLoading = false;
          this.snackBar.open('Course created successfully', 'Close', { duration: 3000 });
          this.dialogRef.close(course);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error creating course:', error);
          
          // If it's an auth error (401), user will be logged out by interceptor
          // Don't show course-specific error message for auth errors
          if (error?.status === 401) {
            // User will be redirected to login by auth service
            return;
          }
          
          // Extract error message
          let errorMessage = 'Failed to create course. Please try again.';
          if (error?.message && error.message.includes('session has expired')) {
            errorMessage = error.message;
          } else if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.error?.message) {
            errorMessage = error.error.message;
          } else if (error?.status === 403) {
            errorMessage = 'You do not have permission to create courses.';
          } else if (error?.status === 400) {
            errorMessage = 'Invalid course data. Please check your input.';
          }
          
          // Error interceptor will also show a snackbar, but we show a more specific one here
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onClose(): void {
    this.dialogRef.close();
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  }

  formatDuration(weeks: number | undefined): string {
    if (!weeks) return 'N/A';
    if (weeks === 1) return '1 week';
    if (weeks < 52) return `${weeks} weeks`;
    const years = Math.floor(weeks / 52);
    const remainingWeeks = weeks % 52;
    if (remainingWeeks === 0) {
      return years === 1 ? '1 year' : `${years} years`;
    }
    return `${years} year${years > 1 ? 's' : ''}, ${remainingWeeks} week${remainingWeeks > 1 ? 's' : ''}`;
  }

  getErrorMessage(fieldName: string): string {
    const field = this.courseForm.get(fieldName);
    // Only show errors if field has been touched or form has been submitted
    if (!field || (!field.touched && !this.isSubmitted)) {
      return '';
    }
    
    if (field.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field.hasError('minlength')) {
      return `${fieldName} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    if (field.hasError('min')) {
      return `${fieldName} must be at least ${field.errors?.['min'].min}`;
    }
    if (field.hasError('max')) {
      return `${fieldName} must be at most ${field.errors?.['max'].max}`;
    }
    return '';
  }
  
  shouldShowError(fieldName: string): boolean {
    const field = this.courseForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }

  hasPrerequisites(): boolean {
    if (!this.course || !this.course.prerequisites) {
      return false;
    }
    return Array.isArray(this.course.prerequisites) && this.course.prerequisites.length > 0;
  }

  getPrerequisites(): number[] {
    if (!this.course || !this.course.prerequisites) {
      return [];
    }
    return Array.isArray(this.course.prerequisites) ? this.course.prerequisites : [];
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
        console.error('Error loading location suggestions:', error);
      }
    });

    // Load delivery mode suggestions
    this.autocompleteService.getSuggestions('delivery_mode').subscribe({
      next: (suggestions) => {
        this.deliveryModeSuggestions = suggestions;
        this.filteredDeliveryModeSuggestions = suggestions;
      },
      error: (error) => {
        console.error('Error loading delivery mode suggestions:', error);
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

  // Helper methods for chip inputs
  addLocation(): void {
    const location = this.locationInput.trim();
    if (location && !this.courseForm.value.locations.includes(location)) {
      const currentLocations = this.courseForm.value.locations || [];
      this.courseForm.patchValue({
        locations: [...currentLocations, location]
      });
      
      // Save to autocomplete suggestions
      this.autocompleteService.addSuggestion('location', location).subscribe({
        next: () => {
          // Reload suggestions to include the new one
          this.loadAutocompleteSuggestions();
        },
        error: (error) => {
          console.error('Error saving location suggestion:', error);
        }
      });
      
      this.locationInput = '';
      this.filteredLocationSuggestions = this.locationSuggestions;
    }
  }

  removeLocation(location: string): void {
    const currentLocations = this.courseForm.value.locations || [];
    this.courseForm.patchValue({
      locations: currentLocations.filter((l: string) => l !== location)
    });
  }

  addDeliveryMode(): void {
    const mode = this.deliveryModeInput.trim();
    if (mode && !this.courseForm.value.delivery_modes.includes(mode)) {
      const currentModes = this.courseForm.value.delivery_modes || [];
      this.courseForm.patchValue({
        delivery_modes: [...currentModes, mode]
      });
      
      // Save to autocomplete suggestions
      this.autocompleteService.addSuggestion('delivery_mode', mode).subscribe({
        next: () => {
          // Reload suggestions to include the new one
          this.loadAutocompleteSuggestions();
        },
        error: (error) => {
          console.error('Error saving delivery mode suggestion:', error);
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
    const currentModes = this.courseForm.value.delivery_modes || [];
    this.courseForm.patchValue({
      delivery_modes: currentModes.filter((m: string) => m !== mode)
    });
  }

  // Helper methods for view mode
  getInstructorDisplay(instructor: number | string): string {
    if (instructor === 'TBD') {
      return 'TBD';
    }
    if (typeof instructor === 'number') {
      const user = this.availableUsers.find(u => u.id === instructor);
      return user ? user.full_name : `User ID: ${instructor}`;
    }
    return String(instructor);
  }

  getInstructors(): (number | string)[] {
    if (!this.course || !this.course.instructors) {
      return [];
    }
    return Array.isArray(this.course.instructors) ? this.course.instructors : [];
  }

  getLocations(): string[] {
    if (!this.course || !this.course.locations) {
      return [];
    }
    return Array.isArray(this.course.locations) ? this.course.locations : [];
  }

  getDeliveryModes(): string[] {
    if (!this.course || !this.course.delivery_modes) {
      return [];
    }
    return Array.isArray(this.course.delivery_modes) ? this.course.delivery_modes : [];
  }

  viewEventRegistrations(): void {
    if (!this.course?.planning_center_event_id) {
      this.snackBar.open('This course does not have a Planning Center event ID', 'Close', { duration: 3000 });
      return;
    }

    const dialogRef = this.dialog.open(EventRegistrationsDialogComponent, {
      width: '800px',
      maxWidth: '90vw',
      data: {
        eventId: this.course.planning_center_event_id,
        eventName: this.course.planning_center_event_name || this.course.title,
        courseId: this.course.id
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.imported) {
        this.snackBar.open(`Successfully imported ${result.count} registration(s) as enrollments`, 'Close', { duration: 5000 });
      }
    });
  }
}
