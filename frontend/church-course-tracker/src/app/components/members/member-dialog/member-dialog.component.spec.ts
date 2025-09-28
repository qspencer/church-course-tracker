import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { MemberDialogComponent } from './member-dialog.component';
import { MemberService } from '../../../services/member.service';
import { Person } from '../../../models';

describe('MemberDialogComponent', () => {
  let component: MemberDialogComponent;
  let fixture: ComponentFixture<MemberDialogComponent>;
  let memberServiceSpy: jasmine.SpyObj<MemberService>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<MemberDialogComponent>>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

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

  const mockDialogData = {
    member: mockMember
  };

  beforeEach(async () => {
    const memberSpy = jasmine.createSpyObj('MemberService', ['createMember', 'updateMember']);
    const matDialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const matSnackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);
    
    // Set up default return values for service methods
    memberSpy.createMember.and.returnValue(of(mockMember));
    memberSpy.updateMember.and.returnValue(of(mockMember));

    await TestBed.configureTestingModule({
      declarations: [MemberDialogComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule
      ],
      providers: [
        { provide: MemberService, useValue: memberSpy },
        { provide: MatDialogRef, useValue: matDialogRefSpy },
        { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
        { provide: MatSnackBar, useValue: matSnackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MemberDialogComponent);
    component = fixture.componentInstance;
    memberServiceSpy = TestBed.inject(MemberService) as jasmine.SpyObj<MemberService>;
    dialogRefSpy = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<MemberDialogComponent>>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
    
    // Initialize component properly
    component.ngOnInit();
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize in editing mode when member provided', () => {
    // Component should already be initialized in beforeEach
    expect(component.isEditing).toBe(true);
    expect(component.data.member).toEqual(mockMember);
  });

  describe('form initialization', () => {
    it('should initialize form with validators', () => {
      fixture.detectChanges();
      
      // Clear the fields and mark as touched to trigger validation
      component.memberForm.get('first_name')?.setValue('');
      component.memberForm.get('last_name')?.setValue('');
      component.memberForm.get('first_name')?.markAsTouched();
      component.memberForm.get('last_name')?.markAsTouched();
      
      expect(component.memberForm.get('first_name')?.hasError('required')).toBe(true);
      expect(component.memberForm.get('last_name')?.hasError('required')).toBe(true);
    });

  it('should patch form values when editing', () => {
    // Component should already be initialized in beforeEach
    expect(component.isEditing).toBe(true);
    expect(component.data.member).toEqual(mockMember);
    
    expect(component.memberForm.get('first_name')?.value).toBe(mockMember.first_name);
    expect(component.memberForm.get('last_name')?.value).toBe(mockMember.last_name);
    expect(component.memberForm.get('email')?.value).toBe(mockMember.email);
    expect(component.memberForm.get('phone')?.value).toBe(mockMember.phone);
    expect(component.memberForm.get('planning_center_id')?.value).toBe(mockMember.planning_center_id);
  });
  });

  describe('onSubmit for editing', () => {
    it('should update member when editing', () => {
      // Component should already be initialized in global beforeEach
      // Verify we're in editing mode
      expect(component.isEditing).toBe(true);
      
      // Then patch the form with updated values
      component.memberForm.patchValue({
        first_name: 'John',
        last_name: 'Updated',
        email: 'john.updated@example.com',
        phone: '999-888-7777',
        planning_center_id: 'pc456'
      });
      memberServiceSpy.updateMember.and.returnValue(of(mockMember));

      component.onSubmit();

      expect(memberServiceSpy.updateMember).toHaveBeenCalledWith(1, {
        first_name: 'John',
        last_name: 'Updated',
        email: 'john.updated@example.com',
        phone: '999-888-7777',
        planning_center_id: 'pc456'
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Member updated successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockMember);
    });

    it('should handle update error', () => {
      // Component should already be initialized in global beforeEach
      memberServiceSpy.updateMember.and.returnValue(throwError(() => new Error('Update error')));
      const consoleErrorSpy = spyOn(console, 'error');

      component.onSubmit();

      expect(consoleErrorSpy).toHaveBeenCalledWith('Error updating member:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('onSubmit for creating', () => {
    beforeEach(() => {
      // Reset to create mode
      component.data.member = null;
      component.isEditing = false;
      component.memberForm.patchValue({
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        phone: '555-444-3333',
        planning_center_id: ''
      });
    });

    it('should create member when not editing', () => {
      memberServiceSpy.createMember.and.returnValue(of(mockMember));

      component.onSubmit();

      expect(memberServiceSpy.createMember).toHaveBeenCalledWith({
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
        phone: '555-444-3333',
        planning_center_id: ''
      });
      expect(snackBarSpy.open).toHaveBeenCalledWith('Member created successfully', 'Close', { duration: 3000 });
      expect(dialogRefSpy.close).toHaveBeenCalledWith(mockMember);
    });

    it('should handle create error', () => {
      memberServiceSpy.createMember.and.returnValue(throwError(() => new Error('Create error')));
      spyOn(console, 'error');

      component.onSubmit();

      expect(console.error).toHaveBeenCalledWith('Error creating member:', jasmine.any(Error));
      expect(component.isLoading).toBe(false);
    });
  });

  describe('form validation', () => {
    it('should not submit if form is invalid', () => {
      component.memberForm.patchValue({
        first_name: '',
        last_name: '',
        email: 'invalid-email'
      });

      component.onSubmit();

      expect(memberServiceSpy.createMember).not.toHaveBeenCalled();
      expect(memberServiceSpy.updateMember).not.toHaveBeenCalled();
    });

    it('should validate email format', () => {
      component.memberForm.patchValue({
        email: 'invalid-email'
      });

      expect(component.memberForm.get('email')?.hasError('email')).toBe(true);
    });
  });

  describe('getErrorMessage', () => {
    it('should return required error message', () => {
      // Set the field to empty and mark as touched to trigger validation
      component.memberForm.get('first_name')?.setValue('');
      component.memberForm.get('first_name')?.markAsTouched();
      const message = component.getErrorMessage('first_name');
      expect(message).toBe('first name is required');
    });

    it('should return email error message', () => {
      component.memberForm.get('email')?.setValue('invalid-email');
      const message = component.getErrorMessage('email');
      expect(message).toBe('Please enter a valid email address');
    });

    it('should return minlength error message', () => {
      component.memberForm.get('first_name')?.setValue('a');
      const message = component.getErrorMessage('first_name');
      expect(message).toBe('first name must be at least 2 characters');
    });
  });

  describe('onCancel', () => {
    it('should close dialog without data', () => {
      component.onCancel();
      expect(dialogRefSpy.close).toHaveBeenCalledWith();
    });
  });

  describe('template rendering', () => {
    let templateFixture: ComponentFixture<MemberDialogComponent>;
    let templateComponent: MemberDialogComponent;

    beforeEach(async () => {
      // Create a fresh component instance for template tests
      // Reset TestBed to ensure clean state
      TestBed.resetTestingModule();
      
      await TestBed.configureTestingModule({
        declarations: [MemberDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule
        ],
        providers: [
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: mockDialogData },
          { provide: MatSnackBar, useValue: snackBarSpy }
        ]
      }).compileComponents();

      templateFixture = TestBed.createComponent(MemberDialogComponent);
      templateComponent = templateFixture.componentInstance;
      templateComponent.ngOnInit();
      templateFixture.detectChanges();
    });

    it('should display correct title for editing', () => {
      // Ensure component is in editing mode
      expect(templateComponent.isEditing).toBe(true);
      expect(templateComponent.data.member).toEqual(mockMember);
      const compiled = templateFixture.nativeElement;
      expect(compiled.querySelector('h2').textContent.trim()).toBe('Edit Member');
    });

    it('should display correct button text for editing', () => {
      // Ensure component is in editing mode
      expect(templateComponent.isEditing).toBe(true);
      expect(templateComponent.data.member).toEqual(mockMember);
      const compiled = templateFixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton.textContent.trim()).toBe('Update');
    });

    it('should show loading spinner when loading', () => {
      templateComponent.isLoading = true;
      templateFixture.detectChanges();

      const compiled = templateFixture.nativeElement;
      expect(compiled.querySelector('mat-spinner')).toBeTruthy();
    });
  });

  describe('create mode', () => {
    let createFixture: ComponentFixture<MemberDialogComponent>;
    let createComponent: MemberDialogComponent;

    beforeEach(async () => {
      // Reset TestBed to allow reconfiguration
      TestBed.resetTestingModule();
      
      // Create a new test module for create mode
      await TestBed.configureTestingModule({
        declarations: [MemberDialogComponent],
        imports: [
          ReactiveFormsModule,
          BrowserAnimationsModule,
          MatDialogModule,
          MatFormFieldModule,
          MatInputModule,
          MatButtonModule,
          MatIconModule,
          MatProgressSpinnerModule
        ],
        providers: [
          { provide: MemberService, useValue: memberServiceSpy },
          { provide: MatDialogRef, useValue: dialogRefSpy },
          { provide: MAT_DIALOG_DATA, useValue: { member: null } },
          { provide: MatSnackBar, useValue: snackBarSpy }
        ]
      }).compileComponents();

      createFixture = TestBed.createComponent(MemberDialogComponent);
      createComponent = createFixture.componentInstance;
      createFixture.detectChanges();
    });


    it('should initialize in create mode', () => {
      expect(createComponent.isEditing).toBe(false);
    });

    it('should display correct title for creating', () => {
      const compiled = createFixture.nativeElement;
      expect(compiled.querySelector('h2').textContent.trim()).toBe('Add New Member');
    });

    it('should display correct button text for creating', () => {
      const compiled = createFixture.nativeElement;
      const submitButton = compiled.querySelector('button[color="primary"]');
      expect(submitButton.textContent.trim()).toBe('Create');
    });
  });
});
