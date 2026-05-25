import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';

import { MemberEnrollmentsDialogComponent, MemberEnrollmentsDialogData } from './member-enrollments-dialog.component';
import { Enrollment, EnrollmentStatus } from '../../../models';
import { Person } from '../../../models';

describe('MemberEnrollmentsDialogComponent', () => {
  let component: MemberEnrollmentsDialogComponent;
  let fixture: ComponentFixture<MemberEnrollmentsDialogComponent>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<MemberEnrollmentsDialogComponent>>;

  const mockMember: Person = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    planning_center_id: 'pc123',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const mockEnrollment: Enrollment = {
    id: 1,
    person_id: 1,
    course_id: 1,
    status: EnrollmentStatus.COMPLETED,
    progress_percentage: 100,
    enrolled_at: '2023-01-01T00:00:00Z',
    completion_date: '2023-06-01T00:00:00Z',
    notes: null,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  beforeEach(async () => {
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
    imports: [
        BrowserAnimationsModule,
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
        MatCardModule,
        MemberEnrollmentsDialogComponent
    ],
    providers: [
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { member: mockMember, enrollments: [mockEnrollment] } }
    ]
}).compileComponents();

    fixture = TestBed.createComponent(MemberEnrollmentsDialogComponent);
    component = fixture.componentInstance;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<MemberEnrollmentsDialogComponent>>;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with member and enrollments', () => {
    expect(component.member).toEqual(mockMember);
    expect(component.enrollments).toEqual([mockEnrollment]);
  });

  it('should handle empty enrollments array', () => {
    // Create a new component instance with empty enrollments since enrollments are set in constructor
    TestBed.resetTestingModule();
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    
    TestBed.configureTestingModule({
    imports: [
        BrowserAnimationsModule,
        MatDialogModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
        MatCardModule,
        MemberEnrollmentsDialogComponent
    ],
    providers: [
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: { member: mockMember, enrollments: [] } }
    ]
}).compileComponents();

    const newFixture = TestBed.createComponent(MemberEnrollmentsDialogComponent);
    const newComponent = newFixture.componentInstance;
    newFixture.detectChanges();

    expect(newComponent.enrollments).toEqual([]);
  });

  describe('getStatusColor', () => {
    it('should return primary for completed', () => {
      expect(component.getStatusColor('completed')).toBe('primary');
    });

    it('should return accent for in_progress', () => {
      expect(component.getStatusColor('in_progress')).toBe('accent');
    });

    it('should return warn for dropped', () => {
      expect(component.getStatusColor('dropped')).toBe('warn');
    });

    it('should return empty string for enrolled', () => {
      expect(component.getStatusColor('enrolled')).toBe('');
    });

    it('should return empty string for unknown status', () => {
      expect(component.getStatusColor('unknown')).toBe('');
    });
  });

  describe('getStatusText', () => {
    it('should format status text', () => {
      expect(component.getStatusText('in_progress')).toBe('In Progress');
    });

    it('should handle status with underscore', () => {
      expect(component.getStatusText('enrolled')).toBe('Enrolled');
    });
  });

  describe('formatDate', () => {
    it('should format valid date', () => {
      const formatted = component.formatDate('2023-01-15T10:30:00Z');
      expect(formatted).toContain('Jan');
      expect(formatted).toContain('2023');
    });

    it('should return N/A for null', () => {
      expect(component.formatDate(null)).toBe('N/A');
    });

    it('should return N/A for undefined', () => {
      expect(component.formatDate(undefined)).toBe('N/A');
    });

    it('should return N/A for invalid date string', () => {
      expect(component.formatDate('invalid-date')).toBe('N/A');
    });
  });

  describe('close', () => {
    it('should close dialog', () => {
      component.close();
      expect(dialogRefSpy.close).toHaveBeenCalled();
    });
  });
});
