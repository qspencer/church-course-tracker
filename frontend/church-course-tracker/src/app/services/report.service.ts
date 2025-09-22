import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardStats, ProgressReport, ReportFilters, CompletionTrendsResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private readonly API_URL = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.API_URL}/dashboard`);
  }

  getProgressReport(filters?: ReportFilters): Observable<ProgressReport> {
    let httpParams = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = (filters as any)[key];
        if (value !== null && value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => httpParams = httpParams.append(key, v.toString()));
          } else {
            httpParams = httpParams.set(key, value.toString());
          }
        }
      });
    }
    return this.http.get<ProgressReport>(`${this.API_URL}/progress`, { params: httpParams });
  }

  getCompletionTrends(filters?: ReportFilters): Observable<CompletionTrendsResponse> {
    let httpParams = new HttpParams();
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = (filters as any)[key];
        if (value !== null && value !== undefined) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get<CompletionTrendsResponse>(`${this.API_URL}/completion-trends`, { params: httpParams });
  }

  exportReport(reportType: string, filters?: ReportFilters): Observable<Blob> {
    let httpParams = new HttpParams().set('type', reportType);
    if (filters) {
      Object.keys(filters).forEach(key => {
        const value = (filters as any)[key];
        if (value !== null && value !== undefined) {
          httpParams = httpParams.set(key, value.toString());
        }
      });
    }
    return this.http.get(`${this.API_URL}/export`, { 
      params: httpParams,
      responseType: 'blob'
    });
  }
}
