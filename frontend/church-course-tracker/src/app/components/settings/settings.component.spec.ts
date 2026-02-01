import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReactiveFormsModule } from '@angular/forms';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { of, throwError } from 'rxjs';

import { SettingsComponent } from './settings.component';
import { SettingsService } from '../../services/settings.service';
import { AuthService } from '../../services/auth.service';
import { SystemSetting, SystemSettingsByCategory, PlanningCenterConfig } from '../../models/settings.model';

describe('SettingsComponent', () => {
  let component: SettingsComponent;
  let fixture: ComponentFixture<SettingsComponent>;
  let settingsService: jasmine.SpyObj<SettingsService>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  const mockSettings: SystemSettingsByCategory = {
    system: [
      {
        id: 1,
        key: 'app_name',
        value: 'Church Course Tracker',
        category: 'system',
        data_type: 'string',
        description: 'Application name',
        is_sensitive: false,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: null,
        updated_by: null
      },
      {
        id: 2,
        key: 'debug_mode',
        value: 'false',
        category: 'system',
        data_type: 'boolean',
        description: 'Enable debug mode',
        is_sensitive: false,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: null,
        updated_by: null
      }
    ],
    security: [
      {
        id: 3,
        key: 'password_min_length',
        value: '8',
        category: 'security',
        data_type: 'integer',
        description: 'Minimum password length',
        is_sensitive: false,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: null,
        updated_by: null
      }
    ]
  };

  const mockPlanningCenterConfig: PlanningCenterConfig = {
    api_url: 'https://api.test.com',
    app_id: 'app123',
    secret: 'secret123',
    access_token: 'token123',
    max_events: 1000,
    cache_ttl_minutes: 10,
    use_mock: false
  };

  beforeEach(async () => {
    const settingsServiceSpy = jasmine.createSpyObj('SettingsService', [
      'getSettings',
      'getPlanningCenterConfig',
      'updateSettingsBatch',
      'updatePlanningCenterConfig'
    ]);
    settingsServiceSpy.getSettings.and.returnValue(of(mockSettings));
    settingsServiceSpy.getPlanningCenterConfig.and.returnValue(of(mockPlanningCenterConfig));
    settingsServiceSpy.updateSettingsBatch.and.returnValue(of([]));
    settingsServiceSpy.updatePlanningCenterConfig.and.returnValue(of({}));

    const authServiceSpy = jasmine.createSpyObj('AuthService', ['isAdmin']);
    authServiceSpy.isAdmin.and.returnValue(true);

    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      declarations: [SettingsComponent],
      imports: [
        ReactiveFormsModule,
        MatTabsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatSelectModule,
        MatCheckboxModule,
        MatProgressSpinnerModule,
        NoopAnimationsModule
      ],
      providers: [
        { provide: SettingsService, useValue: settingsServiceSpy },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SettingsComponent);
    component = fixture.componentInstance;
    settingsService = TestBed.inject(SettingsService) as jasmine.SpyObj<SettingsService>;
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load settings on init', () => {
    fixture.detectChanges();
    expect(settingsService.getSettings).toHaveBeenCalled();
    expect(component.settings).toEqual(mockSettings);
  });

  it('should redirect non-admin users', () => {
    authService.isAdmin.and.returnValue(false);
    fixture.detectChanges();
    expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
    expect(snackBar.open).toHaveBeenCalledWith('Access denied. Admin privileges required.', 'Close', { duration: 3000 });
  });

  it('should populate forms with settings data', () => {
    fixture.detectChanges();
    expect(component.systemForm.get('app_name')?.value).toBe('Church Course Tracker');
    expect(component.systemForm.get('debug_mode')?.value).toBe(false);
    expect(component.securityForm.get('password_min_length')?.value).toBe(8);
  });

  it('should change active category', () => {
    const securityIndex = component.categories.indexOf('security');
    component.onCategoryChange(securityIndex);
    expect(component.activeCategory).toBe('security');
    expect(component.activeCategoryIndex).toBe(securityIndex);
  });

  it('should save system settings', () => {
    fixture.detectChanges();
    // Set valid values for required fields
    component.systemForm.get('session_timeout_minutes')?.setValue(120);
    component.systemForm.get('max_upload_size_mb')?.setValue(10);
    component.systemForm.get('debug_mode')?.setValue(true);
    component.systemForm.get('debug_mode')?.markAsDirty();
    component.systemForm.updateValueAndValidity();
    
    component.saveCategory();
    
    expect(settingsService.updateSettingsBatch).toHaveBeenCalled();
    expect(snackBar.open).toHaveBeenCalledWith('System settings saved successfully', 'Close', { duration: 3000 });
  });

  it('should save Planning Center config', () => {
    fixture.detectChanges();
    component.activeCategory = 'planning_center';
    component.planningCenterForm.get('api_url')?.setValue('https://new.api.com');
    component.planningCenterForm.get('api_url')?.markAsDirty();
    
    component.saveCategory();
    
    expect(settingsService.updatePlanningCenterConfig).toHaveBeenCalled();
    expect(snackBar.open).toHaveBeenCalledWith('Planning Center settings saved successfully', 'Close', { duration: 3000 });
  });

  it('should not save if form is invalid', () => {
    fixture.detectChanges();
    component.systemForm.get('session_timeout_minutes')?.setValue(-1); // Invalid value
    component.systemForm.get('session_timeout_minutes')?.markAsDirty();
    
    component.saveCategory();
    
    expect(settingsService.updateSettingsBatch).not.toHaveBeenCalled();
    expect(snackBar.open).toHaveBeenCalledWith('Please fix validation errors', 'Close', { duration: 3000 });
  });

  it('should not save if no changes', () => {
    fixture.detectChanges();
    // Ensure form is valid but has no dirty fields
    component.systemForm.get('session_timeout_minutes')?.setValue(120);
    component.systemForm.get('max_upload_size_mb')?.setValue(10);
    component.systemForm.markAsPristine();
    component.systemForm.updateValueAndValidity();
    
    component.saveCategory();
    
    expect(settingsService.updateSettingsBatch).not.toHaveBeenCalled();
    expect(snackBar.open).toHaveBeenCalledWith('No changes to save', 'Close', { duration: 2000 });
  });

  it('should handle save errors', () => {
    fixture.detectChanges();
    // Set valid values for required fields
    component.systemForm.get('session_timeout_minutes')?.setValue(120);
    component.systemForm.get('max_upload_size_mb')?.setValue(10);
    component.systemForm.get('debug_mode')?.setValue(true);
    component.systemForm.get('debug_mode')?.markAsDirty();
    component.systemForm.updateValueAndValidity();
    
    settingsService.updateSettingsBatch.and.returnValue(throwError(() => new Error('Save failed')));
    
    component.saveCategory();
    
    expect(snackBar.open).toHaveBeenCalledWith('Error saving settings', 'Close', { duration: 3000 });
  });

  it('should cancel changes and reload', () => {
    fixture.detectChanges();
    component.systemForm.get('debug_mode')?.setValue(true);
    
    component.cancelChanges();
    
    expect(settingsService.getSettings).toHaveBeenCalledTimes(2); // Once on init, once on cancel
  });

  it('should toggle Planning Center secrets visibility', () => {
    expect(component.showPlanningCenterSecrets).toBe(false);
    component.togglePlanningCenterSecrets();
    expect(component.showPlanningCenterSecrets).toBe(true);
    component.togglePlanningCenterSecrets();
    expect(component.showPlanningCenterSecrets).toBe(false);
  });

  it('should mask sensitive values', () => {
    const masked = component.getMaskedValue('secret_value');
    expect(masked).toBe('•'.repeat(20));
    expect(component.getMaskedValue(null)).toBe('');
    expect(component.getMaskedValue(undefined)).toBe('');
  });

  // Negative test cases
  it('should handle network errors when loading settings', () => {
    settingsService.getSettings.and.returnValue(throwError(() => new Error('Network error')));
    fixture.detectChanges();
    
    expect(snackBar.open).toHaveBeenCalledWith(
      jasmine.stringContaining('Error'),
      'Close',
      { duration: 3000 }
    );
  });

  it('should handle timeout when loading settings', () => {
    settingsService.getSettings.and.returnValue(
      throwError(() => ({ status: 0, message: 'Timeout' }))
    );
    fixture.detectChanges();
    
    expect(snackBar.open).toHaveBeenCalled();
  });

  it('should handle 403 Forbidden when loading settings', () => {
    settingsService.getSettings.and.returnValue(
      throwError(() => ({ status: 403, message: 'Forbidden' }))
    );
    fixture.detectChanges();
    
    // Component shows error snackbar on 403, doesn't navigate
    // The navigation happens in ngOnInit if user is not admin, not in error handler
    expect(snackBar.open).toHaveBeenCalledWith(
      'Error loading settings',
      'Close',
      { duration: 3000 }
    );
  });

  it('should handle save errors with specific error message', () => {
    fixture.detectChanges();
    component.systemForm.get('session_timeout_minutes')?.setValue(120);
    component.systemForm.get('max_upload_size_mb')?.setValue(10);
    component.systemForm.get('debug_mode')?.setValue(true);
    component.systemForm.get('debug_mode')?.markAsDirty();
    component.systemForm.updateValueAndValidity();
    
    const error = { status: 500, message: 'Server error' };
    settingsService.updateSettingsBatch.and.returnValue(throwError(() => error));
    
    component.saveCategory();
    
    expect(snackBar.open).toHaveBeenCalledWith('Error saving settings', 'Close', { duration: 3000 });
  });

  it('should not save if form has validation errors', () => {
    fixture.detectChanges();
    // Set invalid values
    component.systemForm.get('session_timeout_minutes')?.setValue(-5);
    component.systemForm.get('max_upload_size_mb')?.setValue(-1);
    component.systemForm.get('session_timeout_minutes')?.markAsDirty();
    component.systemForm.get('max_upload_size_mb')?.markAsDirty();
    component.systemForm.updateValueAndValidity();
    
    component.saveCategory();
    
    expect(settingsService.updateSettingsBatch).not.toHaveBeenCalled();
    expect(snackBar.open).toHaveBeenCalledWith('Please fix validation errors', 'Close', { duration: 3000 });
  });

  // Edge case tests
  it('should handle empty settings response', () => {
    settingsService.getSettings.and.returnValue(of({}));
    fixture.detectChanges();
    
    expect(component.settings).toEqual({});
  });

  it('should handle settings with missing categories', () => {
    const partialSettings: SystemSettingsByCategory = {
      system: mockSettings['system']
      // Missing other categories
    };
    settingsService.getSettings.and.returnValue(of(partialSettings));
    fixture.detectChanges();
    
    expect(component.settings).toEqual(partialSettings);
  });

  it('should handle very long input values', () => {
    fixture.detectChanges();
    const longValue = 'a'.repeat(10000);
    component.systemForm.get('app_name')?.setValue(longValue);
    component.systemForm.get('app_name')?.markAsDirty();
    
    // Should handle without crashing
    expect(component.systemForm.get('app_name')?.value).toBe(longValue);
  });

  it('should handle special characters in input values', () => {
    fixture.detectChanges();
    const specialValue = "!@#$%^&*()_+-=[]{}|;':\",./<>?";
    component.systemForm.get('app_name')?.setValue(specialValue);
    component.systemForm.get('app_name')?.markAsDirty();
    
    expect(component.systemForm.get('app_name')?.value).toBe(specialValue);
  });

  it('should handle unicode characters in input values', () => {
    fixture.detectChanges();
    const unicodeValue = "测试 🎉 émoji ñoño";
    component.systemForm.get('app_name')?.setValue(unicodeValue);
    component.systemForm.get('app_name')?.markAsDirty();
    
    expect(component.systemForm.get('app_name')?.value).toBe(unicodeValue);
  });

  it('should handle boundary values for session timeout', () => {
    fixture.detectChanges();
    // Test minimum value
    component.systemForm.get('session_timeout_minutes')?.setValue(1);
    expect(component.systemForm.get('session_timeout_minutes')?.valid).toBe(true);
    
    // Test maximum value
    component.systemForm.get('session_timeout_minutes')?.setValue(1440); // 24 hours
    expect(component.systemForm.get('session_timeout_minutes')?.valid).toBe(true);
    
    // Test below minimum
    component.systemForm.get('session_timeout_minutes')?.setValue(0);
    expect(component.systemForm.get('session_timeout_minutes')?.valid).toBe(false);
    
    // Test above maximum
    component.systemForm.get('session_timeout_minutes')?.setValue(1441);
    expect(component.systemForm.get('session_timeout_minutes')?.valid).toBe(false);
  });

  it('should handle boundary values for max upload size', () => {
    fixture.detectChanges();
    // Test minimum value
    component.systemForm.get('max_upload_size_mb')?.setValue(1);
    expect(component.systemForm.get('max_upload_size_mb')?.valid).toBe(true);
    
    // Test maximum value
    component.systemForm.get('max_upload_size_mb')?.setValue(1000);
    expect(component.systemForm.get('max_upload_size_mb')?.valid).toBe(true);
    
    // Test below minimum
    component.systemForm.get('max_upload_size_mb')?.setValue(0);
    expect(component.systemForm.get('max_upload_size_mb')?.valid).toBe(false);
  });

  it('should handle null or undefined settings values', () => {
    const settingsWithNulls: SystemSettingsByCategory = {
      system: [
        {
          id: 1,
          key: 'app_name',
          value: null as any,
          category: 'system',
          data_type: 'string',
          description: 'App name',
          is_sensitive: false,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: null,
          updated_by: null
        }
      ]
    };
    settingsService.getSettings.and.returnValue(of(settingsWithNulls));
    fixture.detectChanges();
    
    // Should handle null values gracefully - component converts null to empty string
    // Using || '' in populateForms converts null to ''
    expect(component.systemForm.get('app_name')?.value).toBe('');
  });

  it('should handle rapid category changes', () => {
    fixture.detectChanges();
    const categories = component.categories;
    
    // Rapidly change categories
    for (let i = 0; i < categories.length; i++) {
      component.onCategoryChange(i);
    }
    
    // Should end up on last category
    expect(component.activeCategory).toBe(categories[categories.length - 1]);
  });

  it('should handle concurrent save attempts', () => {
    fixture.detectChanges();
    component.systemForm.get('session_timeout_minutes')?.setValue(120);
    component.systemForm.get('max_upload_size_mb')?.setValue(10);
    component.systemForm.get('debug_mode')?.setValue(true);
    component.systemForm.get('debug_mode')?.markAsDirty();
    component.systemForm.updateValueAndValidity();
    
    // Simulate concurrent saves
    component.saveCategory();
    component.saveCategory();
    
    // Should handle gracefully (may call service multiple times or debounce)
    expect(settingsService.updateSettingsBatch).toHaveBeenCalled();
  });
});
