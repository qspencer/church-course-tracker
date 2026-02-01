import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoggerService } from '../../services/logger.service';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss']
})
export class AuthComponent implements OnInit {
  loginForm: FormGroup;
  registerForm: FormGroup;
  isLoginMode = true;
  isLoading = false;
  hidePassword = true;
  lockoutMessage: string | null = null;
  remainingAttempts: number | null = null;
  isAccountLocked = false;
  lockoutUntil: Date | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar,
    private logger: LoggerService
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.registerForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      full_name: ['', [Validators.required]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Check if already authenticated
    this.authService.isAuthenticated$.subscribe(isAuth => {
      if (isAuth) {
        this.router.navigate(['/dashboard']);
      }
    });
  }

  switchMode(): void {
    this.isLoginMode = !this.isLoginMode;
  }

  onLogin(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      const credentials = this.loginForm.value;
      
      this.authService.login(credentials).subscribe({
        next: () => {
          this.isLoading = false;
          this.snackBar.open('Login successful!', 'Close', { duration: 3000 });
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.isLoading = false;
          this.logger.error('Login error', error, { component: 'AuthComponent', action: 'login', username: credentials.username });
          
          // Handle account lockout (423 status)
          if (error?.status === 423) {
            this.isAccountLocked = true;
            const message = error?.error?.detail || 'Account locked due to too many failed login attempts.';
            this.lockoutMessage = message;
            
            // Extract remaining time from error message
            const timeMatch = message.match(/(\d+)\s+minute/);
            if (timeMatch) {
              const minutes = parseInt(timeMatch[1], 10);
              this.lockoutUntil = new Date(Date.now() + minutes * 60 * 1000);
            }
            
            this.snackBar.open(message, 'Close', {
              duration: 10000,
              horizontalPosition: 'end',
              verticalPosition: 'top',
              panelClass: ['error-snackbar', 'lockout-snackbar']
            });
            return;
          }
          
          // Reset lockout state if not locked
          this.isAccountLocked = false;
          this.lockoutMessage = null;
          this.lockoutUntil = null;
          
          // Show user-friendly error message
          let errorMessage = 'Login failed. Please check your credentials and try again.';
          
          // Extract error message from API response if available
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
            
            // Extract remaining attempts from error message
            const attemptsMatch = errorMessage.match(/(\d+)\s+attempt\(s\)\s+remaining/);
            if (attemptsMatch) {
              this.remainingAttempts = parseInt(attemptsMatch[1], 10);
            } else {
              this.remainingAttempts = null;
            }
          } else if (error?.status === 401) {
            errorMessage = 'Incorrect username or password. Please try again.';
            this.remainingAttempts = null;
          } else if (error?.status === 0 || error?.status === undefined) {
            errorMessage = 'Unable to connect to the server. Please check your internet connection.';
            this.remainingAttempts = null;
          } else if (error?.status >= 500) {
            errorMessage = 'Server error. Please try again later.';
            this.remainingAttempts = null;
          }
          
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  onRegister(): void {
    if (this.registerForm.valid) {
      const formValue = this.registerForm.value;
      
      if (formValue.password !== formValue.confirmPassword) {
        this.snackBar.open('Passwords do not match', 'Close', { duration: 3000 });
        return;
      }

      this.isLoading = true;
      const userData = {
        username: formValue.username,
        email: formValue.email,
        full_name: formValue.full_name,
        password: formValue.password
      };

      this.authService.register(userData).subscribe({
        next: () => {
          this.isLoading = false;
          this.snackBar.open('Registration successful! Please login.', 'Close', { duration: 3000 });
          this.isLoginMode = true;
          this.registerForm.reset();
        },
        error: (error) => {
          this.isLoading = false;
          this.logger.error('Registration error', error, { component: 'AuthComponent', action: 'register', username: userData.username });
          
          // Show user-friendly error message
          let errorMessage = 'Registration failed. Please try again.';
          
          // Extract error message from API response if available
          if (error?.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error?.status === 400) {
            errorMessage = 'Invalid registration data. Please check your input.';
          } else if (error?.status === 409) {
            errorMessage = 'Username or email already exists. Please use different credentials.';
          } else if (error?.status === 0 || error?.status === undefined) {
            errorMessage = 'Unable to connect to the server. Please check your internet connection.';
          } else if (error?.status >= 500) {
            errorMessage = 'Server error. Please try again later.';
          }
          
          this.snackBar.open(errorMessage, 'Close', {
            duration: 5000,
            horizontalPosition: 'end',
            verticalPosition: 'top',
            panelClass: ['error-snackbar']
          });
        }
      });
    }
  }

  getErrorMessage(formGroup: FormGroup, fieldName: string): string {
    const field = formGroup.get(fieldName);
    if (field?.hasError('required')) {
      return `${fieldName} is required`;
    }
    if (field?.hasError('email')) {
      return 'Please enter a valid email';
    }
    if (field?.hasError('minlength')) {
      return `${fieldName} must be at least ${field.errors?.['minlength'].requiredLength} characters`;
    }
    return '';
  }
}
