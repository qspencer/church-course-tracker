import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CourseContentService } from './course-content.service';
import { environment } from '../../environments/environment';
import {
  CourseModule,
  CourseContent,
  CourseModuleCreate,
  CourseContentCreate,
  ContentAccessLog,
  ContentUploadResponse,
  CourseContentType,
  StorageType,
  ContentProgress,
  CourseContentSummary
} from '../models';

describe('CourseContentService', () => {
  let service: CourseContentService;
  let httpMock: HttpTestingController;

  const mockModule: CourseModule = {
    id: 1,
    course_id: 1,
    title: 'Test Module',
    description: 'Test Description',
    order_index: 1,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockContent: CourseContent = {
    id: 1,
    course_id: 1,
    module_id: 1,
    title: 'Test Content',
    description: 'Test Content Description',
    content_type: 'document' as any,
    storage_type: 'database' as any,
    file_name: 'test.pdf',
    order_index: 1,
    is_active: true,
    download_count: 0,
    view_count: 0,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CourseContentService]
    });

    service = TestBed.inject(CourseContentService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Module methods', () => {
    it('should create a module', () => {
      const moduleCreate: CourseModuleCreate = {
        course_id: 1,
        title: 'New Module',
        description: 'New Description',
        order_index: 1
      };

      service.createModule(moduleCreate).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/modules/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(moduleCreate);
      req.flush(mockModule);
    });

    it('should fetch course modules', () => {
      service.getCourseModules(1).subscribe(modules => {
        expect(modules).toEqual([mockModule]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/modules/1`);
      expect(req.request.method).toBe('GET');
      req.flush([mockModule]);
    });

    it('should fetch a single module', () => {
      service.getModule(1).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/modules/single/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockModule);
    });

    it('should update a module', () => {
      const moduleUpdate = { title: 'Updated Module' };

      service.updateModule(1, moduleUpdate).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/modules/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(moduleUpdate);
      req.flush(mockModule);
    });

    it('should delete a module', () => {
      service.deleteModule(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/content/modules/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Content methods', () => {
    it('should create content', () => {
      const contentCreate: CourseContentCreate = {
        course_id: 1,
        module_id: 1,
        title: 'New Content',
        description: 'New Description',
        content_type: CourseContentType.DOCUMENT,
        storage_type: StorageType.DATABASE,
        order_index: 1,
        is_active: true
      };

      service.createContent(contentCreate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(contentCreate);
      req.flush(mockContent);
    });

    it('should fetch course content', () => {
      service.getCourseContent(1).subscribe(contents => {
        expect(contents).toEqual([mockContent]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/course/1`);
      expect(req.request.method).toBe('GET');
      req.flush([mockContent]);
    });

    it('should fetch course content with module filter', () => {
      service.getCourseContent(1, 1).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/content/course/1` &&
        request.params.get('module_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockContent]);
    });

    it('should fetch a single content item', () => {
      service.getContentItem(1).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockContent);
    });

    it('should update content', () => {
      const contentUpdate = { title: 'Updated Content' };

      service.updateContent(1, contentUpdate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(contentUpdate);
      req.flush(mockContent);
    });

    it('should delete content', () => {
      service.deleteContent(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('File operations', () => {
    it('should upload a file', () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      const mockResponse: ContentUploadResponse = {
        file_name: 'test.pdf',
        file_size: 1024,
        file_path: 'http://example.com/files/test.pdf',
        mime_type: 'application/pdf',
        message: 'File uploaded successfully'
      };

      service.uploadFile(1, file).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/upload`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body instanceof FormData).toBe(true);
      req.flush(mockResponse);
    });

    it('should download content', () => {
      const mockBlob = new Blob(['test'], { type: 'application/pdf' });

      service.downloadContent(1).subscribe(blob => {
        expect(blob).toEqual(mockBlob);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/download`);
      expect(req.request.method).toBe('GET');
      expect(req.request.responseType).toBe('blob');
      req.flush(mockBlob);
    });
  });

  describe('Access and progress tracking', () => {
    it('should log content access', () => {
      const accessData = {
        content_id: 1,
        user_id: 1,
        access_type: 'view' as any
      };
      const mockAccessLog: ContentAccessLog = {
        id: 1,
        content_id: 1,
        user_id: 1,
        access_type: 'view',
        access_timestamp: '2023-01-01T00:00:00Z'
      };

      service.logContentAccess(accessData).subscribe(log => {
        expect(log).toEqual(mockAccessLog);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/access`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(accessData);
      req.flush(mockAccessLog);
    });

    it('should update content progress', () => {
      const progressData = {
        content_id: 1,
        progress_percentage: 50,
        time_spent: 300
      };

      const mockAccessLog: ContentAccessLog = {
        id: 1,
        content_id: 1,
        user_id: 1,
        access_type: 'view',
        access_timestamp: '2023-01-01T00:00:00Z'
      };

      service.updateContentProgress(progressData).subscribe(log => {
        expect(log).toEqual(mockAccessLog);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/progress`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(progressData);
      req.flush(mockAccessLog);
    });

    it('should fetch content access logs', () => {
      const mockLogs: ContentAccessLog[] = [{
        id: 1,
        content_id: 1,
        user_id: 1,
        access_type: 'view',
        access_timestamp: '2023-01-01T00:00:00Z'
      }];

      service.getContentAccessLogs(1).subscribe(logs => {
        expect(logs).toEqual(mockLogs);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/content/1/access-logs` &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockLogs);
    });

    it('should fetch user content progress', () => {
      const mockProgress = {
        1: {
          content_id: 1,
          content_title: 'Test Content',
          progress_percentage: 50,
          time_spent: 300,
          last_accessed: '2023-01-01T00:00:00Z'
        }
      };

      service.getUserContentProgress(1, 1).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/user/1/course/1/progress`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgress);
    });
  });

  describe('Summary and audit', () => {
    it('should fetch course content summary', () => {
      const mockSummary = {
        course_id: 1,
        total_modules: 5,
        total_content_items: 20,
        total_file_size: 1024000,
        content_by_type: { document: 10, video: 5, audio: 5 },
        recent_uploads: []
      };

      service.getCourseContentSummary(1).subscribe(summary => {
        expect(summary).toEqual(mockSummary);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/content/course/1/summary`);
      expect(req.request.method).toBe('GET');
      req.flush(mockSummary);
    });

    it('should fetch content audit logs', () => {
      const mockAuditLogs: any[] = [{
        id: 1,
        content_id: 1,
        action: 'update',
        changed_by: 1,
        changed_at: '2023-01-01T00:00:00Z'
      }];

      service.getContentAuditLogs(1).subscribe(logs => {
        expect(logs).toEqual(mockAuditLogs);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/content/1/audit-logs` &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockAuditLogs);
    });
  });

  describe('Helper methods', () => {
    it('should log content view', () => {
      service.logContentView(1);

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/access`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body.access_type).toBe('view');
      req.flush({});
    });

    it('should log content download', () => {
      service.logContentDownload(1);

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/access`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body.access_type).toBe('download');
      req.flush({});
    });

    it('should update progress', () => {
      service.updateProgress(1, 75, 600);

      const req = httpMock.expectOne(`${environment.apiUrl}/content/1/progress`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body.progress_percentage).toBe(75);
      expect(req.request.body.time_spent).toBe(600);
      req.flush({});
    });
  });
});
