import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';

// Chart.js
import { NgChartsModule } from 'ng2-charts';

import { DashboardComponent } from './dashboard.component';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { DashboardStats, Course, Enrollment } from '../../models';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let reportServiceSpy: jasmine.SpyObj<ReportService>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let enrollmentServiceSpy: jasmine.SpyObj<EnrollmentService>;

  const mockStats: DashboardStats = {
    total_courses: 10,
    active_courses: 8,
    total_enrollments: 50,
    completed_enrollments: 25,
    total_members: 30,
    completion_rate: 50
  };

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
      is_active: true,
      created_at: '2023-01-02T00:00:00Z',
      updated_at: '2023-01-02T00:00:00Z'
    }
  ];

  const mockEnrollments: Enrollment[] = [
    {
      id: 1,
      person_id: 1,
      course_id: 1,
      enrolled_at: '2023-01-01T00:00:00Z',
      status: 'enrolled' as any,
      progress_percentage: 75,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    }
  ];

  const mockCompletionTrends = [
    { date: '2023-01-01', enrollments: 5, completions: 2 },
    { date: '2023-01-02', enrollments: 8, completions: 4 },
    { date: '2023-01-03', enrollments: 6, completions: 3 }
  ];

  beforeEach(async () => {
    const reportSpy = jasmine.createSpyObj('ReportService', ['getDashboardStats', 'getCompletionTrends']);
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['getEnrollments']);

    await TestBed.configureTestingModule({
      declarations: [DashboardComponent],
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatProgressBarModule,
        MatChipsModule,
        NgChartsModule
      ],
      providers: [
        { provide: ReportService, useValue: reportSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: EnrollmentService, useValue: enrollmentSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    reportServiceSpy = TestBed.inject(ReportService) as jasmine.SpyObj<ReportService>;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    enrollmentServiceSpy = TestBed.inject(EnrollmentService) as jasmine.SpyObj<EnrollmentService>;
  });

  beforeEach(() => {
    // Setup default return values
    reportServiceSpy.getDashboardStats.and.returnValue(of(mockStats));
    reportServiceSpy.getCompletionTrends.and.returnValue(of(mockCompletionTrends));
    courseServiceSpy.getCourses.and.returnValue(of(mockCourses));
    enrollmentServiceSpy.getEnrollments.and.returnValue(of(mockEnrollments));
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with loading state', () => {
    expect(component.isLoading).toBe(true);
    expect(component.stats).toBeNull();
  });

  describe('ngOnInit', () => {
    it('should load dashboard data on init', () => {
      component.ngOnInit();

      expect(reportServiceSpy.getDashboardStats).toHaveBeenCalled();
      expect(courseServiceSpy.getCourses).toHaveBeenCalledWith({ limit: 5, sort: 'created_at', order: 'desc' });
      expect(enrollmentServiceSpy.getEnrollments).toHaveBeenCalledWith({ limit: 5, sort: 'enrolled_at', order: 'desc' });
      expect(reportServiceSpy.getCompletionTrends).toHaveBeenCalledWith({ days: 30 });
    });
  });

  describe('loadDashboardData', () => {
    it('should load stats and set loading to false', () => {
      component.loadDashboardData();

      expect(component.stats).toEqual(mockStats);
      expect(component.isLoading).toBe(false);
    });

    it('should load recent courses', () => {
      component.loadDashboardData();

      expect(component.recentCourses).toEqual(mockCourses);
    });

    it('should load recent enrollments', () => {
      component.loadDashboardData();

      expect(component.recentEnrollments).toEqual(mockEnrollments);
    });

    it('should handle stats loading error', () => {
      reportServiceSpy.getDashboardStats.and.returnValue(throwError(() => new Error('Stats error')));
      spyOn(console, 'error');

      component.loadDashboardData();

      expect(console.error).toHaveBeenCalledWith('Error loading dashboard stats:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });

    it('should handle courses loading error', () => {
      courseServiceSpy.getCourses.and.returnValue(throwError(() => new Error('Courses error')));
      spyOn(console, 'error');

      component.loadDashboardData();

      expect(console.error).toHaveBeenCalledWith('Error loading recent courses:', jasmine.any(Error));
    });

    it('should handle enrollments loading error', () => {
      enrollmentServiceSpy.getEnrollments.and.returnValue(throwError(() => new Error('Enrollments error')));
      spyOn(console, 'error');

      component.loadDashboardData();

      expect(console.error).toHaveBeenCalledWith('Error loading recent enrollments:', jasmine.any(Error));
    });
  });

  describe('updateCompletionChart', () => {
    it('should update chart data with stats', () => {
      component['updateCompletionChart'](mockStats);

      expect(component.completionChartData.datasets[0].data).toEqual([25, 25, jasmine.any(Number)]);
    });
  });

  describe('loadCompletionTrends', () => {
    it('should update trends chart data', () => {
      component['loadCompletionTrends']();

      const expectedLabels = mockCompletionTrends.map(t => new Date(t.date).toLocaleDateString());
      const expectedData = mockCompletionTrends.map(t => t.enrollments);

      expect(component.enrollmentTrendsData.labels).toEqual(expectedLabels);
      expect(component.enrollmentTrendsData.datasets[0].data).toEqual(expectedData);
    });

    it('should handle completion trends error', () => {
      reportServiceSpy.getCompletionTrends.and.returnValue(throwError(() => new Error('Trends error')));
      spyOn(console, 'error');

      component['loadCompletionTrends']();

      expect(console.error).toHaveBeenCalledWith('Error loading completion trends:', jasmine.any(Error));
    });
  });

  describe('getCompletionRate', () => {
    it('should return completion rate from stats', () => {
      component.stats = mockStats;
      expect(component.getCompletionRate()).toBe(50);
    });

    it('should return 0 when no stats', () => {
      component.stats = null;
      expect(component.getCompletionRate()).toBe(0);
    });
  });

  describe('getCompletionRateColor', () => {
    it('should return green for high completion rates', () => {
      component.stats = { ...mockStats, completion_rate: 85 };
      expect(component.getCompletionRateColor()).toBe('#4CAF50');
    });

    it('should return orange for medium completion rates', () => {
      component.stats = { ...mockStats, completion_rate: 65 };
      expect(component.getCompletionRateColor()).toBe('#FF9800');
    });

    it('should return red for low completion rates', () => {
      component.stats = { ...mockStats, completion_rate: 45 };
      expect(component.getCompletionRateColor()).toBe('#F44336');
    });
  });

  describe('refreshDashboard', () => {
    it('should reload dashboard data', () => {
      spyOn(component, 'loadDashboardData');
      
      component.refreshDashboard();

      expect(component.loadDashboardData).toHaveBeenCalled();
    });
  });

  describe('template rendering', () => {
    beforeEach(() => {
      component.stats = mockStats;
      component.recentCourses = mockCourses;
      component.recentEnrollments = mockEnrollments;
      component.isLoading = false;
      fixture.detectChanges();
    });

    it('should display stats cards', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.stats-grid')).toBeTruthy();
    });

    it('should display recent courses', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.recent-courses')).toBeTruthy();
    });

    it('should display recent enrollments', () => {
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.recent-enrollments')).toBeTruthy();
    });

    it('should show loading spinner when loading', () => {
      component.isLoading = true;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-spinner')).toBeTruthy();
    });
  });
});
