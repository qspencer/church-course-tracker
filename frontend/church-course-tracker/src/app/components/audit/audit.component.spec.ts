/**
 * Smoke test for AuditComponent.
 * Pre-Angular-18→21-migration coverage; the May-25 audit identified
 * /audit as having zero Karma specs. This test verifies the component
 * BOOTS under future Angular versions; behavioral tests are P1 #15.
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { AuditComponent } from './audit.component';
import { AuditService } from '../../services/audit.service';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';
import { LoggerService } from '../../services/logger.service';

describe('AuditComponent (smoke)', () => {
  let component: AuditComponent;
  let fixture: ComponentFixture<AuditComponent>;

  beforeEach(async () => {
    const auditSpy = jasmine.createSpyObj('AuditService', [
      'getAuditLogs',
      'getAuditSummary',
      'downloadAuditLogs',
    ]);
    auditSpy.getAuditLogs.and.returnValue(of({ items: [], total: 0 }));
    auditSpy.getAuditSummary.and.returnValue(of({ total_logs: 0, recent_activity: [] }));
    auditSpy.downloadAuditLogs.and.returnValue(of(new Blob()));

    const authSpy = jasmine.createSpyObj('AuthService', ['hasAnyRole', 'getCurrentUser']);
    authSpy.hasAnyRole.and.returnValue(true);
    authSpy.getCurrentUser.and.returnValue({ id: 1, username: 'admin', role: 'admin' });

    const userSpy = jasmine.createSpyObj('UserService', ['getUsers']);
    userSpy.getUsers.and.returnValue(of([]));

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [AuditComponent],
      imports: [BrowserAnimationsModule, ReactiveFormsModule, FormsModule, MatDialogModule],
      schemas: [NO_ERRORS_SCHEMA],
      providers: [
        { provide: AuditService, useValue: auditSpy },
        { provide: AuthService, useValue: authSpy },
        { provide: UserService, useValue: userSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AuditComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
