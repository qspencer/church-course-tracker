import { Injectable, isDevMode } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PlanningCenterEvent {
  id: string;
  type: string;
  attributes: {
    name: string;
    start_date: string;
    end_date: string;
    created_at: string;
    updated_at: string;
    [key: string]: any;
  };
  relationships: {
    event_type: {
      data: {
        id: string;
        type: string;
      }
    }
  };
}

export interface PlanningCenterList {
  id: string;
  type: string;
  attributes: {
    name: string;
    created_at: string;
    updated_at: string;
    [key: string]: any;
  };
}

@Injectable({
  providedIn: 'root'
})
export class PlanningCenterService {
  private readonly API_URL = `${environment.apiUrl}/planning-center`;

  constructor(private http: HttpClient) { 
    // Only log in development mode
    if (isDevMode()) {
      console.log('PlanningCenterService API_URL:', this.API_URL);
      if (!this.API_URL.startsWith('https://') && !this.API_URL.includes('localhost')) {
        console.error('❌ PlanningCenterService API_URL is NOT HTTPS!', this.API_URL);
      }
    }
  }

  getEvents(): Observable<PlanningCenterEvent[]> {
    // Trust the API_URL from environment
    const url = `${this.API_URL}/events`;
    return this.http.get<PlanningCenterEvent[]>(url);
  }

  getLists(): Observable<PlanningCenterList[]> {
    const url = `${this.API_URL}/lists`;
    return this.http.get<PlanningCenterList[]>(url);
  }

  syncAll(): Observable<any> {
    const url = `${this.API_URL}/all`;
    return this.http.post(url, {});
  }
}
