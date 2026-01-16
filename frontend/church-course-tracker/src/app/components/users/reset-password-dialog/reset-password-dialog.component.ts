import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { finalize } from 'rxjs/operators';
import { UserService } from '../../../services/user.service';
import { LoggerService } from '../../../services/logger.service';

export interface ResetPasswordDialogData {
  user: {
    id: number;
    full_name: string;
    email: string;
  };
}

@Component({
  selector: 'app-reset-password-dialog',
  templateUrl: './reset-password-dialog.component.html',
  styleUrls: ['./reset-password-dialog.component.scss']
})
export class ResetPasswordDialogComponent {
  passwordForm: FormGroup;
  isSubmitting = false;
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ResetPasswordDialogComponent>,
    private userService: UserService,
    private snackBar: MatSnackBar,
    @Inject(MAT_DIALOG_DATA) public data: ResetPasswordDialogData,
    private logger: LoggerService
  ) {
    this.passwordForm = this.fb.group({
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password');
    const confirmPassword = form.get('confirmPassword');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit(): void {
    if (this.isSubmitting || !this.passwordForm.valid) {
      return;
    }

    this.isSubmitting = true;
    const newPassword = this.passwordForm.get('password')?.value;

    this.userService.updateUser(this.data.user.id, { password: newPassword })
      .pipe(finalize(() => this.isSubmitting = false))
      .subscribe({
        next: () => {
          this.snackBar.open(`Password reset successfully for ${this.data.user.full_name}`, 'Close', {
            duration: 3000
          });
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.logger.error('Error resetting password', error, { component: 'ResetPasswordDialogComponent', action: 'resetPassword', userId: this.data.user.id });
          const message = error?.error?.detail || 'Failed to reset password';
          this.snackBar.open(message, 'Close', { duration: 5000 });
        }
      });
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }

  getErrorMessage(fieldName: string): string {
    const field = this.passwordForm.get(fieldName);
    if (field?.hasError('required')) {
      return 'This field is required';
    }
    if (field?.hasError('minlength')) {
      return 'Password must be at least 8 characters';
    }
    if (field?.hasError('passwordMismatch')) {
      return 'Passwords do not match';
    }
    return '';
  }
}
