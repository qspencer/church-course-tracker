import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ProgressService } from './progress.service';
import { Progress, ProgressStatus } from '../models';
import { environment } from '../../environments/environment';

describe('ProgressService', () => {
  let service: ProgressService;
  let httpMock: HttpTestingController;

  const mockProgress: Progress = {
    id: 1,
    enrollment_id: 1,
    content_id: 1,
    completed_at: '2023-01-01T00:00:00Z',
    status: ProgressStatus.COMPLETED,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ProgressService]
    });

    service = TestBed.inject(ProgressService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getProgress', () => {
    it('should fetch progress items', () => {
      const mockProgressItems = [mockProgress];

      service.getProgress().subscribe(items => {
        expect(items).toEqual(mockProgressItems);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgressItems);
    });

    it('should fetch progress with parameters', () => {
      const params = { enrollment_id: 1 };
      
      service.getProgress(params).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/progress` &&
        request.params.get('enrollment_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockProgress]);
    });
  });

  describe('getProgressByEnrollment', () => {
    it('should fetch progress by enrollment', () => {
      const mockProgressItems = [mockProgress];

      service.getProgressByEnrollment(1).subscribe(items => {
        expect(items).toEqual(mockProgressItems);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress/enrollment/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgressItems);
    });
  });

  describe('updateProgress', () => {
    it('should update progress status', () => {
      service.updateProgress(1, ProgressStatus.COMPLETED).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual({ status: ProgressStatus.COMPLETED });
      req.flush(mockProgress);
    });
  });

  describe('markContentComplete', () => {
    it('should mark content as complete', () => {
      service.markContentComplete(1, 1).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress/complete`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({
        enrollment_id: 1,
        content_id: 1
      });
      req.flush(mockProgress);
    });
  });

  describe('getPersonProgress', () => {
    it('should fetch person progress', () => {
      const mockPersonProgress = { overall_progress: 75, completed_items: 5 };

      service.getPersonProgress(1).subscribe(progress => {
        expect(progress).toEqual(mockPersonProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress/person/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockPersonProgress);
    });
  });

  describe('getCourseProgress', () => {
    it('should fetch course progress', () => {
      const mockCourseProgress = { average_progress: 65, total_enrollments: 20 };

      service.getCourseProgress(1).subscribe(progress => {
        expect(progress).toEqual(mockCourseProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/progress/course/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCourseProgress);
    });
  });
});
