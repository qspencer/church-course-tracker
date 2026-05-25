import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort, MatSortHeader } from '@angular/material/sort';
import { MatTableDataSource, MatTable, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCellDef, MatCell, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CourseService } from '../../services/course.service';
import { AuthService } from '../../services/auth.service';
import { LoggerService } from '../../services/logger.service';
import { Course, PlanningCenterImportData } from '../../models';
import { CourseDialogComponent } from './course-dialog/course-dialog.component';
import { ConfirmDialogComponent } from '../../shared/confirm-dialog/confirm-dialog.component';
import { PCImportDialogComponent, PCImportDialogData } from './pc-import-dialog/pc-import-dialog.component';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent } from '@angular/material/card';
import { MatFormField, MatLabel, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatChip } from '@angular/material/chips';
import { MatTooltip } from '@angular/material/tooltip';
import { SlicePipe, DatePipe } from '@angular/common';

@Component({
    selector: 'app-courses',
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.scss'],
    imports: [MatButton, MatIcon, MatCard, MatCardHeader, MatCardTitle, MatCardSubtitle, MatCardContent, MatFormField, MatLabel, MatInput, MatSuffix, MatProgressSpinner, MatTable, MatSort, MatColumnDef, MatHeaderCellDef, MatHeaderCell, MatCheckbox, MatCellDef, MatCell, MatSortHeader, MatChip, MatIconButton, MatTooltip, MatHeaderRowDef, MatHeaderRow, MatRowDef, MatRow, MatPaginator, SlicePipe, DatePipe]
})
export class CoursesComponent implements OnInit {
  displayedColumns: string[] = ['title', 'description', 'duration_weeks', 'is_active', 'created_at', 'actions'];
  dataSource = new MatTableDataSource<Course>();
  isLoading = true;

  // Bulk selection properties
  selectedCourses = new Set<number>();
  isDeleting = false;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private courseService: CourseService,
    private authService: AuthService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private logger: LoggerService,
    private router: Router
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
        this.logger.error('Error loading courses', error);
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

  openCourseDialog(course?: Course, importData?: PlanningCenterImportData): void {
    const dialogRef = this.dialog.open(CourseDialogComponent, {
      width: '1000px',
      maxWidth: '95vw',
      autoFocus: false, // Prevent auto-focus to reduce aria-hidden warnings
      restoreFocus: true, // Restore focus when dialog closes
      data: { course: course || null, importData: importData || null }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadCourses();
      }
    });
  }

  openImportDialog(): void {
    const dialogRef = this.dialog.open(PCImportDialogComponent, {
      width: '700px',
      data: { entityType: 'course' } as PCImportDialogData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Open course dialog with import data
        this.openCourseDialog(undefined, result);
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
            this.logger.error('Error deleting course', error);
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
        this.logger.error('Error updating course status', error);
      }
    });
  }

  viewCourseDetails(course: Course): void {
    // Open course details dialog in view mode
    this.dialog.open(CourseDialogComponent, {
      width: '1000px',
      maxWidth: '95vw',
      autoFocus: false, // Prevent auto-focus to reduce aria-hidden warnings
      restoreFocus: true, // Restore focus when dialog closes
      data: { 
        course: course,
        viewMode: true 
      }
    });
  }

  manageCourseContent(course: Course): void {
    // Navigate to course content management page
    this.router.navigate(['/courses', course.id, 'content']);
  }

  getStatusColor(isActive: boolean): string {
    return isActive ? 'primary' : 'warn';
  }

  getStatusText(isActive: boolean): string {
    return isActive ? 'Active' : 'Inactive';
  }

  // Role-based access control methods
  canCreateCourse(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canEditCourse(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  canDeleteCourse(): boolean {
    return this.authService.hasRole('admin');
  }

  canToggleCourseStatus(): boolean {
    return this.authService.hasAnyRole(['admin', 'staff']);
  }

  // Bulk selection methods
  get actualDisplayedColumns(): string[] {
    if (this.canDeleteCourse()) {
      return ['select', ...this.displayedColumns];
    }
    return this.displayedColumns;
  }

  toggleSelection(courseId: number): void {
    if (this.selectedCourses.has(courseId)) {
      this.selectedCourses.delete(courseId);
    } else {
      this.selectedCourses.add(courseId);
    }
  }

  isSelected(courseId: number): boolean {
    return this.selectedCourses.has(courseId);
  }

  getCurrentPageData(): Course[] {
    if (!this.paginator) {
      return this.dataSource.filteredData;
    }
    const startIndex = this.paginator.pageIndex * this.paginator.pageSize;
    const endIndex = startIndex + this.paginator.pageSize;
    return this.dataSource.filteredData.slice(startIndex, endIndex);
  }

  isAllSelected(): boolean {
    const currentPageData = this.getCurrentPageData();
    return currentPageData.length > 0 && currentPageData.every(course => this.selectedCourses.has(course.id));
  }

  isIndeterminate(): boolean {
    const currentPageData = this.getCurrentPageData();
    const selectedOnPage = currentPageData.filter(course => this.selectedCourses.has(course.id)).length;
    return selectedOnPage > 0 && selectedOnPage < currentPageData.length;
  }

  toggleSelectAll(): void {
    const currentPageData = this.getCurrentPageData();
    if (this.isAllSelected()) {
      // Deselect all on current page
      currentPageData.forEach(course => this.selectedCourses.delete(course.id));
    } else {
      // Select all on current page
      currentPageData.forEach(course => this.selectedCourses.add(course.id));
    }
  }

  selectAllFiltered(): void {
    this.dataSource.filteredData.forEach(course => this.selectedCourses.add(course.id));
  }

  clearSelection(): void {
    this.selectedCourses.clear();
  }

  getSelectedCount(): number {
    return this.selectedCourses.size;
  }

  bulkDeleteCourses(): void {
    const selectedIds = Array.from(this.selectedCourses);
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Courses',
        message: `Are you sure you want to delete ${selectedIds.length} course(s)? This action cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.isDeleting = true;
        this.courseService.bulkDeleteCourses(selectedIds).subscribe({
          next: (response) => {
            this.isDeleting = false;
            if (response.failed_ids.length > 0) {
              this.snackBar.open(
                `Deleted ${response.deleted_count} course(s). ${response.failed_ids.length} failed.`,
                'Close',
                { duration: 5000 }
              );
            } else {
              this.snackBar.open(
                `Successfully deleted ${response.deleted_count} course(s)`,
                'Close',
                { duration: 3000 }
              );
            }
            this.clearSelection();
            this.loadCourses();
          },
          error: (error) => {
            this.isDeleting = false;
            this.logger.error('Error bulk deleting courses', error);
            this.snackBar.open('Error deleting courses', 'Close', { duration: 3000 });
          }
        });
      }
    });
  }
}
