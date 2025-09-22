import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';

import { CoursesComponent } from './courses.component';
import { CourseService } from '../../services/course.service';
import { AuthService } from '../../services/auth.service';
import { Course } from '../../models';

describe('CoursesComponent', () => {
  let component: CoursesComponent;
  let fixture: ComponentFixture<CoursesComponent>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  const mockCourses: Course[] = [
    {
      id: 1,
      title: 'Test Course 1',
      description: 'Test Description 1',
      duration_weeks: 4,
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    },
    {
      id: 2,
      title: 'Test Course 2',
      description: 'Test Description 2',
      duration_weeks: 6,
      is_active: false,
      created_at: '2023-01-02T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z'
    }
  ];

  beforeEach(async () => {
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses', 'deleteCourse', 'updateCourse']);
    const authSpy = jasmine.createSpyObj('AuthService', ['hasRole', 'hasAnyRole']);
    const matDialogSpy = jasmine.createSpyObj('MatDialog', ['open']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [CoursesComponent],
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
        MatFormFieldModule,
        MatInputModule,
        MatProgressSpinnerModule,
        MatChipsModule,
        MatTooltipModule
      ],
      providers: [
        { provide: CourseService, useValue: courseSpy },
        { provide: AuthService, useValue: authSpy },
        { provide: MatDialog, useValue: matDialogSpy },
        { provide: MatSnackBar, useValue: matSnackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(CoursesComponent);
    component = fixture.componentInstance;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    dialogSpy = TestBed.inject(MatDialog) as jasmine.SpyObj<MatDialog>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;

    // Setup default return values
    courseServiceSpy.getCourses.and.returnValue(of(mockCourses));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with loading state', () => {
    expect(component.isLoading).toBe(true);
  });

  describe('ngOnInit', () => {
    it('should load courses on init', () => {
      component.ngOnInit();
      expect(courseServiceSpy.getCourses).toHaveBeenCalled();
    });
  });

  describe('loadCourses', () => {
    it('should load courses and update data source', () => {
      component.loadCourses();

      expect(courseServiceSpy.getCourses).toHaveBeenCalled();
      expect(component.dataSource.data).toEqual(mockCourses);
      expect(component.isLoading).toBe(false);
    });

    it('should handle loading error', () => {
      courseServiceSpy.getCourses.and.returnValue(throwError(() => new Error('Load error')));
      spyOn(console, 'error');

      component.loadCourses();

      expect(console.error).toHaveBeenCalledWith('Error loading courses:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('applyFilter', () => {
    beforeEach(() => {
      component.dataSource.data = mockCourses;
    });

    it('should filter data source', () => {
      const event = { target: { value: 'Test Course 1' } } as any;
      
      component.applyFilter(event);

      expect(component.dataSource.filter).toBe('test course 1');
    });
  });

  describe('openCourseDialog', () => {
    it('should open dialog for new course', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      spyOn(component, 'loadCourses');

      component.openCourseDialog();

      expect(dialogSpy.open).toHaveBeenCalledWith(jasmine.any(Function), {
        width: '600px',
        data: { course: null }
      });
      expect(component.loadCourses).toHaveBeenCalled();
    });

    it('should open dialog for existing course', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      spyOn(component, 'loadCourses');

      component.openCourseDialog(mockCourses[0]);

      expect(dialogSpy.open).toHaveBeenCalledWith(jasmine.any(Function), {
        width: '600px',
        data: { course: mockCourses[0] }
      });
    });
  });

  describe('deleteCourse', () => {
    it('should delete course after confirmation', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      courseServiceSpy.deleteCourse.and.returnValue(of(undefined));
      spyOn(component, 'loadCourses');

      component.deleteCourse(mockCourses[0]);

      expect(dialogSpy.open).toHaveBeenCalled();
      expect(courseServiceSpy.deleteCourse).toHaveBeenCalledWith(1);
      expect(snackBarSpy.open).toHaveBeenCalledWith('Course deleted successfully', 'Close', { duration: 3000 });
      expect(component.loadCourses).toHaveBeenCalled();
    });

    it('should not delete course if not confirmed', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(false));
      dialogSpy.open.and.returnValue(dialogRefSpy);

      component.deleteCourse(mockCourses[0]);

      expect(courseServiceSpy.deleteCourse).not.toHaveBeenCalled();
    });

    it('should handle delete error', () => {
      const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['afterClosed']);
      dialogRefSpy.afterClosed.and.returnValue(of(true));
      dialogSpy.open.and.returnValue(dialogRefSpy);
      courseServiceSpy.deleteCourse.and.returnValue(throwError(() => new Error('Delete error')));
      spyOn(console, 'error');

      component.deleteCourse(mockCourses[0]);

      expect(console.error).toHaveBeenCalledWith('Error deleting course:', jasmine.any(Error));
    });
  });

  describe('toggleCourseStatus', () => {
    it('should toggle course active status', () => {
      courseServiceSpy.updateCourse.and.returnValue(of(mockCourses[0]));
      spyOn(component, 'loadCourses');

      component.toggleCourseStatus(mockCourses[0]);

      expect(courseServiceSpy.updateCourse).toHaveBeenCalledWith(1, { is_active: false });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Course deactivated successfully', 'Close', { duration: 3000 });
      expect(component.loadCourses).toHaveBeenCalled();
    });

    it('should handle toggle error', () => {
      courseServiceSpy.updateCourse.and.returnValue(throwError(() => new Error('Update error')));
      spyOn(console, 'error');

      component.toggleCourseStatus(mockCourses[0]);

      expect(console.error).toHaveBeenCalledWith('Error updating course status:', jasmine.any(Error));
    });
  });

  describe('getStatusColor', () => {
    it('should return primary color for active courses', () => {
      expect(component.getStatusColor(true)).toBe('primary');
    });

    it('should return warn color for inactive courses', () => {
      expect(component.getStatusColor(false)).toBe('warn');
    });
  });

  describe('getStatusText', () => {
    it('should return Active for active courses', () => {
      expect(component.getStatusText(true)).toBe('Active');
    });

    it('should return Inactive for inactive courses', () => {
      expect(component.getStatusText(false)).toBe('Inactive');
    });
  });

  describe('editCourse', () => {
    it('should call openCourseDialog with course', () => {
      spyOn(component, 'openCourseDialog');

      component.editCourse(mockCourses[0]);

      expect(component.openCourseDialog).toHaveBeenCalledWith(mockCourses[0]);
    });
  });

  describe('viewCourseDetails', () => {
    it('should log course details', () => {
      spyOn(console, 'log');

      component.viewCourseDetails(mockCourses[0]);

      expect(console.log).toHaveBeenCalledWith('View course details:', mockCourses[0]);
    });
  });

  describe('template rendering', () => {
    beforeEach(() => {
      component.dataSource.data = mockCourses;
      component.isLoading = false;
      fixture.detectChanges();
    });

    it('should display course table', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.courses-table')).toBeTruthy();
    });

    it('should display search field', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.search-field')).toBeTruthy();
    });

    it('should display add course button', () => {
      const compiled = fixture.nativeElement;
      const addButton = compiled.querySelector('button[color="primary"]');
      expect(addButton.textContent).toContain('Add New Course');
    });

    it('should show loading spinner when loading', () => {
      component.isLoading = true;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-spinner')).toBeTruthy();
    });

    it('should show no data message when no courses', () => {
      component.dataSource.data = [];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.no-data')).toBeTruthy();
    });
  });

  describe('Role-based Access Control', () => {
    it('should allow admin to create courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canCreateCourse()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should allow staff to create courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canCreateCourse()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should not allow viewer to create courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(false);
      
      expect(component.canCreateCourse()).toBe(false);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should allow admin to edit courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canEditCourse()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should allow staff to edit courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canEditCourse()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should not allow viewer to edit courses', () => {
      authServiceSpy.hasAnyRole.and.returnValue(false);
      
      expect(component.canEditCourse()).toBe(false);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should allow admin to delete courses', () => {
      authServiceSpy.hasRole.and.returnValue(true);
      
      expect(component.canDeleteCourse()).toBe(true);
      expect(authServiceSpy.hasRole).toHaveBeenCalledWith('admin');
    });

    it('should not allow staff to delete courses', () => {
      authServiceSpy.hasRole.and.returnValue(false);
      
      expect(component.canDeleteCourse()).toBe(false);
      expect(authServiceSpy.hasRole).toHaveBeenCalledWith('admin');
    });

    it('should not allow viewer to delete courses', () => {
      authServiceSpy.hasRole.and.returnValue(false);
      
      expect(component.canDeleteCourse()).toBe(false);
      expect(authServiceSpy.hasRole).toHaveBeenCalledWith('admin');
    });

    it('should allow admin to toggle course status', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canToggleCourseStatus()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should allow staff to toggle course status', () => {
      authServiceSpy.hasAnyRole.and.returnValue(true);
      
      expect(component.canToggleCourseStatus()).toBe(true);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });

    it('should not allow viewer to toggle course status', () => {
      authServiceSpy.hasAnyRole.and.returnValue(false);
      
      expect(component.canToggleCourseStatus()).toBe(false);
      expect(authServiceSpy.hasAnyRole).toHaveBeenCalledWith(['admin', 'staff']);
    });
  });
});
