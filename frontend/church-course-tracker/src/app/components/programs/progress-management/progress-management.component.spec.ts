/**
 * Smoke test for ProgressManagementComponent.
 * Pre-Angular-18→21-migration coverage. See sibling
 * participants-management.component.spec.ts for the rationale and pattern.
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { ProgressManagementComponent } from './progress-management.component';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { LoggerService } from '../../../services/logger.service';
import { Program } from '../../../models/program.model';

describe('ProgressManagementComponent (smoke)', () => {
  let component: ProgressManagementComponent;
  let fixture: ComponentFixture<ProgressManagementComponent>;

  const mockProgram: Program = {
    id: 1,
    title: 'Smoke Program',
    description: 'Pre-migration smoke',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  };

  beforeEach(async () => {
    const programSpy = jasmine.createSpyObj('ProgramService', [
      'getProgramProgress',
      'getProgramParticipants',
      'getProgramSessions',
      'deleteProgramProgress',
    ]);
    programSpy.getProgramProgress.and.returnValue(of([]));
    programSpy.getProgramParticipants.and.returnValue(of([]));
    programSpy.getProgramSessions.and.returnValue(of([]));
    programSpy.deleteProgramProgress.and.returnValue(of({}));

    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    memberSpy.getMembers.and.returnValue(of([]));

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
    imports: [BrowserAnimationsModule, MatDialogModule, ProgressManagementComponent],
    schemas: [NO_ERRORS_SCHEMA],
    providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { program: mockProgram } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
    ],
}).compileComponents();

    fixture = TestBed.createComponent(ProgressManagementComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
