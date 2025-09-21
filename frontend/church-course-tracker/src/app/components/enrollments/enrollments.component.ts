import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { EnrollmentService } from '../../services/enrollment.service';
import { CourseService } from '../../services/course.service';
import { MemberService } from '../../services/member.service';
import { Enrollment, Course, Person } from '../../models';
import { EnrollmentDialogComponent } from './enrollment-dialog/enrollment-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-enrollments',
  templateUrl: './enrollments.component.html',
  styleUrls: ['./enrollments.component.scss']
})
export class EnrollmentsComponent implements OnInit {
  displayedColumns: string[] = ['person_name', 'course_title', 'status', 'progress_percentage', 'enrolled_at', 'actions'];
  dataSource = new MatTableDataSource<Enrollment>();
  isLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private enrollmentService: EnrollmentService,
    private courseService: CourseService,
    private memberService: MemberService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadEnrollments();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadEnrollments(): void {
    this.isLoading = true;
    this.enrollmentService.getEnrollments().subscribe({
      next: (enrollments) => {
        this.dataSource.data = enrollments;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading enrollments:', error);
        this.isLoading = false;
      }
    });
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
    // Navigate to enrollment details or open detailed dialog
    console.log('View enrollment details:', enrollment);
  }
}
