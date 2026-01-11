import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuditService } from './audit.service';
import { environment } from '../../environments/environment';
import { AuditLog, AuditSummary, AuditLogFilters } from '../models';

describe('AuditService', () => {
  let service: AuditService;
  let httpMock: HttpTestingController;

  const mockAuditLog: AuditLog = {
    id: 1,
    table_name: 'courses',
    record_id: 1,
    action: 'update',
    changed_by: 1,
    changed_at: '2023-01-01T00:00:00Z',
    old_values: {},
    new_values: {}
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuditService]
    });

    service = TestBed.inject(AuditService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getAuditLogs', () => {
    it('should fetch audit logs without filters', () => {
      service.getAuditLogs().subscribe(logs => {
        expect(logs).toEqual([mockAuditLog]);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/audit`);
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });

    it('should fetch audit logs with filters', () => {
      const filters: AuditLogFilters = {
        table_name: 'courses',
        action: 'update',
        changed_by: 1,
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        skip: 0,
        limit: 100
      };

      service.getAuditLogs(filters).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit` &&
        request.params.get('table_name') === 'courses' &&
        request.params.get('action') === 'update' &&
        request.params.get('changed_by') === '1' &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-12-31' &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });
  });

  describe('getAuditSummary', () => {
    it('should fetch audit summary without dates', () => {
      const mockSummary: AuditSummary = {
        total_logs: 100,
        tables_affected: 2,
        actions_performed: 3,
        action_breakdown: { insert: 50, update: 30, delete: 20 },
        table_breakdown: { courses: 40, programs: 60 }
      };

      service.getAuditSummary().subscribe(summary => {
        expect(summary).toEqual(mockSummary);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/audit/summary`);
      expect(req.request.method).toBe('GET');
      req.flush(mockSummary);
    });

    it('should fetch audit summary with dates', () => {
      const mockSummary: AuditSummary = {
        total_logs: 50,
        tables_affected: 2,
        actions_performed: 3,
        action_breakdown: { insert: 25, update: 15, delete: 10 },
        table_breakdown: { courses: 20, programs: 30 }
      };

      service.getAuditSummary('2023-01-01', '2023-12-31').subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/summary` &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-12-31'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockSummary);
    });
  });

  describe('getTableAuditLogs', () => {
    it('should fetch table audit logs', () => {
      service.getTableAuditLogs('courses').subscribe(logs => {
        expect(logs).toEqual([mockAuditLog]);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/table/courses` &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });

    it('should fetch table audit logs with record ID', () => {
      service.getTableAuditLogs('courses', 1, 0, 50).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/table/courses` &&
        request.params.get('record_id') === '1' &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '50'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });
  });

  describe('getUserAuditLogs', () => {
    it('should fetch user audit logs', () => {
      service.getUserAuditLogs(1).subscribe(logs => {
        expect(logs).toEqual([mockAuditLog]);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/user/1` &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });

    it('should fetch user audit logs with pagination', () => {
      service.getUserAuditLogs(1, 10, 20).subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/user/1` &&
        request.params.get('skip') === '10' &&
        request.params.get('limit') === '20'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });
  });

  describe('exportAuditLogs', () => {
    it('should export audit logs as CSV', () => {
      const options = {
        format: 'csv' as any,
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        table_name: 'courses'
      };
      const mockBlob = new Blob(['test'], { type: 'text/csv' });

      service.exportAuditLogs(options).subscribe(blob => {
        expect(blob).toEqual(mockBlob);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/export` &&
        request.params.get('format') === 'csv' &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-12-31' &&
        request.params.get('table_name') === 'courses'
      );
      expect(req.request.method).toBe('GET');
      expect(req.request.responseType).toBe('blob');
      req.flush(mockBlob);
    });
  });

  describe('getStaffActivityLogs', () => {
    it('should fetch staff activity logs', () => {
      service.getStaffActivityLogs().subscribe(logs => {
        expect(logs).toEqual([mockAuditLog]);
      });

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/activity` &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '100'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });

    it('should fetch staff activity logs with dates', () => {
      service.getStaffActivityLogs(0, 50, '2023-01-01', '2023-12-31').subscribe();

      const req = httpMock.expectOne(request =>
        request.url === `${environment.apiUrl}/audit/activity` &&
        request.params.get('skip') === '0' &&
        request.params.get('limit') === '50' &&
        request.params.get('start_date') === '2023-01-01' &&
        request.params.get('end_date') === '2023-12-31'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockAuditLog]);
    });
  });
});
