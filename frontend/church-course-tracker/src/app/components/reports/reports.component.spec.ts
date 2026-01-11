import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Router } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBarModule } from '@angular/material/snack-bar';

// Chart.js
import { NgChartsModule } from 'ng2-charts';

import { ReportsComponent } from './reports.component';
import { ReportService } from '../../services/report.service';
import { CourseService } from '../../services/course.service';
import { DashboardStats, ProgressReport, Course } from '../../models';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';

describe('ReportsComponent', () => {
  let component: ReportsComponent;
  let fixture: ComponentFixture<ReportsComponent>;
  let reportServiceSpy: jasmine.SpyObj<ReportService>;
  let courseServiceSpy: jasmine.SpyObj<CourseService>;
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
    }
  ];

  const mockProgressReport: ProgressReport = {
    course_stats: [],
    member_progress: [],
    completion_trends: []
  };

  beforeEach(async () => {
    const reportSpy = jasmine.createSpyObj('ReportService', ['getDashboardStats', 'getProgressReport', 'exportReport']);
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    const router = jasmine.createSpyObj('Router', ['navigate']);
    
    reportSpy.getDashboardStats.and.returnValue(of(mockStats));
    reportSpy.getProgressReport.and.returnValue(of(mockProgressReport));
    courseSpy.getCourses.and.returnValue(of(mockCourses));
    router.navigate.and.returnValue(Promise.resolve(true));

    await TestBed.configureTestingModule({
      declarations: [ReportsComponent],
      imports: [
        BrowserAnimationsModule,
        ReactiveFormsModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatSnackBarModule,
        NgChartsModule
      ],
      providers: [
        { provide: ReportService, useValue: reportSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: Router, useValue: router },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ReportsComponent);
    component = fixture.componentInstance;
    reportServiceSpy = TestBed.inject(ReportService) as jasmine.SpyObj<ReportService>;
    courseServiceSpy = TestBed.inject(CourseService) as jasmine.SpyObj<CourseService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('navigation methods', () => {
    it('should navigate to courses page', () => {
      component.navigateToCourses();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/churchcoursetracker/courses']);
    });

    it('should navigate to enrollments page', () => {
      component.navigateToEnrollments();
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/churchcoursetracker/enrollments']);
    });
  });
});
