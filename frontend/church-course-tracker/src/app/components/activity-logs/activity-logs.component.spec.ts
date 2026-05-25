/**
 * Smoke test for ActivityLogsComponent.
 * Pre-Angular-18→21-migration coverage.
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { ActivityLogsComponent } from './activity-logs.component';
import { AuditService } from '../../services/audit.service';
import { AuthService } from '../../services/auth.service';
import { LoggerService } from '../../services/logger.service';

describe('ActivityLogsComponent (smoke)', () => {
  let component: ActivityLogsComponent;
  let fixture: ComponentFixture<ActivityLogsComponent>;

  beforeEach(async () => {
    const auditSpy = jasmine.createSpyObj('AuditService', ['getStaffActivityLogs']);
    auditSpy.getStaffActivityLogs.and.returnValue(of({ items: [], total: 0 }));

    const authSpy = jasmine.createSpyObj('AuthService', ['hasAnyRole']);
    authSpy.hasAnyRole.and.returnValue(true);

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [ActivityLogsComponent],
      imports: [BrowserAnimationsModule, ReactiveFormsModule, FormsModule],
      schemas: [NO_ERRORS_SCHEMA],
      providers: [
        { provide: AuditService, useValue: auditSpy },
        { provide: AuthService, useValue: authSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ActivityLogsComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
