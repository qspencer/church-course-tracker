import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Enrollment, EnrollmentCreate, EnrollmentUpdate } from '../models';

@Injectable({
  providedIn: 'root'
})
export class EnrollmentService {
  private readonly API_URL = `${environment.apiUrl}/enrollments`;

  constructor(private http: HttpClient) {
    // Debug: Log the API URL to verify it's HTTPS
    console.log('EnrollmentService API_URL:', this.API_URL);
    if (!this.API_URL.startsWith('https://')) {
      console.error('❌ EnrollmentService API_URL is NOT HTTPS!', this.API_URL);
    }
  }

  getEnrollments(params?: any): Observable<Enrollment[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    // Debug: Log the actual URL being requested
    console.log('EnrollmentService.getEnrollments - Requesting URL:', this.API_URL);
    console.log('EnrollmentService.getEnrollments - Query params:', httpParams.toString());
    
    // Ensure URL is absolute HTTPS (defensive check)
    const url = this.API_URL.startsWith('https://') ? this.API_URL : `https://${this.API_URL.replace(/^https?:\/\//, '')}`;
    
    // Construct full URL with params for logging
    const fullUrlWithParams = `${url}?${httpParams.toString()}`;
    console.log('EnrollmentService.getEnrollments - Final URL (base):', url);
    console.log('EnrollmentService.getEnrollments - Final URL (with params):', fullUrlWithParams);
    
    if (!fullUrlWithParams.startsWith('https://')) {
      console.error('❌ EnrollmentService - Full URL with params is NOT HTTPS!', fullUrlWithParams);
    }
    
    return this.http.get<Enrollment[]>(url, { params: httpParams });
  }

  getEnrollment(id: number): Observable<Enrollment> {
    return this.http.get<Enrollment>(`${this.API_URL}/${id}`);
  }

  createEnrollment(enrollment: EnrollmentCreate): Observable<Enrollment> {
    return this.http.post<Enrollment>(this.API_URL, enrollment);
  }

  updateEnrollment(id: number, enrollment: EnrollmentUpdate): Observable<Enrollment> {
    return this.http.put<Enrollment>(`${this.API_URL}/${id}`, enrollment);
  }

  deleteEnrollment(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`);
  }

  getEnrollmentsByPerson(personId: number): Observable<Enrollment[]> {
    return this.http.get<Enrollment[]>(`${this.API_URL}/person/${personId}`);
  }

  getEnrollmentsByCourse(courseId: number): Observable<Enrollment[]> {
    return this.http.get<Enrollment[]>(`${this.API_URL}/course/${courseId}`);
  }

  bulkEnroll(enrollments: EnrollmentCreate[]): Observable<Enrollment[]> {
    return this.http.post<Enrollment[]>(`${this.API_URL}/bulk`, enrollments);
  }
}
