import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService } from './user.service';
import { User, UserCreate, UserUpdate } from '../models';
import { environment } from '../../environments/environment';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;
  const API_URL = `${environment.apiUrl}/users`;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    role: 'staff',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockUsers: User[] = [
    mockUser,
    {
      id: 2,
      username: 'admin',
      email: 'admin@example.com',
      full_name: 'Admin User',
      role: 'admin',
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    }
  ];

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getUsers', () => {
    it('should return users with default pagination', () => {
      service.getUsers().subscribe(users => {
        expect(users).toEqual(mockUsers);
      });

      const req = httpMock.expectOne(`${API_URL}?skip=0&limit=100`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUsers);
    });

    it('should return users with custom pagination', () => {
      service.getUsers(10, 20).subscribe(users => {
        expect(users).toEqual(mockUsers);
      });

      const req = httpMock.expectOne(`${API_URL}?skip=10&limit=20`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUsers);
    });
  });

  describe('getUser', () => {
    it('should return a specific user', () => {
      service.getUser(1).subscribe(user => {
        expect(user).toEqual(mockUser);
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUser);
    });
  });

  describe('createUser', () => {
    it('should create a new user', () => {
      const newUser: UserCreate = {
        username: 'newuser',
        email: 'new@example.com',
        full_name: 'New User',
        role: 'staff',
        password: 'password123'
      };

      service.createUser(newUser).subscribe(user => {
        expect(user).toEqual(mockUser);
      });

      const req = httpMock.expectOne(API_URL);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newUser);
      req.flush(mockUser);
    });
  });

  describe('updateUser', () => {
    it('should update an existing user', () => {
      const userUpdate: UserUpdate = {
        full_name: 'Updated Name',
        is_active: false
      };

      const updatedUser = { ...mockUser, ...userUpdate };

      service.updateUser(1, userUpdate).subscribe(user => {
        expect(user).toEqual(updatedUser);
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(userUpdate);
      req.flush(updatedUser);
    });
  });

  describe('deleteUser', () => {
    it('should delete a user', () => {
      service.deleteUser(1).subscribe(response => {
        expect(response).toBeTruthy();
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });
});
