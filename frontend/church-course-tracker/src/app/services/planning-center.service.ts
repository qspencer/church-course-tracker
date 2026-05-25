import { Injectable, isDevMode, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoggerService } from './logger.service';

export interface PlanningCenterEvent {
  id: string;
  type: string;
  attributes: {
    name: string;
    start_date: string;
    end_date: string;
    created_at: string;
    updated_at: string;
    [key: string]: string | number | boolean | null | undefined;
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
    [key: string]: string | number | boolean | null | undefined;
  };
}

@Injectable({
  providedIn: 'root'
})
export class PlanningCenterService {
  private http = inject(HttpClient);
  private logger = inject(LoggerService);

  private readonly API_URL = `${environment.apiUrl}/planning-center`;

  constructor() { 
    // Only log in development mode
    if (isDevMode()) {
      this.logger.debug('PlanningCenterService API_URL', { apiUrl: this.API_URL });
      if (!this.API_URL.startsWith('https://') && !this.API_URL.includes('localhost')) {
        this.logger.error('PlanningCenterService API_URL is NOT HTTPS!', null, { apiUrl: this.API_URL });
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

  getEvent(eventId: string): Observable<PlanningCenterEvent> {
    const url = `${this.API_URL}/events/${eventId}`;
    return this.http.get<PlanningCenterEvent>(url);
  }

  getList(listId: string): Observable<PlanningCenterList> {
    const url = `${this.API_URL}/lists/${listId}`;
    return this.http.get<PlanningCenterList>(url);
  }

  syncAll(): Observable<{ success: boolean; message: string; synced_count?: number }> {
    const url = `${this.API_URL}/all`;
    return this.http.post<{ success: boolean; message: string; synced_count?: number }>(url, {});
  }

  searchPeople(searchTerm: string, limit: number = 20): Observable<PlanningCenterPerson[]> {
    const url = `${this.API_URL}/people/search`;
    return this.http.get<PlanningCenterPerson[]>(url, {
      params: { q: searchTerm, limit: limit.toString() }
    });
  }

  getEventRegistrations(eventId: string): Observable<PlanningCenterRegistration[]> {
    const url = `${this.API_URL}/events/${eventId}/registrations`;
    return this.http.get<PlanningCenterRegistration[]>(url);
  }
}

export interface PlanningCenterRegistration {
  id: string;
  type: string;
  imported?: boolean; // UI flag to track if registration has been imported
  attributes: {
    status?: string;
    registration_date?: string;
    notes?: string;
    [key: string]: string | number | boolean | null | undefined;
  };
  relationships?: {
    person?: {
      data: {
        id: string;
        type: string;
      };
    };
    [key: string]: {
      data?: {
        id: string;
        type: string;
      };
    } | string | number | boolean | null | undefined;
  };
}

export interface PlanningCenterPerson {
  id: string;
  type: string;
  attributes: {
    first_name: string;
    last_name: string;
    email?: string;
    phone_number?: string;
    [key: string]: string | number | boolean | null | undefined;
  };
  relationships?: {
    [key: string]: string | number | boolean | null | undefined;
  };
}
