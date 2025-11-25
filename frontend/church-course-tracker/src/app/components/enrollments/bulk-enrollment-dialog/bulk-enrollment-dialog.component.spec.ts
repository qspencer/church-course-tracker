import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { of } from 'rxjs';

import { BulkEnrollmentDialogComponent } from './bulk-enrollment-dialog.component';
import { PlanningCenterService } from '../../../services/planning-center.service';
import { CourseService } from '../../../services/course.service';
import { EnrollmentService } from '../../../services/enrollment.service';

describe('BulkEnrollmentDialogComponent', () => {
  let component: BulkEnrollmentDialogComponent;
  let fixture: ComponentFixture<BulkEnrollmentDialogComponent>;

  beforeEach(async () => {
    const planningCenterSpy = jasmine.createSpyObj('PlanningCenterService', ['getEvents', 'getLists']);
    planningCenterSpy.getEvents.and.returnValue(of([]));
    planningCenterSpy.getLists.and.returnValue(of([]));
    
    const courseSpy = jasmine.createSpyObj('CourseService', ['getCourses']);
    courseSpy.getCourses.and.returnValue(of([]));
    
    const enrollmentSpy = jasmine.createSpyObj('EnrollmentService', ['bulkEnrollFromPCEvent', 'bulkEnrollFromPCList']);
    
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [BulkEnrollmentDialogComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatSelectModule,
        MatRadioModule,
        MatButtonModule,
        MatProgressSpinnerModule,
        MatCheckboxModule
      ],
      providers: [
        { provide: PlanningCenterService, useValue: planningCenterSpy },
        { provide: CourseService, useValue: courseSpy },
        { provide: EnrollmentService, useValue: enrollmentSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BulkEnrollmentDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
