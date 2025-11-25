import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PlanningCenterService, PlanningCenterEvent, PlanningCenterList } from '../../../services/planning-center.service';
import { CourseService } from '../../../services/course.service';
import { ProgramService } from '../../../services/program.service';
import { EnrollmentService } from '../../../services/enrollment.service';
import { Course, Program } from '../../../models';

export interface BulkImportDialogData {
  targetType?: 'course' | 'program';
}

@Component({
  selector: 'app-bulk-enrollment-dialog',
  templateUrl: './bulk-enrollment-dialog.component.html',
  styleUrls: ['./bulk-enrollment-dialog.component.scss']
})
export class BulkEnrollmentDialogComponent implements OnInit {
  form: FormGroup;
  events: PlanningCenterEvent[] = [];
  lists: PlanningCenterList[] = [];
  courses: Course[] = [];
  programs: Program[] = [];
  isLoadingEvents = false;
  isLoadingLists = false;
  isLoadingCourses = false;
  isLoadingPrograms = false;
  isSubmitting = false;
  sourceType: 'event' | 'list' = 'event';
  targetType: 'course' | 'program' = 'course';

  constructor(
    private dialogRef: MatDialogRef<BulkEnrollmentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: BulkImportDialogData = {},
    private fb: FormBuilder,
    private planningCenterService: PlanningCenterService,
    private courseService: CourseService,
    private programService: ProgramService,
    private enrollmentService: EnrollmentService,
    private snackBar: MatSnackBar
  ) {
    // Set target type from data or default to 'course'
    this.targetType = data?.targetType || 'course';
    
    this.form = this.fb.group({
      target_type: [this.targetType],
      source_type: ['event'],
      pc_event_id: [''], // Conditional required
      pc_list_id: [''], // Conditional required
      course_id: [''], // Conditional required
      program_id: [''], // Conditional required
      role_name: [''], // Required for programs
      update_existing: [true]
    });

    // Update validators when target type changes
    this.form.get('target_type')?.valueChanges.subscribe(type => {
      this.targetType = type;
      if (type === 'course') {
        this.form.get('course_id')?.setValidators([Validators.required]);
        this.form.get('program_id')?.clearValidators();
        this.form.get('role_name')?.clearValidators();
        this.form.get('program_id')?.setValue('');
        this.form.get('role_name')?.setValue('');
      } else {
        this.form.get('program_id')?.setValidators([Validators.required]);
        this.form.get('role_name')?.setValidators([Validators.required]);
        this.form.get('course_id')?.clearValidators();
        this.form.get('course_id')?.setValue('');
      }
      this.form.get('course_id')?.updateValueAndValidity();
      this.form.get('program_id')?.updateValueAndValidity();
      this.form.get('role_name')?.updateValueAndValidity();
    });

    // Update validators when source type changes
    this.form.get('source_type')?.valueChanges.subscribe(type => {
      this.sourceType = type;
      if (type === 'event') {
        this.form.get('pc_event_id')?.setValidators([Validators.required]);
        this.form.get('pc_list_id')?.clearValidators();
        // Clear list value
        this.form.get('pc_list_id')?.setValue('');
      } else {
        this.form.get('pc_list_id')?.setValidators([Validators.required]);
        this.form.get('pc_event_id')?.clearValidators();
        // Clear event value
        this.form.get('pc_event_id')?.setValue('');
      }
      this.form.get('pc_event_id')?.updateValueAndValidity();
      this.form.get('pc_list_id')?.updateValueAndValidity();
    });
    
    // Initialize validators
    this.form.get('pc_event_id')?.setValidators([Validators.required]);
    if (this.targetType === 'course') {
      this.form.get('course_id')?.setValidators([Validators.required]);
    } else {
      this.form.get('program_id')?.setValidators([Validators.required]);
      this.form.get('role_name')?.setValidators([Validators.required]);
    }

    // Clear role selection when program changes
    this.form.get('program_id')?.valueChanges.subscribe(() => {
      this.form.get('role_name')?.setValue('');
    });
  }

  ngOnInit(): void {
    this.loadEvents();
    this.loadLists();
    if (this.targetType === 'course') {
      this.loadCourses();
    } else {
      this.loadPrograms();
    }

    // Load programs/courses when target type changes
    this.form.get('target_type')?.valueChanges.subscribe(type => {
      if (type === 'course' && this.courses.length === 0) {
        this.loadCourses();
      } else if (type === 'program' && this.programs.length === 0) {
        this.loadPrograms();
      }
    });
  }

