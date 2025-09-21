import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseService } from '../../services/course.service';
import { Course } from '../../models';
import { CourseDialogComponent } from './course-dialog/course-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss']
})
export class CoursesComponent implements OnInit {
  displayedColumns: string[] = ['title', 'description', 'duration_weeks', 'is_active', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Course>();
  isLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private courseService: CourseService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadCourses(): void {
    this.isLoading = true;
    this.courseService.getCourses().subscribe({
      next: (courses) => {
        this.dataSource.data = courses;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading courses:', error);
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

  openCourseDialog(course?: Course): void {
    const dialogRef = this.dialog.open(CourseDialogComponent, {
      width: '600px',
      data: { course: course || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCourses();
      }
    });
  }

  editCourse(course: Course): void {
    this.openCourseDialog(course);
  }

  deleteCourse(course: Course): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Course',
        message: `Are you sure you want to delete "${course.title}"? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.courseService.deleteCourse(course.id).subscribe({
          next: () => {
            this.snackBar.open('Course deleted successfully', 'Close', { duration: 3000 });
            this.loadCourses();
          },
          error: (error) => {
            console.error('Error deleting course:', error);
          }
        });
      }
    });
  }

  toggleCourseStatus(course: Course): void {
    const updatedCourse = { ...course, is_active: !course.is_active };
    this.courseService.updateCourse(course.id, { is_active: updatedCourse.is_active }).subscribe({
      next: () => {
        const status = updatedCourse.is_active ? 'activated' : 'deactivated';
        this.snackBar.open(`Course ${status} successfully`, 'Close', { duration: 3000 });
        this.loadCourses();
      },
      error: (error) => {
        console.error('Error updating course status:', error);
      }
    });
  }

  viewCourseDetails(course: Course): void {
    // Navigate to course details page or open detailed dialog
    console.log('View course details:', course);
  }

  getStatusColor(isActive: boolean): string {
    return isActive ? 'primary' : 'warn';
  }

  getStatusText(isActive: boolean): string {
    return isActive ? 'Active' : 'Inactive';
  }
}
