import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AutocompleteSuggestionService {
  private readonly API_URL = `${environment.apiUrl}/autocomplete-suggestions`;

  constructor(private http: HttpClient) {}

  /**
   * Get suggestions for a field type
   * @param fieldType - Type of field (e.g., 'location', 'delivery_mode')
   * @param limit - Maximum number of suggestions to return (default: 50)
   */
  getSuggestions(fieldType: string, limit: number = 50): Observable<string[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<string[]>(`${this.API_URL}/${fieldType}`, { params });
  }

  /**
   * Add or increment a suggestion
   * @param fieldType - Type of field
   * @param value - The suggestion value
   */
  addSuggestion(fieldType: string, value: string): Observable<any> {
    const params = new HttpParams().set('value', value);
    return this.http.post<any>(`${this.API_URL}/${fieldType}`, null, { params });
  }

  /**
   * Add multiple suggestions at once
   * @param fieldType - Type of field
   * @param values - Array of suggestion values
   */
  addSuggestionsBatch(fieldType: string, values: string[]): Observable<any[]> {
    return this.http.post<any[]>(`${this.API_URL}/${fieldType}/batch`, values);
  }
}

