import { Injectable, isDevMode } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoggerService } from './logger.service';
import { Enrollment, EnrollmentCreate, EnrollmentUpdate } from '../models';

@Injectable({
  providedIn: 'root'
})
export class EnrollmentService {
  private readonly API_URL = `${environment.apiUrl}/enrollments`;

  constructor(
    private http: HttpClient,
    private logger: LoggerService
  ) {
    // Only log errors in development mode - reduce console noise
    if (isDevMode() && !this.API_URL.startsWith('https://') && !this.API_URL.includes('localhost')) {
      this.logger.error('EnrollmentService API_URL is NOT HTTPS!', { url: this.API_URL });
    }
  }

  getEnrollments(params?: { skip?: number; limit?: number; course_id?: number; people_id?: number; status?: string }): Observable<Enrollment[]> {
    let httpParams = new HttpParams();
    if (params) {
      (Object.keys(params) as Array<keyof typeof params>).forEach((key) => {
        const value = params[key];
        if (value !== null && value !== undefined) {
          httpParams = httpParams.set(String(key), String(value));
        }
      });
    }
    
    // Trust the API_URL from environment
    const url = this.API_URL;
    
    // Only log errors in development mode - reduce console noise
    if (isDevMode()) {
      const fullUrlWithParams = `${url}?${httpParams.toString()}`;
      if (!fullUrlWithParams.startsWith('https://') && !fullUrlWithParams.includes('localhost')) {
        this.logger.error('EnrollmentService - Full URL with params is NOT HTTPS!', { url: fullUrlWithParams });
      }
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

  importRegistrations(courseId: number, eventId: string, registrationIds: string[]): Observable<Enrollment[]> {
    return this.http.post<Enrollment[]>(`${this.API_URL}/import-registrations`, {
      course_id: courseId,
      event_id: eventId,
      registration_ids: registrationIds,
      update_existing: true
    });
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

  bulkEnrollFromPCEvent(data: { course_id: number, pc_event_id: string, status_filter?: string[], update_existing?: boolean }): Observable<Enrollment[]> {
    return this.http.post<Enrollment[]>(`${this.API_URL}/bulk-from-pc-event`, data);
  }

  bulkEnrollFromPCList(data: { course_id: number, pc_list_id: string, update_existing?: boolean }): Observable<Enrollment[]> {
    return this.http.post<Enrollment[]>(`${this.API_URL}/bulk-from-pc-list`, data);
  }
}
