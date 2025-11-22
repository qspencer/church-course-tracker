import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PlanningCenterService, PlanningCenterEvent, PlanningCenterList } from '../../../services/planning-center.service';
import { CourseService } from '../../../services/course.service';
import { EnrollmentService } from '../../../services/enrollment.service';
import { Course } from '../../../models';

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
  isLoadingEvents = false;
  isLoadingLists = false;
  isLoadingCourses = false;
  isSubmitting = false;
  sourceType: 'event' | 'list' = 'event';

  constructor(
    private dialogRef: MatDialogRef<BulkEnrollmentDialogComponent>,
    private fb: FormBuilder,
    private planningCenterService: PlanningCenterService,
    private courseService: CourseService,
    private enrollmentService: EnrollmentService,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      source_type: ['event'],
      pc_event_id: [''], // Conditional required
      pc_list_id: [''], // Conditional required
      course_id: ['', Validators.required],
      update_existing: [true]
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
  }

  ngOnInit(): void {
    this.loadEvents();
    this.loadLists();
    this.loadCourses();
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

  onSubmit(): void {
    if (this.form.invalid) {
      return;
    }

    this.isSubmitting = true;
    const { source_type, pc_event_id, pc_list_id, course_id, update_existing } = this.form.value;

    if (source_type === 'event') {
      this.enrollmentService.bulkEnrollFromPCEvent({
        course_id,
        pc_event_id,
        update_existing
      }).subscribe({
        next: (result: any) => this.handleSuccess(result),
        error: (error: any) => this.handleError(error)
      });
    } else {
      this.enrollmentService.bulkEnrollFromPCList({
        course_id,
        pc_list_id,
        update_existing
      }).subscribe({
        next: (result: any) => this.handleSuccess(result),
        error: (error: any) => this.handleError(error)
      });
    }
  }

  private handleSuccess(result: any): void {
    const count = result.length;
    this.snackBar.open(`Successfully processed ${count} enrollments from Planning Center`, 'Close', { duration: 5000 });
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
