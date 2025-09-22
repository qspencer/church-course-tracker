import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { User, UserCreate, UserUpdate } from '../../../models';
import { UserService } from '../../../services/user.service';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface UserDialogData {
  mode: 'create' | 'edit';
  user?: User;
}

@Component({
  selector: 'app-user-dialog',
  templateUrl: './user-dialog.component.html',
  styleUrls: ['./user-dialog.component.scss']
})
export class UserDialogComponent implements OnInit {
  userForm: FormGroup;
  isSubmitting = false;
  hidePassword = true;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<UserDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: UserDialogData
  ) {
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
    if (this.userForm.valid) {
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

        this.userService.createUser(userCreate).subscribe({
          next: (user) => {
            this.snackBar.open('User created successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(user);
          },
          error: (error) => {
            console.error('Error creating user:', error);
            this.snackBar.open('Error creating user', 'Close', { duration: 3000 });
            this.isSubmitting = false;
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

        this.userService.updateUser(this.data.user!.id, userUpdate).subscribe({
          next: (user) => {
            this.snackBar.open('User updated successfully', 'Close', { duration: 3000 });
            this.dialogRef.close(user);
          },
          error: (error) => {
            console.error('Error updating user:', error);
            this.snackBar.open('Error updating user', 'Close', { duration: 3000 });
            this.isSubmitting = false;
          }
        });
      }
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
}
