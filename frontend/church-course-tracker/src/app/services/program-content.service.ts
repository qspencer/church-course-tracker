/**
 * Program Content Service
 * 
 * This service handles API calls for program content management including
 * modules (categories) and content items (lessons).
 */

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  ProgramModule, ProgramModuleCreate, ProgramModuleUpdate,
  ProgramContent, ProgramContentCreate, ProgramContentUpdate
} from '../models/program-content.model';

@Injectable({
  providedIn: 'root'
})
export class ProgramContentService {
  private http = inject(HttpClient);

  private readonly API_URL = `${environment.apiUrl}/program-content`;

  // Program Module Methods (Categories)

  createModule(moduleData: ProgramModuleCreate): Observable<ProgramModule> {
    return this.http.post<ProgramModule>(`${this.API_URL}/modules/`, moduleData);
  }

  getProgramModules(programId: number): Observable<ProgramModule[]> {
    return this.http.get<ProgramModule[]>(`${this.API_URL}/modules/${programId}`);
  }

  getModule(moduleId: number): Observable<ProgramModule> {
    return this.http.get<ProgramModule>(`${this.API_URL}/modules/single/${moduleId}`);
  }

  updateModule(moduleId: number, moduleData: ProgramModuleUpdate): Observable<ProgramModule> {
    return this.http.put<ProgramModule>(`${this.API_URL}/modules/${moduleId}`, moduleData);
  }

  deleteModule(moduleId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/modules/${moduleId}`);
  }

  // Program Content Methods (Lessons)

  createContent(contentData: ProgramContentCreate): Observable<ProgramContent> {
    return this.http.post<ProgramContent>(`${this.API_URL}/`, contentData);
  }

  getProgramContent(programId: number, moduleId?: number): Observable<ProgramContent[]> {
    let params = new HttpParams();
    if (moduleId) {
      params = params.set('module_id', moduleId.toString());
    }
    return this.http.get<ProgramContent[]>(`${this.API_URL}/program/${programId}`, { params });
  }

  getContentItem(contentId: number): Observable<ProgramContent> {
    return this.http.get<ProgramContent>(`${this.API_URL}/${contentId}`);
  }

  updateContent(contentId: number, contentData: ProgramContentUpdate): Observable<ProgramContent> {
    return this.http.put<ProgramContent>(`${this.API_URL}/${contentId}`, contentData);
  }

  deleteContent(contentId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${contentId}`);
  }
}


