/**
 * Smoke test for ParticipantsManagementComponent.
 *
 * Added 2026-05-25 ahead of the Angular 18→21 migration. The pre-upgrade
 * coverage assessment flagged this component at 0.8% line coverage with
 * no e2e visits to /programs - meaning an Angular major-version regression
 * in this surface would ship silently. This spec verifies the component
 * BOOTS under the current and future Angular versions; behavioral tests
 * are a separate concern (P1 #15 in the roadmap).
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { ParticipantsManagementComponent } from './participants-management.component';
import { ProgramService } from '../../../services/program.service';
import { MemberService } from '../../../services/member.service';
import { SearchFilterService } from '../../../shared/search-filter.service';
import { LoggerService } from '../../../services/logger.service';
import { Program } from '../../../models/program.model';

describe('ParticipantsManagementComponent (smoke)', () => {
  let component: ParticipantsManagementComponent;
  let fixture: ComponentFixture<ParticipantsManagementComponent>;

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
      'getProgramParticipants',
      'getProgramParticipantsCount',
      'removeProgramParticipant',
    ]);
    programSpy.getProgramParticipants.and.returnValue(of([]));
    programSpy.getProgramParticipantsCount.and.returnValue(of(0));
    programSpy.removeProgramParticipant.and.returnValue(of({}));

    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    memberSpy.getMembers.and.returnValue(of([]));

    const searchFilterSpy = jasmine.createSpyObj('SearchFilterService', [
      'filterByParticipantNames',
    ]);
    searchFilterSpy.filterByParticipantNames.and.callFake((items: any[]) => items);

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
    imports: [BrowserAnimationsModule, MatDialogModule, ParticipantsManagementComponent],
    schemas: [NO_ERRORS_SCHEMA], // template uses Material elements - we
    // don't care for a boot-only smoke test
    providers: [
        { provide: ProgramService, useValue: programSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: SearchFilterService, useValue: searchFilterSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { program: mockProgram } },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
    ],
}).compileComponents();

    fixture = TestBed.createComponent(ParticipantsManagementComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing (component DI + constructor body)', () => {
    expect(component).toBeTruthy();
  });
});
