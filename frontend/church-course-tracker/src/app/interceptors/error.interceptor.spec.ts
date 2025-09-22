import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HTTP_INTERCEPTORS, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ErrorInterceptor } from './error.interceptor';

describe('ErrorInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  beforeEach(() => {
    const snackBarSpyObj = jasmine.createSpyObj('MatSnackBar', ['open']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        { provide: MatSnackBar, useValue: snackBarSpyObj },
        {
          provide: HTTP_INTERCEPTORS,
          useClass: ErrorInterceptor,
          multi: true
        }
      ]
    });

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should pass through successful requests', () => {
    httpClient.get('/test').subscribe(response => {
      expect(response).toEqual({ success: true });
    });

    const req = httpMock.expectOne('/test');
    req.flush({ success: true });
    expect(snackBarSpy.open).not.toHaveBeenCalled();
  });

  it('should show error message for 400 bad request', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(400);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({ detail: 'Bad request error' }, { status: 400, statusText: 'Bad Request' });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Bad request error', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });

  it('should not show error message for 401 unauthorized', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(401);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 401, statusText: 'Unauthorized' });

    expect(snackBarSpy.open).not.toHaveBeenCalled();
  });

  it('should show error message for 403 forbidden', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(403);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 403, statusText: 'Forbidden' });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Access forbidden', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });

  it('should show error message for 404 not found', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(404);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 404, statusText: 'Not Found' });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Resource not found', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });

  it('should show error message for 500 internal server error', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(500);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({}, { status: 500, statusText: 'Internal Server Error' });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Internal server error', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });

  it('should show custom error message from server', () => {
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(422);
      }
    });

    const req = httpMock.expectOne('/test');
    req.flush({ detail: 'Custom validation error' }, { status: 422, statusText: 'Unprocessable Entity' });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Custom validation error', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });

  it('should handle client-side errors', () => {
    // This test is more complex to set up with HttpClientTestingModule
    // In a real scenario, you would test network errors differently
    httpClient.get('/test').subscribe({
      error: (error: HttpErrorResponse) => {
        // Error handled by interceptor
      }
    });

    const req = httpMock.expectOne('/test');
    const errorEvent = new ErrorEvent('Network error', { message: 'Network error' });
    req.error(errorEvent, { status: 0 });

    expect(snackBarSpy.open).toHaveBeenCalledWith('Network error', 'Close', {
      duration: 5000,
      horizontalPosition: 'end',
      verticalPosition: 'top'
    });
  });
});
