import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Person } from '../models';

@Injectable({
  providedIn: 'root'
})
export class MemberService {
  private http = inject(HttpClient);

  private readonly API_URL = `${environment.apiUrl}/people`;

  getMembers(params?: { skip?: number; limit?: number; search?: string; is_active?: boolean }): Observable<Person[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach((key: string) => {
        const value = params[key as keyof typeof params];
        if (value !== null && value !== undefined) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<Person[]>(this.API_URL, { params: httpParams });
  }

  getMember(id: number): Observable<Person> {
    return this.http.get<Person>(`${this.API_URL}/${id}`);
  }

  createMember(member: Partial<Person>): Observable<Person> {
    return this.http.post<Person>(this.API_URL, member);
  }

  updateMember(id: number, member: Partial<Person>): Observable<Person> {
    return this.http.put<Person>(`${this.API_URL}/${id}`, member);
  }

  deleteMember(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`);
  }

  searchMembers(query: string): Observable<Person[]> {
    const params = new HttpParams().set('search', query);
    return this.http.get<Person[]>(`${this.API_URL}/search`, { params });
  }

  getMemberEnrollments(id: number): Observable<Array<{ id: number; course_id: number; status: string; enrollment_date: string }>> {
    return this.http.get<Array<{ id: number; course_id: number; status: string; enrollment_date: string }>>(`${this.API_URL}/${id}/enrollments`);
  }

  getMemberProgress(id: number): Observable<{ total_courses: number; completed_courses: number; in_progress_courses: number }> {
    return this.http.get<{ total_courses: number; completed_courses: number; in_progress_courses: number }>(`${this.API_URL}/${id}/progress`);
  }

  importMemberFromPlanningCenter(planningCenterPersonId: string): Observable<Person> {
    return this.http.post<Person>(`${this.API_URL}/import-from-pc`, {
      planning_center_person_id: planningCenterPersonId
    });
  }
}
