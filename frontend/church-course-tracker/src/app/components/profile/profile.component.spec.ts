/**
 * Smoke test for ProfileComponent.
 * Pre-Angular-18→21-migration coverage. Reactive Forms in /profile is
 * exactly the kind of component that Angular major-version migrations
 * can silently break (FormBuilder internals changed in v17/19).
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { ProfileComponent } from './profile.component';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { LoggerService } from '../../services/logger.service';

describe('ProfileComponent (smoke)', () => {
  let component: ProfileComponent;
  let fixture: ComponentFixture<ProfileComponent>;

  beforeEach(async () => {
    const userSpy = jasmine.createSpyObj('UserService', [
      'updateCurrentUserProfile',
      'changePassword',
      'getUserPreferences',
      'updateUserPreferences',
    ]);
    userSpy.updateCurrentUserProfile.and.returnValue(of({}));
    userSpy.changePassword.and.returnValue(of({}));
    userSpy.getUserPreferences.and.returnValue(of({}));
    userSpy.updateUserPreferences.and.returnValue(of({}));

    const authSpy = jasmine.createSpyObj('AuthService', ['getCurrentUser']);
    authSpy.getCurrentUser.and.returnValue({
      id: 1,
      username: 'smoke',
      email: 'smoke@example.com',
      full_name: 'Smoke User',
      role: 'admin',
      is_active: true,
    });

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [ProfileComponent],
      imports: [BrowserAnimationsModule, ReactiveFormsModule, FormsModule],
      schemas: [NO_ERRORS_SCHEMA],
      providers: [
        { provide: UserService, useValue: userSpy },
        { provide: AuthService, useValue: authSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ProfileComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
