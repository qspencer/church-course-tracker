import { Injectable, isDevMode, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Course, CourseCreate, CourseUpdate, CourseQueryParams, Content, ContentCreate } from '../models';

export interface BulkDeleteResponse {
  deleted_count: number;
  deleted_ids: number[];
  failed_ids: number[];
  errors: { course_id: number; error: string }[];
}

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private http = inject(HttpClient);

  private readonly API_URL = `${environment.apiUrl}/courses`;

  constructor() {
    // Only log errors in development mode - reduce console noise
    if (isDevMode() && !this.API_URL.startsWith('https://') && !this.API_URL.includes('localhost')) {
      console.error('❌ CourseService API_URL is NOT HTTPS!', this.API_URL);
    }
  }

  getCourses(params?: CourseQueryParams): Observable<Course[]> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
    }
    
    // Trust the API_URL from environment
    const url = this.API_URL;
    
    // Only log errors in development mode - reduce console noise
    if (isDevMode()) {
      const fullUrlWithParams = `${url}?${httpParams.toString()}`;
      if (!fullUrlWithParams.startsWith('https://') && !fullUrlWithParams.includes('localhost')) {
        console.error('❌ CourseService - Full URL with params is NOT HTTPS!', fullUrlWithParams);
      }
    }
    
    return this.http.get<Course[]>(url, { params: httpParams });
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

  bulkDeleteCourses(courseIds: number[]): Observable<BulkDeleteResponse> {
    return this.http.post<BulkDeleteResponse>(`${this.API_URL}/bulk-delete`, { course_ids: courseIds });
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

  getAvailablePrerequisites(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.API_URL}/prerequisites/available`);
  }
}
