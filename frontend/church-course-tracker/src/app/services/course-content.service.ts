/**
 * Course Content Service
 * 
 * This service handles API calls for course content management including
 * modules, content items, file uploads, and access tracking.
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  CourseModule, CourseModuleCreate, CourseModuleUpdate,
  CourseContent, CourseContentCreate, CourseContentUpdate,
  ContentAccessLog, ContentAccessLogCreate,
  ContentAuditLog, ContentUploadResponse, ContentProgressUpdate,
  CourseContentSummary, ContentProgress
} from '../models';

@Injectable({
  providedIn: 'root'
})
export class CourseContentService {
  private readonly API_URL = `${environment.apiUrl}/content`;

  constructor(private http: HttpClient) {}

  // Course Module Methods

  createModule(moduleData: CourseModuleCreate): Observable<CourseModule> {
    return this.http.post<CourseModule>(`${this.API_URL}/modules/`, moduleData);
  }

  getCourseModules(courseId: number): Observable<CourseModule[]> {
    return this.http.get<CourseModule[]>(`${this.API_URL}/modules/${courseId}`);
  }

  getModule(moduleId: number): Observable<CourseModule> {
    return this.http.get<CourseModule>(`${this.API_URL}/modules/single/${moduleId}`);
  }

  updateModule(moduleId: number, moduleData: CourseModuleUpdate): Observable<CourseModule> {
    return this.http.put<CourseModule>(`${this.API_URL}/modules/${moduleId}`, moduleData);
  }

  deleteModule(moduleId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/modules/${moduleId}`);
  }

  // Course Content Methods

  createContent(contentData: CourseContentCreate): Observable<CourseContent> {
    return this.http.post<CourseContent>(`${this.API_URL}/`, contentData);
  }

  getCourseContent(courseId: number, moduleId?: number): Observable<CourseContent[]> {
    let params = new HttpParams();
    if (moduleId) {
      params = params.set('module_id', moduleId.toString());
    }
    return this.http.get<CourseContent[]>(`${this.API_URL}/course/${courseId}`, { params });
  }

  getContentItem(contentId: number): Observable<CourseContent> {
    return this.http.get<CourseContent>(`${this.API_URL}/${contentId}`);
  }

  updateContent(contentId: number, contentData: CourseContentUpdate): Observable<CourseContent> {
    return this.http.put<CourseContent>(`${this.API_URL}/${contentId}`, contentData);
  }

  deleteContent(contentId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${contentId}`);
  }

  // File Upload and Download

  uploadFile(contentId: number, file: File): Observable<ContentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ContentUploadResponse>(`${this.API_URL}/${contentId}/upload`, formData);
  }

  downloadContent(contentId: number): Observable<Blob> {
    return this.http.get(`${this.API_URL}/${contentId}/download`, {
      responseType: 'blob'
    });
  }

  // Content Access and Progress Tracking

  logContentAccess(accessData: ContentAccessLogCreate): Observable<ContentAccessLog> {
    return this.http.post<ContentAccessLog>(`${this.API_URL}/${accessData.content_id}/access`, accessData);
  }

  updateContentProgress(progressData: ContentProgressUpdate): Observable<ContentAccessLog> {
    return this.http.put<ContentAccessLog>(`${this.API_URL}/${progressData.content_id}/progress`, progressData);
  }

  getContentAccessLogs(contentId: number, limit: number = 100): Observable<ContentAccessLog[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<ContentAccessLog[]>(`${this.API_URL}/${contentId}/access-logs`, { params });
  }

  getUserContentProgress(userId: number, courseId: number): Observable<{ [key: number]: ContentProgress }> {
    return this.http.get<{ [key: number]: ContentProgress }>(`${this.API_URL}/user/${userId}/course/${courseId}/progress`);
  }

  // Audit Trail

  getContentAuditLogs(contentId: number, limit: number = 100): Observable<ContentAuditLog[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<ContentAuditLog[]>(`${this.API_URL}/${contentId}/audit-logs`, { params });
  }

  // Course Content Summary

  getCourseContentSummary(courseId: number): Observable<CourseContentSummary> {
    return this.http.get<CourseContentSummary>(`${this.API_URL}/course/${courseId}/summary`);
  }

  // Helper Methods

  /**
   * Download content and trigger browser download
   */
  downloadContentFile(content: CourseContent): void {
    this.downloadContent(content.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = content.file_name || content.title;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Error downloading content:', error);
      }
    });
  }

  /**
   * Log content view access
   */
  logContentView(contentId: number): void {
    const accessData: ContentAccessLogCreate = {
      content_id: contentId,
      user_id: 0, // Will be set by the backend based on current user
      access_type: 'view'
    };
    
    this.logContentAccess(accessData).subscribe({
      error: (error) => {
        console.error('Error logging content view:', error);
      }
    });
  }

  /**
   * Log content download access
   */
  logContentDownload(contentId: number): void {
    const accessData: ContentAccessLogCreate = {
      content_id: contentId,
      user_id: 0, // Will be set by the backend based on current user
      access_type: 'download'
    };
    
    this.logContentAccess(accessData).subscribe({
      error: (error) => {
        console.error('Error logging content download:', error);
      }
    });
  }

  /**
   * Update content progress (for videos/audio)
   */
  updateProgress(contentId: number, progressPercentage: number, timeSpent?: number): void {
    const progressData: ContentProgressUpdate = {
      content_id: contentId,
      progress_percentage: progressPercentage,
      time_spent: timeSpent
    };
    
    this.updateContentProgress(progressData).subscribe({
      error: (error) => {
        console.error('Error updating content progress:', error);
      }
    });
  }
}


