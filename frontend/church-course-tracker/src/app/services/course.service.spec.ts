import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CourseService } from './course.service';
import { Course, CourseCreate, CourseUpdate, Content, ContentCreate } from '../models';
import { environment } from '../../environments/environment';

describe('CourseService', () => {
  let service: CourseService;
  let httpMock: HttpTestingController;

  const mockCourse: Course = {
    id: 1,
    title: 'Test Course',
    description: 'Test Description',
    duration_weeks: 4,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockContent: Content = {
    id: 1,
    course_id: 1,
    title: 'Test Content',
    description: 'Test Content Description',
    content_type_id: 1,
    content_url: 'http://example.com/content',
    sort_order: 1,
    is_required: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CourseService]
    });

    service = TestBed.inject(CourseService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getCourses', () => {
    it('should fetch courses', () => {
      const mockCourses = [mockCourse];

      service.getCourses().subscribe(courses => {
        expect(courses).toEqual(mockCourses);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCourses);
    });

    it('should fetch courses with parameters', () => {
      const params = { is_active: true, limit: 10 };
      
      service.getCourses(params).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/courses` &&
        request.params.get('is_active') === 'true' &&
        request.params.get('limit') === '10'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockCourse]);
    });
  });

  describe('getCourse', () => {
    it('should fetch a single course', () => {
      service.getCourse(1).subscribe(course => {
        expect(course).toEqual(mockCourse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockCourse);
    });
  });

  describe('createCourse', () => {
    it('should create a course', () => {
      const courseCreate: CourseCreate = {
        title: 'New Course',
        description: 'New Description',
        duration_weeks: 6
      };

      service.createCourse(courseCreate).subscribe(course => {
        expect(course).toEqual(mockCourse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(courseCreate);
      req.flush(mockCourse);
    });
  });

  describe('updateCourse', () => {
    it('should update a course', () => {
      const courseUpdate: CourseUpdate = {
        title: 'Updated Course',
        is_active: false
      };

      service.updateCourse(1, courseUpdate).subscribe(course => {
        expect(course).toEqual(mockCourse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(courseUpdate);
      req.flush(mockCourse);
    });
  });

  describe('deleteCourse', () => {
    it('should delete a course', () => {
      service.deleteCourse(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('getCourseContent', () => {
    it('should fetch course content', () => {
      const mockContents = [mockContent];

      service.getCourseContent(1).subscribe(contents => {
        expect(contents).toEqual(mockContents);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1/content`);
      expect(req.request.method).toBe('GET');
      req.flush(mockContents);
    });
  });

  describe('addCourseContent', () => {
    it('should add course content', () => {
      const contentCreate: ContentCreate = {
        course_id: 1,
        title: 'New Content',
        description: 'New Content Description',
        content_type_id: 1,
        sort_order: 2,
        is_required: false
      };

      service.addCourseContent(contentCreate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1/content`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(contentCreate);
      req.flush(mockContent);
    });
  });

  describe('updateCourseContent', () => {
    it('should update course content', () => {
      const contentUpdate = { title: 'Updated Content' };

      service.updateCourseContent(1, 1, contentUpdate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1/content/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(contentUpdate);
      req.flush(mockContent);
    });
  });

  describe('deleteCourseContent', () => {
    it('should delete course content', () => {
      service.deleteCourseContent(1, 1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1/content/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('getCourseStats', () => {
    it('should fetch course stats', () => {
      const mockStats = { enrollments: 10, completions: 5 };

      service.getCourseStats(1).subscribe(stats => {
        expect(stats).toEqual(mockStats);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/courses/1/stats`);
      expect(req.request.method).toBe('GET');
      req.flush(mockStats);
    });
  });
});
