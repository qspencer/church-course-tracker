import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { User, UserProfileUpdate, ChangePasswordRequest, UserPreference } from '../../models';
import { LoggerService } from '../../services/logger.service';

@Component({
    selector: 'app-profile',
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss'],
    standalone: false
})
export class ProfileComponent implements OnInit {
  profileForm: FormGroup;
  passwordForm: FormGroup;
  preferencesForm: FormGroup;
  
  currentUser: User | null = null;
  preferences: UserPreference | null = null;
  
  isLoading = false;
  isSavingProfile = false;
  isChangingPassword = false;
  isSavingPreferences = false;
  
  hideCurrentPassword = true;
  hideNewPassword = true;
  hideConfirmPassword = true;
  
  selectedTab = 0;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {
    this.profileForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      full_name: ['', [Validators.required]]
    });

    this.passwordForm = this.fb.group({
      current_password: ['', [Validators.required, Validators.minLength(8)]],
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', [Validators.required, Validators.minLength(8)]]
    }, { validators: this.passwordMatchValidator });

    this.preferencesForm = this.fb.group({
      email_notifications: [true],
      course_updates: [true],
      system_announcements: [true]
    });
  }

  ngOnInit(): void {
    this.loadUserData();
  }

  loadUserData(): void {
    this.currentUser = this.authService.getCurrentUser();
    if (this.currentUser) {
      this.profileForm.patchValue({
        username: this.currentUser.username || '',
        email: this.currentUser.email,
        full_name: this.currentUser.full_name
      });
    }

    this.loadPreferences();
  }

  loadPreferences(): void {
    this.isLoading = true;
    this.userService.getUserPreferences().subscribe({
      next: (prefs) => {
        this.preferences = prefs;
        this.preferencesForm.patchValue({
          email_notifications: prefs.email_notifications,
          course_updates: prefs.course_updates,
          system_announcements: prefs.system_announcements
        });
        this.isLoading = false;
      },
      error: (error) => {
        this.logger.error('Error loading preferences', error, {
          component: 'ProfileComponent',
          action: 'loadPreferences',
          userId: this.currentUser?.id
        });
        this.snackBar.open('Error loading preferences', 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    });
  }

  onSaveProfile(): void {
    if (this.profileForm.valid) {
      this.isSavingProfile = true;
      const profileUpdate: UserProfileUpdate = this.profileForm.value;
      
      this.userService.updateCurrentUserProfile(profileUpdate).subscribe({
        next: (updatedUser) => {
          this.currentUser = updatedUser;
          this.authService.getCurrentUser(); // Refresh current user in auth service
          this.snackBar.open('Profile updated successfully', 'Close', { duration: 3000 });
          this.isSavingProfile = false;
        },
        error: (error) => {
          this.logger.error('Error updating profile', error, {
            component: 'ProfileComponent',
            action: 'onSaveProfile',
            userId: this.currentUser?.id
          });
          const errorMessage = error?.error?.detail || 'Error updating profile';
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          this.isSavingProfile = false;
        }
      });
    }
  }

  onChangePassword(): void {
    if (this.passwordForm.valid) {
      this.isChangingPassword = true;
      const passwordData: ChangePasswordRequest = this.passwordForm.value;
      
      this.userService.changePassword(passwordData).subscribe({
        next: (response) => {
          this.snackBar.open(response.message || 'Password changed successfully', 'Close', { duration: 3000 });
          this.passwordForm.reset();
          this.isChangingPassword = false;
        },
        error: (error) => {
          this.logger.error('Error changing password', error, {
            component: 'ProfileComponent',
            action: 'onChangePassword',
            userId: this.currentUser?.id
          });
          const errorMessage = error?.error?.detail || 'Error changing password';
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          this.isChangingPassword = false;
        }
      });
    }
  }

  onSavePreferences(): void {
    if (this.preferencesForm.valid) {
      this.isSavingPreferences = true;
      const preferencesUpdate = this.preferencesForm.value;
      
      this.userService.updateUserPreferences(preferencesUpdate).subscribe({
        next: (updatedPrefs) => {
          this.preferences = updatedPrefs;
          this.snackBar.open('Preferences updated successfully', 'Close', { duration: 3000 });
          this.isSavingPreferences = false;
        },
        error: (error) => {
          this.logger.error('Error updating preferences', error, {
            component: 'ProfileComponent',
            action: 'onSavePreferences',
            userId: this.currentUser?.id
          });
          const errorMessage = error?.error?.detail || 'Error updating preferences';
          this.snackBar.open(errorMessage, 'Close', { duration: 5000 });
          this.isSavingPreferences = false;
        }
      });
    }
  }

  passwordMatchValidator(form: FormGroup) {
    const newPassword = form.get('new_password');
    const confirmPassword = form.get('confirm_password');
    
    if (newPassword && confirmPassword && newPassword.value !== confirmPassword.value) {
      confirmPassword.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    } else {
      if (confirmPassword) {
        confirmPassword.setErrors(null);
      }
      return null;
    }
  }

  getErrorMessage(formGroup: FormGroup, fieldName: string): string {
    const field = formGroup.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName.replace('_', ' ')} is required`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email';
    }
    if (field?.hasError('minlength')) {
      return `${fieldName.replace('_', ' ')} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    if (field?.hasError('passwordMismatch')) {
      return 'Passwords do not match';
    }
    return '';
  }
}

