/**
 * Smoke test for ProgressComponent.
 * Pre-Angular-18→21-migration coverage. /progress is exercised by e2e
 * (progress-tracking.spec.ts) but had no Karma unit spec - this catches
 * boot-time regressions faster than the e2e suite.
 */
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';

import { ProgressComponent } from './progress.component';
import { ProgressService } from '../../services/progress.service';
import { EnrollmentService } from '../../services/enrollment.service';
import { CourseService } from '../../services/course.service';
import { MemberService } from '../../services/member.service';
import { LoggerService } from '../../services/logger.service';

describe('ProgressComponent (smoke)', () => {
  let component: ProgressComponent;
  let fixture: ComponentFixture<ProgressComponent>;

  beforeEach(async () => {
    const progressSpy = jasmine.createSpyObj('ProgressService', [
      'getProgressByEnrollment',
      'markContentComplete',
      'updateProgress',
    ]);
    progressSpy.getProgressByEnrollment.and.returnValue(of([]));
    progressSpy.markContentComplete.and.returnValue(of({}));
    progressSpy.updateProgress.and.returnValue(of({}));

    const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['getEnrollments']);
    enrollmentSpy.getEnrollments.and.returnValue(of([]));

    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    courseSpy.getCourses.and.returnValue(of([]));

    const memberSpy = jasmine.createSpyObj('MemberService', ['getMembers']);
    memberSpy.getMembers.and.returnValue(of([]));

    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error', 'warn', 'info', 'debug']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
    imports: [BrowserAnimationsModule, ReactiveFormsModule, FormsModule, ProgressComponent],
    schemas: [NO_ERRORS_SCHEMA],
    providers: [
        { provide: ProgressService, useValue: progressSpy },
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: MemberService, useValue: memberSpy },
        { provide: LoggerService, useValue: loggerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        provideHttpClient(withInterceptorsFromDi()),
        provideHttpClientTesting(),
    ],
}).compileComponents();

    fixture = TestBed.createComponent(ProgressComponent);
    component = fixture.componentInstance;
  });

  it('should construct without throwing', () => {
    expect(component).toBeTruthy();
  });
});
