import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ProgramContentService } from './program-content.service';
import { environment } from '../../environments/environment';
import {
  ProgramModule,
  ProgramContent,
  ProgramModuleCreate,
  ProgramContentCreate
} from '../models/program-content.model';

describe('ProgramContentService', () => {
  let service: ProgramContentService;
  let httpMock: HttpTestingController;

  const mockModule: ProgramModule = {
    id: 1,
    program_id: 1,
    title: 'Test Module',
    description: 'Test Description',
    order_index: 1,
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockContent: ProgramContent = {
    id: 1,
    program_id: 1,
    module_id: 1,
    title: 'Test Content',
    description: 'Test Content Description',
    content_type: 'document' as any,
    external_url: 'http://example.com/content',
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
      providers: [ProgramContentService]
    });

    service = TestBed.inject(ProgramContentService);
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
      const moduleCreate: ProgramModuleCreate = {
        program_id: 1,
        title: 'New Module',
        description: 'New Description',
        order_index: 1
      };

      service.createModule(moduleCreate).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/modules/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(moduleCreate);
      req.flush(mockModule);
    });

    it('should fetch program modules', () => {
      service.getProgramModules(1).subscribe(modules => {
        expect(modules).toEqual([mockModule]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/modules/1`);
      expect(req.request.method).toBe('GET');
      req.flush([mockModule]);
    });

    it('should fetch a single module', () => {
      service.getModule(1).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/modules/single/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockModule);
    });

    it('should update a module', () => {
      const moduleUpdate = { title: 'Updated Module' };

      service.updateModule(1, moduleUpdate).subscribe(module => {
        expect(module).toEqual(mockModule);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/modules/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(moduleUpdate);
      req.flush(mockModule);
    });

    it('should delete a module', () => {
      service.deleteModule(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/modules/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('Content methods', () => {
    it('should create content', () => {
      const contentCreate: ProgramContentCreate = {
        program_id: 1,
        module_id: 1,
        title: 'New Content',
        description: 'New Description',
        content_type: 'document' as any,
        order_index: 1,
        is_active: true
      };

      service.createContent(contentCreate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(contentCreate);
      req.flush(mockContent);
    });

    it('should fetch program content', () => {
      service.getProgramContent(1).subscribe(contents => {
        expect(contents).toEqual([mockContent]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/program/1`);
      expect(req.request.method).toBe('GET');
      req.flush([mockContent]);
    });

    it('should fetch program content with module filter', () => {
      service.getProgramContent(1, 1).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/program-content/program/1` &&
        request.params.get('module_id') === '1'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockContent]);
    });

    it('should fetch a single content item', () => {
      service.getContentItem(1).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockContent);
    });

    it('should update content', () => {
      const contentUpdate = { title: 'Updated Content' };

      service.updateContent(1, contentUpdate).subscribe(content => {
        expect(content).toEqual(mockContent);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(contentUpdate);
      req.flush(mockContent);
    });

    it('should delete content', () => {
      service.deleteContent(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/program-content/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });
});
