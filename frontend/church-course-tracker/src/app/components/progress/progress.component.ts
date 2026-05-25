import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProgressService } from '../../services/progress.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { CourseService } from '../../services/course.service';
import { MemberService } from '../../services/member.service';
import { Progress, Enrollment, Course, Person, ProgressStatus } from '../../models';
import { LoggerService } from '../../services/logger.service';

@Component({
    selector: 'app-progress',
    templateUrl: './progress.component.html',
    styleUrls: ['./progress.component.scss'],
    standalone: false
})
export class ProgressComponent implements OnInit {
  enrollments: Enrollment[] = [];
  courses: Course[] = [];
  members: Person[] = [];
  selectedEnrollment: Enrollment | null = null;
  progressItems: Progress[] = [];
  isLoading = true;
  isUpdating = false;

  // Filters
  courseFilter = new FormControl('');
  memberFilter = new FormControl('');
  statusFilter = new FormControl('');

  statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'enrolled', label: 'Enrolled' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'dropped', label: 'Dropped' }
  ];

  constructor(
    private progressService: ProgressService,
    private enrollmentService: EnrollmentService,
    private courseService: CourseService,
    private memberService: MemberService,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {}

  ngOnInit(): void {
    this.loadData();
    this.setupFilters();
  }

  loadData(): void {
    this.isLoading = true;
    
    // Load enrollments with progress data
    this.enrollmentService.getEnrollments().subscribe({
      next: (enrollments) => {
        this.enrollments = enrollments;
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading enrollments', error, {
          component: 'ProgressComponent',
          action: 'loadData'
        });
        this.snackBar.open('Error loading enrollments', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });

    // Load courses and members for filters
    this.courseService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
      },
      error: (error) => {
        this.logger.error('Error loading courses', error, {
          component: 'ProgressComponent',
          action: 'loadData'
        });
      }
    });

    this.memberService.getMembers().subscribe({
      next: (members) => {
        this.members = members;
      },
      error: (error) => {
        this.logger.error('Error loading members', error, {
          component: 'ProgressComponent',
          action: 'loadData'
        });
      }
    });
  }

  setupFilters(): void {
    this.courseFilter.valueChanges.subscribe(() => this.applyFilters());
    this.memberFilter.valueChanges.subscribe(() => this.applyFilters());
    this.statusFilter.valueChanges.subscribe(() => this.applyFilters());
  }

  applyFilters(): void {
    // Filter logic would be implemented here
    // For now, we'll keep it simple
  }

  selectEnrollment(enrollment: Enrollment): void {
    this.selectedEnrollment = enrollment;
    this.loadProgressDetails(enrollment.id);
  }

  loadProgressDetails(enrollmentId: number): void {
    this.progressService.getProgressByEnrollment(enrollmentId).subscribe({
      next: (progress) => {
        this.progressItems = progress;
      },
      error: (error) => {
        this.logger.error('Error loading progress details', error, {
          component: 'ProgressComponent',
          action: 'loadProgressDetails',
          enrollmentId
        });
        this.snackBar.open('Error loading progress details', 'Close', { duration: 3000 });
      }
    });
  }

  updateProgressStatus(progressId: number, status: ProgressStatus): void {
    this.isUpdating = true;
    this.progressService.updateProgress(progressId, status).subscribe({
      next: (updatedProgress) => {
        // Update the progress item in the list
        const index = this.progressItems.findIndex(p => p.id === progressId);
        if (index !== -1) {
          this.progressItems[index] = updatedProgress;
        }
        
        // Refresh enrollment data to update overall progress
        if (this.selectedEnrollment) {
          this.loadProgressDetails(this.selectedEnrollment.id);
        }
        
        this.snackBar.open('Progress updated successfully', 'Close', { duration: 3000 });
        this.isUpdating = false;
      },
      error: (error) => {
        this.logger.error('Error updating progress', error, {
          component: 'ProgressComponent',
          action: 'updateProgressStatus',
          progressId
        });
        this.snackBar.open('Error updating progress', 'Close', { duration: 3000 });
        this.isUpdating = false;
      }
    });
  }

  markContentComplete(enrollmentId: number, contentId: number): void {
    this.isUpdating = true;
    this.progressService.markContentComplete(enrollmentId, contentId).subscribe({
      next: () => {
        this.loadProgressDetails(enrollmentId);
        this.snackBar.open('Content marked as complete', 'Close', { duration: 3000 });
        this.isUpdating = false;
      },
      error: (error) => {
        this.logger.error('Error marking content complete', error, {
          component: 'ProgressComponent',
          action: 'markContentComplete',
          enrollmentId,
          contentId
        });
        this.snackBar.open('Error marking content complete', 'Close', { duration: 3000 });
        this.isUpdating = false;
      }
    });
  }

  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'primary';
      case 'in_progress':
        return 'accent';
      case 'enrolled':
        return 'basic';
      case 'dropped':
        return 'warn';
      default:
        return 'basic';
    }
  }

  getProgressStatusColor(status: ProgressStatus): string {
    switch (status) {
      case ProgressStatus.COMPLETED:
        return '#4CAF50';
      case ProgressStatus.IN_PROGRESS:
        return '#FF9800';
      case ProgressStatus.NOT_STARTED:
        return '#9E9E9E';
      default:
        return '#9E9E9E';
    }
  }

  getProgressStatusIcon(status: ProgressStatus): string {
    switch (status) {
      case ProgressStatus.COMPLETED:
        return 'check_circle';
      case ProgressStatus.IN_PROGRESS:
        return 'play_circle';
      case ProgressStatus.NOT_STARTED:
        return 'radio_button_unchecked';
      default:
        return 'radio_button_unchecked';
    }
  }

  getOverallProgress(enrollment: Enrollment): number {
    return enrollment.progress_percentage || 0;
  }

  getPersonName(person: Person | undefined): string {
    if (!person) return 'Unknown';
    return `${person.first_name} ${person.last_name}`;
  }

  refreshData(): void {
    this.loadData();
    if (this.selectedEnrollment) {
      this.loadProgressDetails(this.selectedEnrollment.id);
    }
  }
}
