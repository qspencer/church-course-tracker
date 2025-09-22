import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { of, throwError } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { UserDialogComponent, UserDialogData } from './user-dialog.component';
import { UserService } from '../../../services/user.service';
import { User, UserCreate, UserUpdate } from '../../../models';

describe('UserDialogComponent', () => {
  let component: UserDialogComponent;
  let fixture: ComponentFixture<UserDialogComponent>;
  let userService: jasmine.SpyObj<UserService>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<UserDialogComponent>>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    role: 'staff',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };

  const createDialogData = (mode: 'create' | 'edit', user?: User): UserDialogData => ({
    mode,
    user
  });

  beforeEach(async () => {
    const userServiceSpy = jasmine.createSpyObj('UserService', ['createUser', 'updateUser']);
    const dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        NoopAnimationsModule,
        MatDialogModule,
        MatFormFieldModule,
        MatInputModule,
        MatSelectModule,
        MatButtonModule,
        MatCheckboxModule,
        MatIconModule
      ],
      declarations: [UserDialogComponent],
      providers: [
        { provide: UserService, useValue: userServiceSpy },
        { provide: MatDialogRef, useValue: dialogRefSpy },
        { provide: MatSnackBar, useValue: snackBarSpy },
        { provide: MAT_DIALOG_DATA, useValue: createDialogData('create') }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(UserDialogComponent);
    component = fixture.componentInstance;
    userService = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
    dialogRef = TestBed.inject(MatDialogRef) as jasmine.SpyObj<MatDialogRef<UserDialogComponent>>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should initialize form for create mode', () => {
      component.data = createDialogData('create');
      component.ngOnInit();

      expect(component.userForm.get('password')?.hasError('required')).toBe(true);
    });

    it('should populate form for edit mode', () => {
      component.data = createDialogData('edit', mockUser);
      component.ngOnInit();

      expect(component.userForm.get('email')?.value).toBe(mockUser.email);
      expect(component.userForm.get('full_name')?.value).toBe(mockUser.full_name);
      expect(component.userForm.get('role')?.value).toBe(mockUser.role);
      expect(component.userForm.get('is_active')?.value).toBe(mockUser.is_active);
      expect(component.userForm.get('password')?.value).toBe('');
    });
  });

  describe('onSubmit', () => {
    beforeEach(() => {
      component.userForm.patchValue({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff',
        password: 'password123'
      });
    });

    it('should create user successfully in create mode', () => {
      component.data = createDialogData('create');
      userService.createUser.and.returnValue(of(mockUser));

      component.onSubmit();

      expect(userService.createUser).toHaveBeenCalledWith(jasmine.objectContaining({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff',
        password: 'password123'
      }));
      expect(snackBar.open).toHaveBeenCalledWith(
        'User created successfully',
        'Close',
        { duration: 3000 }
      );
      expect(dialogRef.close).toHaveBeenCalledWith(mockUser);
    });

    it('should update user successfully in edit mode', () => {
      component.data = createDialogData('edit', mockUser);
      userService.updateUser.and.returnValue(of(mockUser));

      component.onSubmit();

      expect(userService.updateUser).toHaveBeenCalledWith(mockUser.id, jasmine.objectContaining({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff'
      }));
      expect(snackBar.open).toHaveBeenCalledWith(
        'User updated successfully',
        'Close',
        { duration: 3000 }
      );
      expect(dialogRef.close).toHaveBeenCalledWith(mockUser);
    });

    it('should include password in update when provided', () => {
      component.data = createDialogData('edit', mockUser);
      component.userForm.patchValue({ password: 'newpassword123' });
      userService.updateUser.and.returnValue(of(mockUser));

      component.onSubmit();

      expect(userService.updateUser).toHaveBeenCalledWith(mockUser.id, jasmine.objectContaining({
        password: 'newpassword123'
      }));
    });

    it('should not include password in update when not provided', () => {
      component.data = createDialogData('edit', mockUser);
      component.userForm.patchValue({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff',
        password: '' // Empty password
      });
      userService.updateUser.and.returnValue(of(mockUser));

      component.onSubmit();

      expect(userService.updateUser).toHaveBeenCalled();
      const updateCall = userService.updateUser.calls.mostRecent().args[1] as UserUpdate;
      expect(updateCall.password).toBeUndefined();
    });

    it('should handle error when creating user fails', () => {
      component.data = createDialogData('create');
      const error = new Error('Failed to create user');
      userService.createUser.and.returnValue(throwError(() => error));

      component.onSubmit();

      expect(snackBar.open).toHaveBeenCalledWith(
        'Error creating user',
        'Close',
        { duration: 3000 }
      );
      expect(dialogRef.close).not.toHaveBeenCalled();
    });

    it('should handle error when updating user fails', () => {
      component.data = createDialogData('edit', mockUser);
      const error = new Error('Failed to update user');
      userService.updateUser.and.returnValue(throwError(() => error));

      component.onSubmit();

      expect(snackBar.open).toHaveBeenCalledWith(
        'Error updating user',
        'Close',
        { duration: 3000 }
      );
      expect(dialogRef.close).not.toHaveBeenCalled();
    });

    it('should not submit when form is invalid', () => {
      component.userForm.patchValue({
        email: 'invalid-email',
        full_name: '',
        password: '123' // Too short
      });

      component.onSubmit();

      expect(userService.createUser).not.toHaveBeenCalled();
      expect(userService.updateUser).not.toHaveBeenCalled();
    });
  });

  describe('onCancel', () => {
    it('should close dialog without result', () => {
      component.onCancel();
      expect(dialogRef.close).toHaveBeenCalled();
    });
  });

  describe('getErrorMessage', () => {
    beforeEach(() => {
      component.ngOnInit();
    });

    it('should return required error message', () => {
      component.userForm.get('email')?.setValue('');
      component.userForm.get('email')?.markAsTouched();

      const error = component.getErrorMessage('email');
      expect(error).toBe('email is required');
    });

    it('should return email validation error message', () => {
      component.userForm.get('email')?.setValue('invalid-email');
      component.userForm.get('email')?.markAsTouched();

      const error = component.getErrorMessage('email');
      expect(error).toBe('Please enter a valid email address');
    });

    it('should return minlength error message', () => {
      component.userForm.get('full_name')?.setValue('A');
      component.userForm.get('full_name')?.markAsTouched();

      const error = component.getErrorMessage('full_name');
      expect(error).toBe('full_name must be at least 2 characters long');
    });

    it('should return empty string for valid field', () => {
      component.userForm.get('email')?.setValue('valid@example.com');
      component.userForm.get('email')?.markAsTouched();

      const error = component.getErrorMessage('email');
      expect(error).toBe('');
    });
  });

  describe('form validation', () => {
    it('should be invalid with empty required fields', () => {
      component.ngOnInit();
      expect(component.userForm.valid).toBe(false);
    });

    it('should be valid with all required fields filled', () => {
      component.ngOnInit();
      component.userForm.patchValue({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff',
        password: 'password123'
      });
      expect(component.userForm.valid).toBe(true);
    });

    it('should be invalid with invalid email', () => {
      component.ngOnInit();
      component.userForm.patchValue({
        email: 'invalid-email',
        full_name: 'Test User',
        role: 'staff',
        password: 'password123'
      });
      expect(component.userForm.valid).toBe(false);
    });

    it('should be invalid with short password', () => {
      component.ngOnInit();
      component.userForm.patchValue({
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'staff',
        password: '123'
      });
      expect(component.userForm.valid).toBe(false);
    });
  });
});
