import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { User, UserCreate, UserUpdate, UserProfileUpdate, ChangePasswordRequest, UserPreference, UserPreferenceUpdate } from '../models';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly API_URL = `${environment.apiUrl}/users`;

  constructor(private http: HttpClient) {}

  getUsers(skip: number = 0, limit: number = 100): Observable<User[]> {
    let httpParams = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    
    return this.http.get<User[]>(this.API_URL, { params: httpParams });
  }

  getUser(userId: number): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/${userId}`);
  }

  createUser(user: UserCreate): Observable<User> {
    return this.http.post<User>(this.API_URL, user);
  }

  updateUser(userId: number, user: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.API_URL}/${userId}`, user);
  }

  deleteUser(userId: number): Observable<any> {
    return this.http.delete(`${this.API_URL}/${userId}`);
  }

  // Current user profile methods
  updateCurrentUserProfile(profile: UserProfileUpdate): Observable<User> {
    return this.http.patch<User>(`${this.API_URL}/me`, profile);
  }

  changePassword(passwordData: ChangePasswordRequest): Observable<{ message: string }> {
    return this.http.patch<{ message: string }>(`${this.API_URL}/me/change-password`, passwordData);
  }

  getUserPreferences(): Observable<UserPreference> {
    return this.http.get<UserPreference>(`${this.API_URL}/me/preferences`);
  }

  updateUserPreferences(preferences: UserPreferenceUpdate): Observable<UserPreference> {
    return this.http.patch<UserPreference>(`${this.API_URL}/me/preferences`, preferences);
  }
}
