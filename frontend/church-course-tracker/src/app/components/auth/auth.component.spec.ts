import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

// Angular Material
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AuthComponent } from './auth.component';
import { AuthService } from '../../services/auth.service';
import { User, LoginResponse } from '../../models';

describe('AuthComponent', () => {
  let component: AuthComponent;
  let fixture: ComponentFixture<AuthComponent>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let routerSpy: jasmine.SpyObj<Router>;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

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

  const mockLoginResponse: LoginResponse = {
    access_token: 'mock-token',
    token_type: 'Bearer',
    user: mockUser
  };

  beforeEach(async () => {
    const authSpy = jasmine.createSpyObj('AuthService', ['login', 'register'], {
      isAuthenticated$: of(false)
    });
    const routerSpyObj = jasmine.createSpyObj('Router', ['navigate']);
    const snackBarSpyObj = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [AuthComponent],
      imports: [
        ReactiveFormsModule,
        BrowserAnimationsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule
      ],
      providers: [
        { provide: AuthService, useValue: authSpy },
        { provide: Router, useValue: routerSpyObj },
        { provide: MatSnackBar, useValue: snackBarSpyObj }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AuthComponent);
    component = fixture.componentInstance;
    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    routerSpy = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  beforeEach(() => {
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize in login mode', () => {
    expect(component.isLoginMode).toBe(true);
  });

  it('should initialize forms with validators', () => {
    expect(component.loginForm.get('username')?.hasError('required')).toBe(true);
    expect(component.loginForm.get('password')?.hasError('required')).toBe(true);
    expect(component.registerForm.get('username')?.hasError('required')).toBe(true);
    expect(component.registerForm.get('email')?.hasError('required')).toBe(true);
    expect(component.registerForm.get('full_name')?.hasError('required')).toBe(true);
    expect(component.registerForm.get('password')?.hasError('required')).toBe(true);
  });

  describe('switchMode', () => {
    it('should toggle between login and register mode', () => {
      expect(component.isLoginMode).toBe(true);
      
      component.switchMode();
      expect(component.isLoginMode).toBe(false);
      
      component.switchMode();
      expect(component.isLoginMode).toBe(true);
    });
  });

  describe('onLogin', () => {
    beforeEach(() => {
      component.loginForm.patchValue({
        username: 'testuser',
        password: 'password123'
      });
    });

    it('should call authService.login with form values', () => {
      authServiceSpy.login.and.returnValue(of(mockLoginResponse));

      component.onLogin();

      expect(authServiceSpy.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123'
      });
    });

    it('should show success message and navigate on successful login', () => {
      authServiceSpy.login.and.returnValue(of(mockLoginResponse));

      component.onLogin();

      expect(snackBarSpy.open).toHaveBeenCalledWith('Login successful!', 'Close', { duration: 3000 });
      expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
      expect(component.isLoading).toBe(false);
    });

    it('should handle login error', () => {
      authServiceSpy.login.and.returnValue(throwError(() => new Error('Login failed')));

      component.onLogin();

      expect(component.isLoading).toBe(false);
    });

    it('should not submit if form is invalid', () => {
      component.loginForm.patchValue({
        username: '',
        password: ''
      });

      component.onLogin();

      expect(authServiceSpy.login).not.toHaveBeenCalled();
    });
  });

  describe('onRegister', () => {
    beforeEach(() => {
      component.registerForm.patchValue({
        username: 'newuser',
        email: 'new@example.com',
        full_name: 'New User',
        password: 'password123',
        confirmPassword: 'password123'
      });
    });

    it('should call authService.register with form values', () => {
      authServiceSpy.register.and.returnValue(of(mockUser));

      component.onRegister();

      expect(authServiceSpy.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@example.com',
        full_name: 'New User',
        password: 'password123'
      });
    });

    it('should show success message and switch to login mode', () => {
      authServiceSpy.register.and.returnValue(of(mockUser));

      component.onRegister();

      expect(snackBarSpy.open).toHaveBeenCalledWith('Registration successful! Please login.', 'Close', { duration: 3000 });
      expect(component.isLoginMode).toBe(true);
      expect(component.isLoading).toBe(false);
    });

    it('should show error if passwords do not match', () => {
      component.registerForm.patchValue({
        confirmPassword: 'different-password'
      });

      component.onRegister();

      expect(snackBarSpy.open).toHaveBeenCalledWith('Passwords do not match', 'Close', { duration: 3000 });
      expect(authServiceSpy.register).not.toHaveBeenCalled();
    });

    it('should handle registration error', () => {
      authServiceSpy.register.and.returnValue(throwError(() => new Error('Registration failed')));

      component.onRegister();

      expect(component.isLoading).toBe(false);
    });
  });

  describe('getErrorMessage', () => {
    it('should return required error message', () => {
      const message = component.getErrorMessage(component.loginForm, 'username');
      expect(message).toBe('username is required');
    });

    it('should return email error message', () => {
      component.registerForm.get('email')?.setValue('invalid-email');
      const message = component.getErrorMessage(component.registerForm, 'email');
      expect(message).toBe('Please enter a valid email');
    });

    it('should return minlength error message', () => {
      component.loginForm.get('password')?.setValue('123');
      const message = component.getErrorMessage(component.loginForm, 'password');
      expect(message).toBe('password must be at least 6 characters');
    });
  });

  describe('navigation on authentication', () => {
  it('should navigate to dashboard if already authenticated', fakeAsync(() => {
    // Set up the observable to emit true immediately
    authServiceSpy.isAuthenticated$ = of(true);
    
    // Initialize component
    component.ngOnInit();
    tick(); // Wait for the subscription to be processed
    fixture.detectChanges();

    expect(routerSpy.navigate).toHaveBeenCalledWith(['/dashboard']);
  }));
  });
});
