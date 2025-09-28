import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuditLog, AuditLogFilters, AuditSummary, AuditExportOptions } from '../models';

@Injectable({
  providedIn: 'root'
})
export class AuditService {
  private readonly API_URL = `${environment.apiUrl}/audit`;

  constructor(private http: HttpClient) {}

  /**
   * Get system-wide audit logs with filtering options
   */
  getAuditLogs(filters: AuditLogFilters = {}): Observable<AuditLog[]> {
    let params = new HttpParams();
    
    if (filters.table_name) {
      params = params.set('table_name', filters.table_name);
    }
    
    if (filters.action) {
      params = params.set('action', filters.action);
    }
    
    if (filters.changed_by) {
      params = params.set('changed_by', filters.changed_by.toString());
    }
    
    if (filters.start_date) {
      params = params.set('start_date', filters.start_date);
    }
    
    if (filters.end_date) {
      params = params.set('end_date', filters.end_date);
    }
    
    if (filters.skip !== undefined) {
      params = params.set('skip', filters.skip.toString());
    }
    
    if (filters.limit !== undefined) {
      params = params.set('limit', filters.limit.toString());
    }
    
    return this.http.get<AuditLog[]>(this.API_URL, { params });
  }

  /**
   * Get audit log summary statistics
   */
  getAuditSummary(startDate?: string, endDate?: string): Observable<AuditSummary> {
    let params = new HttpParams();
    
    if (startDate) {
      params = params.set('start_date', startDate);
    }
    
    if (endDate) {
      params = params.set('end_date', endDate);
    }
    
    return this.http.get<AuditSummary>(`${this.API_URL}/summary`, { params });
  }

  /**
   * Get audit logs for a specific table
   */
  getTableAuditLogs(
    tableName: string, 
    recordId?: number, 
    skip: number = 0, 
    limit: number = 100
  ): Observable<AuditLog[]> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    
    if (recordId) {
      params = params.set('record_id', recordId.toString());
    }
    
    return this.http.get<AuditLog[]>(`${this.API_URL}/table/${tableName}`, { params });
  }

  /**
   * Get audit logs for a specific user
   */
  getUserAuditLogs(
    userId: number, 
    skip: number = 0, 
    limit: number = 100
  ): Observable<AuditLog[]> {
    const params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    
    return this.http.get<AuditLog[]>(`${this.API_URL}/user/${userId}`, { params });
  }

  /**
   * Export audit logs
   */
  exportAuditLogs(options: AuditExportOptions): Observable<Blob> {
    let params = new HttpParams().set('format', options.format);
    
    if (options.start_date) {
      params = params.set('start_date', options.start_date);
    }
    
    if (options.end_date) {
      params = params.set('end_date', options.end_date);
    }
    
    if (options.table_name) {
      params = params.set('table_name', options.table_name);
    }
    
    return this.http.get(`${this.API_URL}/export`, { 
      params, 
      responseType: 'blob' 
    });
  }

  /**
   * Download exported audit logs
   */
  downloadAuditLogs(options: AuditExportOptions): void {
    this.exportAuditLogs(options).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        const extension = options.format === 'csv' ? 'csv' : 'json';
        link.download = `audit_logs_${new Date().toISOString().split('T')[0]}.${extension}`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Error downloading audit logs:', error);
      }
    });
  }
}


