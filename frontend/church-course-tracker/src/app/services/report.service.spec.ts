import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ReportService } from './report.service';
import { DashboardStats, ProgressReport, ReportFilters } from '../models';
import { environment } from '../../environments/environment';

describe('ReportService', () => {
  let service: ReportService;
  let httpMock: HttpTestingController;

  const mockDashboardStats: DashboardStats = {
    total_courses: 10,
    active_courses: 8,
    total_enrollments: 50,
    completed_enrollments: 25,
    total_members: 30,
    completion_rate: 50
  };

  const mockProgressReport: ProgressReport = {
    course_stats: [{
      course_id: 1,
      course_title: 'Test Course',
      total_enrollments: 10,
      completed_enrollments: 5,
      in_progress_enrollments: 3,
      completion_rate: 50,
      average_progress: 60
    }],
    member_progress: [{
      person_id: 1,
      person_name: 'John Doe',
      total_enrollments: 2,
      completed_enrollments: 1,
      in_progress_enrollments: 1,
      overall_progress: 75
    }],
    completion_trends: [{
      date: '2023-01-01',
      completions: 5,
      enrollments: 10
    }]
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ReportService]
    });

    service = TestBed.inject(ReportService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getDashboardStats', () => {
    it('should fetch dashboard stats', () => {
      service.getDashboardStats().subscribe(stats => {
        expect(stats).toEqual(mockDashboardStats);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/reports/dashboard`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDashboardStats);
    });
  });

  describe('getProgressReport', () => {
    it('should fetch progress report', () => {
      service.getProgressReport().subscribe(report => {
        expect(report).toEqual(mockProgressReport);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/reports/progress`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgressReport);
    });

    it('should fetch progress report with filters', () => {
      const filters: ReportFilters = {
        start_date: '2023-01-01',
        end_date: '2023-01-31',
        course_ids: [1, 2],
        status: 'completed'
      };

      service.getProgressReport(filters).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/reports/progress` &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-01-31' &&
        request.params.get('status') === 'completed' &&
        request.params.getAll('course_ids').length === 2
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockProgressReport);
    });
  });

  describe('getCompletionTrends', () => {
    it('should fetch completion trends', () => {
      const mockTrends = [{ date: '2023-01-01', completions: 5, enrollments: 10 }];

      service.getCompletionTrends().subscribe(trends => {
        expect(trends).toEqual(mockTrends);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/reports/completion-trends`);
      expect(req.request.method).toBe('GET');
      req.flush(mockTrends);
    });

    it('should fetch completion trends with filters', () => {
      const filters: ReportFilters = {
        start_date: '2023-01-01',
        end_date: '2023-01-31'
      };

      service.getCompletionTrends(filters).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/reports/completion-trends` &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-01-31'
      );
      expect(req.request.method).toBe('GET');
      req.flush([]);
    });
  });

  describe('exportReport', () => {
    it('should export report as blob', () => {
      const mockBlob = new Blob(['test data'], { type: 'application/pdf' });

      service.exportReport('pdf').subscribe(blob => {
        expect(blob).toEqual(mockBlob);
      });

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/reports/export` &&
        request.params.get('type') === 'pdf'
      );
      expect(req.request.method).toBe('GET');
      expect(req.request.responseType).toBe('blob');
      req.flush(mockBlob);
    });

    it('should export report with filters', () => {
      const filters: ReportFilters = {
        start_date: '2023-01-01',
        course_ids: [1]
      };
      const mockBlob = new Blob(['test data'], { type: 'application/xlsx' });

      service.exportReport('xlsx', filters).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/reports/export` &&
        request.params.get('type') === 'xlsx' &&
        request.params.get('start_date') === '2023-01-01'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockBlob);
    });
  });
});
