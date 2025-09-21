import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { EnrollmentService } from './enrollment.service';
import { Enrollment, EnrollmentCreate, EnrollmentUpdate } from '../models';
import { environment } from '../../environments/environment';

describe('EnrollmentService', () => {
  let service: EnrollmentService;
  let httpMock: HttpTestingController;

  const mockEnrollment: Enrollment = {
    id: 1,
    person_id: 1,
    course_id: 1,
    enrolled_at: '2023-01-01T00:00:00Z',
    status: 'enrolled' as any,
    progress_percentage: 50,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [EnrollmentService]
    });

    service = TestBed.inject(EnrollmentService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getEnrollments', () => {
    it('should fetch enrollments', () => {
      const mockEnrollments = [mockEnrollment];

      service.getEnrollments().subscribe(enrollments => {
        expect(enrollments).toEqual(mockEnrollments);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEnrollments);
    });

    it('should fetch enrollments with parameters', () => {
      const params = { status: 'completed', limit: 10 };
      
      service.getEnrollments(params).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/enrollments` &&
        request.params.get('status') === 'completed' &&
        request.params.get('limit') === '10'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockEnrollment]);
    });
  });

  describe('getEnrollment', () => {
    it('should fetch a single enrollment', () => {
      service.getEnrollment(1).subscribe(enrollment => {
        expect(enrollment).toEqual(mockEnrollment);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEnrollment);
    });
  });

  describe('createEnrollment', () => {
    it('should create an enrollment', () => {
      const enrollmentCreate: EnrollmentCreate = {
        person_id: 1,
        course_id: 1
      };

      service.createEnrollment(enrollmentCreate).subscribe(enrollment => {
        expect(enrollment).toEqual(mockEnrollment);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(enrollmentCreate);
      req.flush(mockEnrollment);
    });
  });

  describe('updateEnrollment', () => {
    it('should update an enrollment', () => {
      const enrollmentUpdate: EnrollmentUpdate = {
        status: 'completed' as any
      };

      service.updateEnrollment(1, enrollmentUpdate).subscribe(enrollment => {
        expect(enrollment).toEqual(mockEnrollment);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(enrollmentUpdate);
      req.flush(mockEnrollment);
    });
  });

  describe('deleteEnrollment', () => {
    it('should delete an enrollment', () => {
      service.deleteEnrollment(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('getEnrollmentsByPerson', () => {
    it('should fetch enrollments by person', () => {
      const mockEnrollments = [mockEnrollment];

      service.getEnrollmentsByPerson(1).subscribe(enrollments => {
        expect(enrollments).toEqual(mockEnrollments);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/person/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEnrollments);
    });
  });

  describe('getEnrollmentsByCourse', () => {
    it('should fetch enrollments by course', () => {
      const mockEnrollments = [mockEnrollment];

      service.getEnrollmentsByCourse(1).subscribe(enrollments => {
        expect(enrollments).toEqual(mockEnrollments);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/course/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEnrollments);
    });
  });

  describe('bulkEnroll', () => {
    it('should create multiple enrollments', () => {
      const enrollments: EnrollmentCreate[] = [
        { person_id: 1, course_id: 1 },
        { person_id: 2, course_id: 1 }
      ];
      const mockResponse = [mockEnrollment];

      service.bulkEnroll(enrollments).subscribe(result => {
        expect(result).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/enrollments/bulk`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(enrollments);
      req.flush(mockResponse);
    });
  });
});
