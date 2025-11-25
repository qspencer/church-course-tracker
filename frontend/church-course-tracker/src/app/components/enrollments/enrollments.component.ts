import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { EnrollmentService } from '../../services/enrollment.service';
import { ProgramService } from '../../services/program.service';
import { CourseService } from '../../services/course.service';
import { MemberService } from '../../services/member.service';
import { Enrollment, Course, Person } from '../../models';
import { ProgramParticipant, Program } from '../../models/program.model';
import { EnrollmentDialogComponent } from './enrollment-dialog/enrollment-dialog.component';
import { BulkEnrollmentDialogComponent } from './bulk-enrollment-dialog/bulk-enrollment-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-enrollments',
  templateUrl: './enrollments.component.html',
  styleUrls: ['./enrollments.component.scss']
})
export class EnrollmentsComponent implements OnInit {
  viewMode: 'courses' | 'programs' = 'courses';
  displayedColumns: string[] = ['person_name', 'course_title', 'status', 'progress_percentage', 'enrolled_at', 'actions'];
  dataSource = new MatTableDataSource<any>();
  isLoading = true;
  enrollments: Enrollment[] = [];
  participants: ProgramParticipant[] = [];
  programs: Program[] = [];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private enrollmentService: EnrollmentService,
    private programService: ProgramService,
    private courseService: CourseService,
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {
    console.log('EnrollmentsComponent constructor called');
    console.log('Current route:', window.location.pathname);
  }

  ngOnInit(): void {
    this.loadData();
    this.loadPrograms();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onViewModeChange(): void {
    this.loadData();
  }

  loadData(): void {
    if (this.viewMode === 'courses') {
      this.loadEnrollments();
    } else {
      this.loadParticipants();
    }
  }

  loadEnrollments(): void {
    this.isLoading = true;
    this.enrollmentService.getEnrollments().subscribe({
      next: (enrollments) => {
        this.enrollments = enrollments;
        this.dataSource.data = enrollments;
        this.updateDisplayedColumns();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading enrollments:', error);
        this.isLoading = false;
      }
    });
  }

  loadParticipants(): void {
    this.isLoading = true;
    this.programService.getAllProgramParticipants('active').subscribe({
      next: (participants) => {
        this.participants = participants;
        this.dataSource.data = participants;
        this.updateDisplayedColumns();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading participants:', error);
        this.isLoading = false;
      }
    });
  }

  loadPrograms(): void {
    this.programService.getPrograms({ is_active: true }).subscribe({
      next: (programs) => {
        this.programs = programs;
      },
      error: (error) => {
        console.error('Error loading programs:', error);
      }
    });
  }

  updateDisplayedColumns(): void {
    if (this.viewMode === 'courses') {
      this.displayedColumns = ['person_name', 'course_title', 'status', 'progress_percentage', 'enrolled_at', 'actions'];
    } else {
      this.displayedColumns = ['person_name', 'program_title', 'role_name', 'status', 'progress_percentage', 'start_date', 'actions'];
    }
  }

  applyFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  openEnrollmentDialog(enrollment?: Enrollment): void {
    const dialogRef = this.dialog.open(EnrollmentDialogComponent, {
      width: '600px',
      data: { enrollment: enrollment || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadEnrollments();
      }
    });
  }

  openBulkImportDialog(): void {
    const dialogRef = this.dialog.open(BulkEnrollmentDialogComponent, {
      width: '600px',
      data: { targetType: this.viewMode === 'courses' ? 'course' : 'program' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadData();
      }
    });
  }

  editEnrollment(enrollment: Enrollment): void {
    this.openEnrollmentDialog(enrollment);
  }

  deleteEnrollment(enrollment: Enrollment): void {
    const personName = enrollment.person ? `${enrollment.person.first_name} ${enrollment.person.last_name}` : 'Unknown';
    const courseTitle = enrollment.course ? enrollment.course.title : 'Unknown Course';
    
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Enrollment',
        message: `Are you sure you want to delete the enrollment for "${personName}" in "${courseTitle}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.enrollmentService.deleteEnrollment(enrollment.id).subscribe({
          next: () => {
            this.snackBar.open('Enrollment deleted successfully', 'Close', { duration: 3000 });
            this.loadEnrollments();
          },
          error: (error) => {
            console.error('Error deleting enrollment:', error);
          }
        });
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

  getStatusText(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'enrolled':
        return 'Enrolled';
      case 'dropped':
        return 'Dropped';
      default:
        return status;
    }
  }

  getProgressColor(progress: number): string {
    if (progress >= 80) return 'primary';
    if (progress >= 50) return 'accent';
    if (progress >= 25) return 'warn';
    return 'basic';
  }

  viewEnrollmentDetails(enrollment: Enrollment): void {
    this.enrollmentService.getEnrollment(enrollment.id).subscribe({
      next: (fullEnrollment) => {
        this.dialog.open(EnrollmentDialogComponent, {
          width: '650px',
          maxWidth: '95vw',
          data: {
            enrollment: fullEnrollment,
            viewMode: true
          }
        });
      },
      error: (error) => {
        console.error('Error loading enrollment details:', error);
        this.snackBar.open('Failed to load enrollment details', 'Close', { duration: 3000 });
      }
    });
  }

  getPersonName(item: any): string {
    if (this.viewMode === 'courses') {
      return `${item.person?.first_name || ''} ${item.person?.last_name || ''}`.trim() || 'Unknown';
    } else {
      // For participants, check if person data is included
      if (item.person) {
        return `${item.person?.first_name || ''} ${item.person?.last_name || ''}`.trim() || 'Unknown';
      } else if (item.people) {
        return `${item.people?.first_name || ''} ${item.people?.last_name || ''}`.trim() || 'Unknown';
      }
      return `Participant ${item.id}`;
    }
  }

  getPersonEmail(item: any): string {
    if (this.viewMode === 'courses') {
      return item.person?.email || '';
    } else {
      return item.person?.email || item.people?.email || '';
    }
  }

  getProgramTitle(programId: number): string {
    const program = this.programs.find(p => p.id === programId);
    return program?.title || `Program ${programId}`;
  }
}
