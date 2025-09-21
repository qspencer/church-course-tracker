import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Progress, ProgressStatus } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ProgressService {
  private readonly API_URL = `${environment.apiUrl}/progress`;

  constructor(private http: HttpClient) {}

  getProgress(params?: any): Observable<Progress[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<Progress[]>(this.API_URL, { params: httpParams });
  }

  getProgressByEnrollment(enrollmentId: number): Observable<Progress[]> {
    return this.http.get<Progress[]>(`${this.API_URL}/enrollment/${enrollmentId}`);
  }

  updateProgress(id: number, status: ProgressStatus): Observable<Progress> {
    return this.http.put<Progress>(`${this.API_URL}/${id}`, { status });
  }

  markContentComplete(enrollmentId: number, contentId: number): Observable<Progress> {
    return this.http.post<Progress>(`${this.API_URL}/complete`, {
      enrollment_id: enrollmentId,
      content_id: contentId
    });
  }

  getPersonProgress(personId: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/person/${personId}`);
  }

  getCourseProgress(courseId: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/course/${courseId}`);
  }
}
