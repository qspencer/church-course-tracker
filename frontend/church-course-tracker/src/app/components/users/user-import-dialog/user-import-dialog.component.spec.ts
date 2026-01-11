import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { UserImportDialogComponent } from './user-import-dialog.component';
import { PlanningCenterService } from '../../../services/planning-center.service';
import { UserService } from '../../../services/user.service';
import { of, throwError } from 'rxjs';

describe('UserImportDialogComponent', () => {
  let component: UserImportDialogComponent;
  let fixture: ComponentFixture<UserImportDialogComponent>;
  let mockPlanningCenterService: jasmine.SpyObj<PlanningCenterService>;
  let mockUserService: jasmine.SpyObj<UserService>;
  let mockDialogRef: jasmine.SpyObj<MatDialogRef<UserImportDialogComponent>>;

  beforeEach(async () => {
    mockPlanningCenterService = jasmine.createSpyObj('PlanningCenterService', ['searchPeople']);
    mockUserService = jasmine.createSpyObj('UserService', ['importUserFromPlanningCenter']);
    mockDialogRef = jasmine.createSpyObj('MatDialogRef', ['close']);

    await TestBed.configureTestingModule({
      declarations: [UserImportDialogComponent],
      imports: [
        ReactiveFormsModule,
        MatDialogModule,
        MatAutocompleteModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatButtonModule,
        MatSnackBarModule,
        NoopAnimationsModule
      ],
      providers: [
        { provide: PlanningCenterService, useValue: mockPlanningCenterService },
        { provide: UserService, useValue: mockUserService },
        { provide: MatDialogRef, useValue: mockDialogRef }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserImportDialogComponent);
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


