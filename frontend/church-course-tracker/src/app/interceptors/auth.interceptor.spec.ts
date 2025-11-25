import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { HTTP_INTERCEPTORS, HttpClient, HttpErrorResponse, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

describe('AuthInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let authServiceSpy: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    const authSpy = jasmine.createSpyObj('AuthService', ['getToken', 'refreshToken', 'logout']);

    TestBed.configureTestingModule({
    imports: [],
    providers: [
        { provide: AuthService, useValue: authSpy },
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true
        },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting()
    ]
});

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should add Authorization header when token exists', () => {
    authServiceSpy.getToken.and.returnValue('test-token');

    httpClient.get('/test').subscribe();

    const req = httpMock.expectOne('/test');
    expect(req.request.headers.get('Authorization')).toBe('Bearer test-token');
    req.flush({});
  });

  it('should not add Authorization header when no token', () => {
    authServiceSpy.getToken.and.returnValue(null);

    httpClient.get('/test').subscribe();

    const req = httpMock.expectOne('/test');
    expect(req.request.headers.has('Authorization')).toBe(false);
    req.flush({});
  });

  it('should retry request with new token on 401 error', () => {
    // Set up the mock to return old token first, then new token
    let tokenCallCount = 0;
    authServiceSpy.getToken.and.callFake(() => {
      tokenCallCount++;
      return tokenCallCount === 1 ? 'old-token' : 'new-token';
    });
    
    authServiceSpy.refreshToken.and.returnValue(of({
      access_token: 'new-token',
      token_type: 'Bearer',
      user: {} as any
    }));

    httpClient.get('/test').subscribe();

    // First request with old token
    const req1 = httpMock.expectOne('/test');
    expect(req1.request.headers.get('Authorization')).toBe('Bearer old-token');
    req1.flush({}, { status: 401, statusText: 'Unauthorized' });

    // Second request with new token
    const req2 = httpMock.expectOne('/test');
    expect(req2.request.headers.get('Authorization')).toBe('Bearer new-token');
    req2.flush({ data: 'success' });
  });

  it('should logout user when refresh token fails', () => {
    authServiceSpy.getToken.and.returnValue('expired-token');
    authServiceSpy.refreshToken.and.returnValue(throwError(() => new Error('Refresh failed')));

    httpClient.get('/test').subscribe({
      error: (error) => {
        // Error might be wrapped in HttpErrorResponse or be an Error directly
        expect(error instanceof Error || error?.error instanceof Error || error?.message).toBeTruthy();
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 401, statusText: 'Unauthorized' });

    expect(authServiceSpy.logout).toHaveBeenCalled();
  });

  it('should pass through non-401 errors', () => {
    authServiceSpy.getToken.and.returnValue('valid-token');

    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(500);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 500, statusText: 'Server Error' });
  });
});
