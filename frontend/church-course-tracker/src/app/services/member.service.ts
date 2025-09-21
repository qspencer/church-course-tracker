import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Person } from '../models';

@Injectable({
  providedIn: 'root'
})
export class MemberService {
  private readonly API_URL = `${environment.apiUrl}/people`;

  constructor(private http: HttpClient) {}

  getMembers(params?: any): Observable<Person[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
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

  getMemberEnrollments(id: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/${id}/enrollments`);
  }

  getMemberProgress(id: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/${id}/progress`);
  }
}
