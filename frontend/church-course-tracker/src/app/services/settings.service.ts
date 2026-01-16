import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  SystemSetting,
  SystemSettingsByCategory,
  SystemSettingUpdate,
  SystemSettingsBatchUpdate,
  PlanningCenterConfig
} from '../models/settings.model';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private readonly API_URL = `${environment.apiUrl}/settings`;

  constructor(private http: HttpClient) {}

  getSettings(category?: string): Observable<SystemSettingsByCategory> {
    let httpParams = new HttpParams();
    if (category) {
      httpParams = httpParams.set('category', category);
    }
    return this.http.get<SystemSettingsByCategory>(this.API_URL, { params: httpParams });
  }

  getSetting(key: string): Observable<SystemSetting> {
    return this.http.get<SystemSetting>(`${this.API_URL}/${key}`);
  }

  updateSetting(key: string, value: string): Observable<SystemSetting> {
    return this.http.patch<SystemSetting>(`${this.API_URL}/${key}`, { value });
  }

  updateSettingsBatch(settings: { [key: string]: string }): Observable<SystemSetting[]> {
    return this.http.patch<SystemSetting[]>(`${this.API_URL}/batch`, { settings });
  }

  getPlanningCenterConfig(): Observable<PlanningCenterConfig> {
    return this.http.get<PlanningCenterConfig>(`${this.API_URL}/planning-center/config`);
  }

  updatePlanningCenterConfig(config: PlanningCenterConfig): Observable<{ [key: string]: SystemSetting }> {
    return this.http.patch<{ [key: string]: SystemSetting }>(`${this.API_URL}/planning-center/config`, config);
  }

  syncToEnvironment(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_URL}/sync-to-env`, {});
  }
}
