import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Course, CourseCreate, CourseUpdate, Content, ContentCreate } from '../models';

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private readonly API_URL = `${environment.apiUrl}/courses`;

  constructor(private http: HttpClient) {}

  getCourses(params?: any): Observable<Course[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    return this.http.get<Course[]>(this.API_URL, { params: httpParams });
  }

  getCourse(id: number): Observable<Course> {
    return this.http.get<Course>(`${this.API_URL}/${id}`);
  }

  createCourse(course: CourseCreate): Observable<Course> {
    return this.http.post<Course>(this.API_URL, course);
  }

  updateCourse(id: number, course: CourseUpdate): Observable<Course> {
    return this.http.put<Course>(`${this.API_URL}/${id}`, course);
  }

  deleteCourse(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}`);
  }

  getCourseContent(courseId: number): Observable<Content[]> {
    return this.http.get<Content[]>(`${this.API_URL}/${courseId}/content`);
  }

  addCourseContent(content: ContentCreate): Observable<Content> {
    return this.http.post<Content>(`${this.API_URL}/${content.course_id}/content`, content);
  }

  updateCourseContent(courseId: number, contentId: number, content: Partial<Content>): Observable<Content> {
    return this.http.put<Content>(`${this.API_URL}/${courseId}/content/${contentId}`, content);
  }

  deleteCourseContent(courseId: number, contentId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${courseId}/content/${contentId}`);
  }

  getCourseStats(courseId: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/${courseId}/stats`);
  }
}