  loadEvents(): void {
    this.isLoadingEvents = true;
    this.planningCenterService.getEvents().subscribe({
      next: (events) => {
        this.events = events;
        this.isLoadingEvents = false;
      },
      error: (error) => {
        console.error('Error loading PC events:', error);
        this.snackBar.open('Failed to load Planning Center events', 'Close', { duration: 3000 });
        this.isLoadingEvents = false;
      }
    });
  }

  loadLists(): void {
    this.isLoadingLists = true;
    this.planningCenterService.getLists().subscribe({
      next: (lists) => {
        this.lists = lists;
        this.isLoadingLists = false;
      },
      error: (error) => {
        console.error('Error loading PC lists:', error);
        this.snackBar.open('Failed to load Planning Center lists', 'Close', { duration: 3000 });
        this.isLoadingLists = false;
      }
    });
  }

  loadCourses(): void {
    this.isLoadingCourses = true;
    this.courseService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.isLoadingCourses = false;
      },
      error: (error) => {
        console.error('Error loading courses:', error);
        this.snackBar.open('Failed to load courses', 'Close', { duration: 3000 });
        this.isLoadingCourses = false;
      }
    });
  }

  loadPrograms(): void {
    this.isLoadingPrograms = true;
    this.programService.getPrograms({ is_active: true }).subscribe({
      next: (programs) => {
        this.programs = programs;
        this.isLoadingPrograms = false;
      },
      error: (error) => {
        console.error('Error loading programs:', error);
        this.snackBar.open('Failed to load programs', 'Close', { duration: 3000 });
        this.isLoadingPrograms = false;
      }
    });
  }

  getSelectedProgramRoles(): string[] {
    const programId = this.form.get('program_id')?.value;
    if (!programId) return [];
    
    const program = this.programs.find(p => p.id === programId);
    if (!program || !program.role_definitions) return [];
    
    return program.role_definitions.map((r: any) => r.name);
  }

  onSubmit(): void {
    if (this.form.invalid) {
      return;
    }

    this.isSubmitting = true;
    const { target_type, source_type, pc_event_id, pc_list_id, course_id, program_id, role_name, update_existing } = this.form.value;

    if (target_type === 'course') {
      // Course enrollment logic
      if (source_type === 'event') {
        this.enrollmentService.bulkEnrollFromPCEvent({
          course_id,
          pc_event_id,
          update_existing
        }).subscribe({
          next: (result: any) => this.handleSuccess(result, 'enrollments'),
          error: (error: any) => this.handleError(error)
        });
      } else {
        this.enrollmentService.bulkEnrollFromPCList({
          course_id,
          pc_list_id,
          update_existing
        }).subscribe({
          next: (result: any) => this.handleSuccess(result, 'enrollments'),
          error: (error: any) => this.handleError(error)
        });
      }
    } else {
      // Program participant logic
      if (source_type === 'event') {
        this.programService.bulkImportParticipantsFromPCEvent({
          program_id,
          pc_event_id,
          role_name,
          update_existing
        }).subscribe({
          next: (result: any) => this.handleSuccess(result, 'participants'),
          error: (error: any) => this.handleError(error)
        });
      } else {
        this.programService.bulkImportParticipantsFromPCList({
          program_id,
          pc_list_id,
          role_name,
          update_existing
        }).subscribe({
          next: (result: any) => this.handleSuccess(result, 'participants'),
          error: (error: any) => this.handleError(error)
        });
      }
    }
  }

  private handleSuccess(result: any, type: 'enrollments' | 'participants'): void {
    const count = result.length || result.count || 0;
    const message = type === 'enrollments' 
      ? `Successfully processed ${count} enrollments from Planning Center`
      : `Successfully processed ${count} participants from Planning Center. View them in the Programs Management page.`;
    this.snackBar.open(message, 'Close', { duration: 7000 });
    this.dialogRef.close(true);
    this.isSubmitting = false;
  }

  private handleError(error: any): void {
    console.error('Error processing bulk enrollment:', error);
    this.snackBar.open('Failed to process bulk enrollment', 'Close', { duration: 5000 });
    this.isSubmitting = false;
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
