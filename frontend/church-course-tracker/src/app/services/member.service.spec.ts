import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MemberService } from './member.service';
import { Person } from '../models';
import { environment } from '../../environments/environment';

describe('MemberService', () => {
  let service: MemberService;
  let httpMock: HttpTestingController;

  const mockMember: Person = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    planning_center_id: 'pc123',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [MemberService]
    });

    service = TestBed.inject(MemberService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getMembers', () => {
    it('should fetch members', () => {
      const mockMembers = [mockMember];

      service.getMembers().subscribe(members => {
        expect(members).toEqual(mockMembers);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people`);
      expect(req.request.method).toBe('GET');
      req.flush(mockMembers);
    });

    it('should fetch members with parameters', () => {
      const params = { limit: 10, search: 'john' };
      
      service.getMembers(params).subscribe();

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/people` &&
        request.params.get('limit') === '10' &&
        request.params.get('search') === 'john'
      );
      expect(req.request.method).toBe('GET');
      req.flush([mockMember]);
    });
  });

  describe('getMember', () => {
    it('should fetch a single member', () => {
      service.getMember(1).subscribe(member => {
        expect(member).toEqual(mockMember);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockMember);
    });
  });

  describe('createMember', () => {
    it('should create a member', () => {
      const memberData = {
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com'
      };

      service.createMember(memberData).subscribe(member => {
        expect(member).toEqual(mockMember);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(memberData);
      req.flush(mockMember);
    });
  });

  describe('updateMember', () => {
    it('should update a member', () => {
      const memberUpdate = {
        email: 'john.updated@example.com'
      };

      service.updateMember(1, memberUpdate).subscribe(member => {
        expect(member).toEqual(mockMember);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(memberUpdate);
      req.flush(mockMember);
    });
  });

  describe('deleteMember', () => {
    it('should delete a member', () => {
      service.deleteMember(1).subscribe();

      const req = httpMock.expectOne(`${environment.apiUrl}/people/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('searchMembers', () => {
    it('should search members', () => {
      const mockMembers = [mockMember];

      service.searchMembers('john').subscribe(members => {
        expect(members).toEqual(mockMembers);
      });

      const req = httpMock.expectOne(request => 
        request.url === `${environment.apiUrl}/people/search` &&
        request.params.get('search') === 'john'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockMembers);
    });
  });

  describe('getMemberEnrollments', () => {
    it('should fetch member enrollments', () => {
      const mockEnrollments = [{ id: 1, course_title: 'Test Course' }];

      service.getMemberEnrollments(1).subscribe(enrollments => {
        expect(enrollments).toEqual(mockEnrollments);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people/1/enrollments`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEnrollments);
    });
  });

  describe('getMemberProgress', () => {
    it('should fetch member progress', () => {
      const mockProgress = { overall_progress: 75, completed_courses: 3 };

      service.getMemberProgress(1).subscribe(progress => {
        expect(progress).toEqual(mockProgress);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/people/1/progress`);
      expect(req.request.method).toBe('GET');
      req.flush(mockProgress);
    });
  });
});
