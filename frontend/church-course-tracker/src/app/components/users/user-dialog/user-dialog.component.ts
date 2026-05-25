import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogTitle, MatDialogContent, MatDialogActions } from '@angular/material/dialog';
import { finalize } from 'rxjs/operators';
import { User, UserCreate, UserUpdate } from '../../../models';
import { UserService } from '../../../services/user.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoggerService } from '../../../services/logger.service';
import { CdkScrollable } from '@angular/cdk/scrolling';
import { MatFormField, MatLabel, MatError, MatHint, MatSuffix } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatIconButton, MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

export interface UserDialogData {
  mode: 'create' | 'edit';
  user?: User;
}

@Component({
    selector: 'app-user-dialog',
    templateUrl: './user-dialog.component.html',
    styleUrls: ['./user-dialog.component.scss'],
    imports: [MatDialogTitle, CdkScrollable, MatDialogContent, ReactiveFormsModule, MatFormField, MatLabel, MatInput, MatError, MatHint, MatSelect, MatOption, MatIconButton, MatSuffix, MatIcon, MatCheckbox, MatDialogActions, MatButton, MatProgressSpinner]
})
export class UserDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private snackBar = inject(MatSnackBar);
  dialogRef = inject<MatDialogRef<UserDialogComponent>>(MatDialogRef);
  data = inject<UserDialogData>(MAT_DIALOG_DATA);
  private logger = inject(LoggerService);

  userForm: FormGroup;
  isSubmitting = false;
  isSubmitted = false; // Track if form has been submitted
  hidePassword = true;

  constructor() {
    this.userForm = this.createForm();
  }

  ngOnInit(): void {
    if (this.data.mode === 'edit' && this.data.user) {
      this.populateForm(this.data.user);
    }
  }

  createForm(): FormGroup {
    const form = this.fb.group({
      username: [''],
      email: ['', [Validators.required, Validators.email]],
      full_name: ['', [Validators.required, Validators.minLength(2)]],
      role: ['staff', [Validators.required]],
      is_active: [true],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });

    // For edit mode, password is optional
    if (this.data.mode === 'edit') {
      form.get('password')?.setValidators([Validators.minLength(8)]);
    }

    return form;
  }

  populateForm(user: User): void {
    this.userForm.patchValue({
      username: user.username || '',
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active,
      password: '' // Don't populate password
    });
  }

  onSubmit(): void {
    // Mark form as submitted to show validation errors
    this.isSubmitted = true;

    if (this.isSubmitting || !this.userForm.valid) {
      return;
    }

    this.isSubmitting = true;
    const formValue = this.userForm.value;

    if (this.data.mode === 'create') {
      const userCreate: UserCreate = {
        username: formValue.username || undefined,
        email: formValue.email,
        full_name: formValue.full_name,
        role: formValue.role,
        is_active: formValue.is_active,
        password: formValue.password
      };

      this.userService.createUser(userCreate)
        .pipe(finalize(() => this.isSubmitting = false))
        .subscribe({
          next: (user) => {
            this.snackBar.open('User created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(user);
          },
          error: (error) => {
            this.logger.error('Error creating user', error, { component: 'UserDialogComponent', action: 'createUser' });
            this.snackBar.open('Error creating user', 'Close', { duration: 5000 });
          }
        });
    } else {
      const userUpdate: UserUpdate = {
        username: formValue.username || undefined,
        email: formValue.email,
        full_name: formValue.full_name,
        role: formValue.role,
        is_active: formValue.is_active
      };

      // Only include password if it's provided
      if (formValue.password) {
        userUpdate.password = formValue.password;
      }

      this.userService.updateUser(this.data.user!.id, userUpdate)
        .pipe(finalize(() => this.isSubmitting = false))
        .subscribe({
          next: (user) => {
            this.snackBar.open('User updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(user);
          },
          error: (error) => {
            this.logger.error('Error updating user', error, { component: 'UserDialogComponent', action: 'updateUser', userId: this.data.user!.id });
            this.snackBar.open('Error updating user', 'Close', { duration: 5000 });
          }
        });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(fieldName: string): string {
    const field = this.userForm.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email address';
    }
    if (field?.hasError('minlength')) {
      const requiredLength = field.errors?.['minlength']?.requiredLength;
      return `${fieldName} must be at least ${requiredLength} characters long`;
    }
    return '';
  }

  shouldShowError(fieldName: string): boolean {
    const field = this.userForm.get(fieldName);
    // Only show error if field is invalid AND (touched OR form submitted)
    return !!(field && field.invalid && (field.touched || this.isSubmitted));
  }
}
