import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MemberImportDialogComponent } from './member-import-dialog.component';
import { PlanningCenterService } from '../../../services/planning-center.service';
import { MemberService } from '../../../services/member.service';
import { of, throwError } from 'rxjs';

describe('MemberImportDialogComponent', () => {
  let component: MemberImportDialogComponent;
  let fixture: ComponentFixture<MemberImportDialogComponent>;
  let mockPlanningCenterService: jasmine.SpyObj<PlanningCenterService>;
  let mockMemberService: jasmine.SpyObj<MemberService>;
  let mockDialogRef: jasmine.SpyObj<MatDialogRef<MemberImportDialogComponent>>;

  beforeEach(async () => {
    mockPlanningCenterService = jasmine.createSpyObj('PlanningCenterService', ['searchPeople']);
    mockMemberService = jasmine.createSpyObj('MemberService', ['importMemberFromPlanningCenter']);
    mockDialogRef = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
      declarations: [MemberImportDialogComponent],
      imports: [
        ReactiveFormsModule,
        MatDialogModule,
        MatAutocompleteModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatSnackBarModule,
        NoopAnimationsModule
      ],
      providers: [
        { provide: PlanningCenterService, useValue: mockPlanningCenterService },
        { provide: MemberService, useValue: mockMemberService },
        { provide: MatDialogRef, useValue: mockDialogRef }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MemberImportDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should search for people when typing', (done) => {
    const mockPeople = [{
      id: '1',
      type: 'Person',
      attributes: {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com'
      }
    }];

    mockPlanningCenterService.searchPeople.and.returnValue(of(mockPeople));

    component.searchControl.setValue('John');
    
    setTimeout(() => {
      expect(mockPlanningCenterService.searchPeople).toHaveBeenCalled();
      done();
    }, 400); // Wait for debounce
  });

  it('should display person name and email', () => {
    const person = {
      id: '1',
      type: 'Person',
      attributes: {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com'
      }
    };

    const display = component.displayPerson(person);
    expect(display).toBe('John Doe (john@example.com)');
  });

  it('should close dialog on cancel', () => {
    component.onCancel();
    expect(mockDialogRef.close).toHaveBeenCalled();
  });
});


