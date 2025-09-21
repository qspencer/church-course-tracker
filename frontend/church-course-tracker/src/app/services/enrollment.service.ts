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

  constructor(private http: HttpClient) {}

  getEnrollments(params?: any): Observable<Enrollment[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<Enrollment[]>(this.API_URL, { params: httpParams });
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
