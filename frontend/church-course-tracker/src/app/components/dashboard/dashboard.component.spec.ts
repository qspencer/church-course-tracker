import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Router, ActivatedRoute } from '@angular/router';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

// Chart.js
import { NgChartsModule } from 'ng2-charts';

import { DashboardComponent } from './dashboard.component';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { ProgramService } from '../../services/program.service';
import { DashboardStats, Course, Enrollment, Program, ProgramStats } from '../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let reportServiceSpy: jasmine.SpyObj<ReportService>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
  let enrollmentServiceSpy: jasmine.SpyObj<EnrollmentService>;
  let programServiceSpy: jasmine.SpyObj<ProgramService>;
  let routerSpy: jasmine.SpyObj<Router>;

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

  const mockCompletionTrends = {
    trends: [
      { date: '2023-01-01', enrollments: 5, completions: 2 },
      { date: '2023-01-02', enrollments: 8, completions: 4 },
      { date: '2023-01-03', enrollments: 6, completions: 3 }
    ],
    period: {
      start_date: '2023-01-01',
      end_date: '2023-01-03'
    },
    course_ids: []
  };

  beforeEach(async () => {
    const reportSpy = jasmine.createSpyObj('ReportService', ['getDashboardStats', 'getCompletionTrends']);
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['getEnrollments']);
    const programSpy = jasmine.createSpyObj('ProgramService', ['getPrograms', 'getProgramParticipants', 'getProgramPairings', 'getProgramSessions']);
    const router = jasmine.createSpyObj('Router', ['navigate']);
    programSpy.getPrograms.and.returnValue(of([]));
    programSpy.getProgramParticipants.and.returnValue(of([]));
    programSpy.getProgramPairings.and.returnValue(of([]));
    programSpy.getProgramSessions.and.returnValue(of([]));
    router.navigate.and.returnValue(Promise.resolve(true));

    await TestBed.configureTestingModule({
    imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatButtonModule,
        MatButtonToggleModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatProgressBarModule,
        MatChipsModule,
        MatSlideToggleModule,
        NgChartsModule,
        DashboardComponent
    ],
    providers: [
        { provide: ReportService, useValue: reportSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: ProgramService, useValue: programSpy },
        { provide: Router, useValue: router },
        { provide: ActivatedRoute, useValue: {} },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
}).compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    reportServiceSpy = TestBed.inject(ReportService) as jasmine.SpyObj<ReportService>;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    enrollmentServiceSpy = TestBed.inject(EnrollmentService) as jasmine.SpyObj<EnrollmentService>;
    programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
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
      expect(courseServiceSpy.getCourses).toHaveBeenCalledWith(jasmine.objectContaining({ limit: 5, sort: 'created_at', order: 'desc' }));
      expect(enrollmentServiceSpy.getEnrollments).toHaveBeenCalledWith({ limit: 5 });
      expect(reportServiceSpy.getCompletionTrends).toHaveBeenCalledWith(jasmine.any(Object));
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

      expect(console.error).toHaveBeenCalledWith('[ERROR] Error loading dashboard stats', jasmine.any(Error), '');
      expect(component.isLoading).toBe(false);
    });

    it('should handle courses loading error', () => {
      courseServiceSpy.getCourses.and.returnValue(throwError(() => new Error('Courses error')));
      spyOn(console, 'error');

      component.loadDashboardData();

      expect(console.error).toHaveBeenCalledWith('[ERROR] Error loading recent courses', jasmine.any(Error), '');
    });

    it('should handle enrollments loading error', () => {
      enrollmentServiceSpy.getEnrollments.and.returnValue(throwError(() => new Error('Enrollments error')));
      spyOn(console, 'error');

      component.loadDashboardData();

      expect(console.error).toHaveBeenCalledWith('[ERROR] Error loading recent enrollments', jasmine.any(Error), '');
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

      const expectedLabels = mockCompletionTrends.trends.map(t => new Date(t.date).toLocaleDateString());
      const expectedData = mockCompletionTrends.trends.map(t => t.enrollments);

      expect(component.enrollmentTrendsData.labels).toEqual(expectedLabels);
      expect(component.enrollmentTrendsData.datasets[0].data).toEqual(expectedData);
    });

    it('should handle completion trends error', () => {
      reportServiceSpy.getCompletionTrends.and.returnValue(throwError(() => new Error('Trends error')));
      spyOn(console, 'error');

      component['loadCompletionTrends']();

      expect(console.error).toHaveBeenCalledWith('[ERROR] Error loading completion trends', jasmine.any(Error), '');
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

  describe('navigation methods', () => {
    it('should navigate to courses page', () => {
      component.navigateToCourses();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/courses']);
    });

    it('should navigate to enrollments page', () => {
      component.navigateToEnrollments();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/enrollments']);
    });

    it('should navigate to members page', () => {
      component.navigateToMembers();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/members']);
    });

    it('should navigate to programs page', () => {
      component.navigateToPrograms();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/programs']);
    });
  });

  describe('onViewModeChange', () => {
    it('should change view mode and reload data', () => {
      spyOn(component, 'loadDashboardData');
      
      component.onViewModeChange('programs');
      
      expect(component.viewMode).toBe('programs');
      expect(component.loadDashboardData).toHaveBeenCalled();
    });
  });

  describe('loadProgramsData', () => {
    it('should load programs data', () => {
      const mockPrograms = [{
        id: 1,
        title: 'Test Program',
        description: 'Test Description',
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      }];
      
      const programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
      programServiceSpy.getPrograms.and.returnValue(of(mockPrograms));
      programServiceSpy.getProgramParticipants.and.returnValue(of([]));
      programServiceSpy.getProgramPairings.and.returnValue(of([]));
      programServiceSpy.getProgramSessions.and.returnValue(of([]));

      component.viewMode = 'programs';
      component['loadProgramsData']();

      expect(programServiceSpy.getPrograms).toHaveBeenCalled();
    });

    it('should handle programs loading error', () => {
      const programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
      programServiceSpy.getPrograms.and.returnValue(throwError(() => new Error('Programs error')));
      spyOn(console, 'error');

      component.viewMode = 'programs';
      component['loadProgramsData']();

      expect(console.error).toHaveBeenCalledWith('[ERROR] Error loading programs', jasmine.any(Error), '');
    });
  });

  describe('calculateProgramStats', () => {
    it('should calculate program stats from programs array', () => {
      const mockPrograms = [
        { id: 1, is_active: true, created_at: '2023-01-01T00:00:00Z', updated_at: '2023-01-01T00:00:00Z' } as any,
        { id: 2, is_active: false, created_at: '2023-01-02T00:00:00Z', updated_at: '2023-01-02T00:00:00Z' } as any
      ];

      const programServiceSpy = TestBed.inject(ProgramService) as jasmine.SpyObj<ProgramService>;
      programServiceSpy.getProgramParticipants.and.returnValue(of([]));
      programServiceSpy.getProgramPairings.and.returnValue(of([]));
      programServiceSpy.getProgramSessions.and.returnValue(of([]));

      component['calculateProgramStats'](mockPrograms);

      expect(component.programStats).toBeTruthy();
      expect(component.programStats?.total_programs).toBe(2);
      expect(component.programStats?.active_programs).toBe(1);
    });
  });

  describe('updateProgramStats', () => {
    it('should update program stats', () => {
      // Initialize programStats first since the method only updates if it exists
      component.programStats = {
        total_participants: 0,
        active_participants: 0,
        total_pairings: 0,
        active_pairings: 0,
        total_sessions: 0,
        completion_rate: 0,
        total_programs: 0,
        active_programs: 0
      };
      
      component['updateProgramStats'](10, 8, 5, 4, 20, 2);

      expect(component.programStats).toBeTruthy();
      expect(component.programStats?.total_participants).toBe(10);
      expect(component.programStats?.active_participants).toBe(8);
      expect(component.programStats?.total_pairings).toBe(5);
      expect(component.programStats?.active_pairings).toBe(4);
      expect(component.programStats?.total_sessions).toBe(20);
    });
  });

  describe('updateCompletionChart', () => {
    it('should update completion chart with program stats', () => {
      component.programStats = {
        total_participants: 100,
        active_participants: 50,
        total_programs: 10,
        active_programs: 8,
        total_pairings: 20,
        active_pairings: 15,
        total_sessions: 50,
        completion_rate: 50
      };

      component['updateProgramCompletionChart']();

      expect(component.completionChartData.datasets[0].data).toBeDefined();
    });
  });

  describe('getEnrollmentMemberName', () => {
    it('should return member name from enrollment', () => {
      const enrollment: Enrollment = {
        id: 1,
        person_id: 1,
        course_id: 1,
        enrolled_at: '2023-01-01T00:00:00Z',
        status: 'enrolled' as any,
        progress_percentage: 0,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        person: {
          id: 1,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z'
        }
      };

      const name = component.getEnrollmentMemberName(enrollment);
      expect(name).toBe('John Doe');
    });

    it('should return fallback ID when no person name', () => {
      const enrollment: Enrollment = {
        id: 1,
        person_id: 1,
        course_id: 1,
        enrolled_at: '2023-01-01T00:00:00Z',
        status: 'enrolled' as any,
        progress_percentage: 0,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      };

      const name = component.getEnrollmentMemberName(enrollment);
      expect(name).toContain('Member #');
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
