import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SettingsService } from '../../services/settings.service';
import { SystemSetting, SystemSettingsByCategory, PlanningCenterConfig } from '../../models/settings.model';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { LoggerService } from '../../services/logger.service';

@Component({
    selector: 'app-settings',
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.scss'],
    standalone: false
})
export class SettingsComponent implements OnInit {
  settings: SystemSettingsByCategory = {};
  categories = ['system', 'planning_center', 'security', 'backup'];
  activeCategory = 'system';
  activeCategoryIndex = 0;
  loading = false;
  saving = false;

  // Form groups for each category
  systemForm!: FormGroup;
  planningCenterForm!: FormGroup;
  securityForm!: FormGroup;
  backupForm!: FormGroup;

  // Planning Center specific
  planningCenterConfig: PlanningCenterConfig | null = null;
  showPlanningCenterSecrets = false;

  constructor(
    private settingsService: SettingsService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private authService: AuthService,
    private router: Router,
    private logger: LoggerService
  ) {
    this.initializeForms();
  }

  ngOnInit(): void {
    // Double-check admin access
    if (!this.authService.isAdmin()) {
      this.snackBar.open('Access denied. Admin privileges required.', 'Close', { duration: 3000 });
      this.router.navigate(['/dashboard']);
      return;
    }

    this.loadSettings();
  }

  initializeForms(): void {
    // System form
    this.systemForm = this.fb.group({
      app_name: [''],
      app_version: [''],
      environment: [''],
      debug_mode: [false],
      session_timeout_minutes: [0, [Validators.min(1), Validators.max(1440)]],
      max_upload_size_mb: [0, [Validators.min(1)]],
      log_level: ['']
    });

    // Planning Center form
    this.planningCenterForm = this.fb.group({
      api_url: ['', Validators.required],
      app_id: [''],
      secret: [''],
      access_token: [''],
      max_events: [2000, [Validators.min(1), Validators.max(10000)]],
      cache_ttl_minutes: [10, [Validators.min(0), Validators.max(1440)]],
      use_mock: [false]
    });

    // Security form
    this.securityForm = this.fb.group({
      password_min_length: [8, [Validators.min(4), Validators.max(128)]],
      password_require_uppercase: [false],
      password_require_lowercase: [false],
      password_require_numbers: [false],
      password_require_special: [false],
      account_lockout_attempts: [5, [Validators.min(1), Validators.max(20)]],
      account_lockout_duration_minutes: [30, [Validators.min(1), Validators.max(1440)]],
      session_idle_timeout_minutes: [60, [Validators.min(1), Validators.max(1440)]],
      rate_limit_enabled: [true],
      rate_limit_requests: [100, [Validators.min(1)]],
      rate_limit_window_seconds: [60, [Validators.min(1)]]
    });

    // Backup form
    this.backupForm = this.fb.group({
      backup_enabled: [false],
      backup_frequency_days: [7, [Validators.min(1), Validators.max(365)]],
      backup_retention_days: [30, [Validators.min(1), Validators.max(3650)]],
      maintenance_window_start: ['02:00'],
      maintenance_window_end: ['04:00']
    });
  }

  loadSettings(): void {
    this.loading = true;
    this.settingsService.getSettings().subscribe({
      next: (data) => {
        this.settings = data;
        this.populateForms();
        this.loading = false;
      },
      error: (error) => {
        this.logger.error('Error loading settings', error);
        this.snackBar.open('Error loading settings', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  populateForms(): void {
    // Populate system form
    if (this.settings['system']) {
      this.settings['system'].forEach(setting => {
        const control = this.systemForm.get(setting.key);
        if (control) {
          if (setting.data_type === 'boolean') {
            control.setValue(setting.value === 'true' || setting.value === '1');
          } else if (setting.data_type === 'integer') {
            control.setValue(setting.value ? parseInt(setting.value, 10) : 0);
          } else {
            control.setValue(setting.value || '');
          }
        }
      });
    }

    // Load Planning Center config
    this.loadPlanningCenterConfig();

    // Populate security form
    if (this.settings['security']) {
      this.settings['security'].forEach(setting => {
        const control = this.securityForm.get(setting.key);
        if (control) {
          if (setting.data_type === 'boolean') {
            control.setValue(setting.value === 'true' || setting.value === '1');
          } else if (setting.data_type === 'integer') {
            control.setValue(setting.value ? parseInt(setting.value, 10) : 0);
          } else {
            control.setValue(setting.value || '');
          }
        }
      });
    }

    // Populate backup form
    if (this.settings['backup']) {
      this.settings['backup'].forEach(setting => {
        const control = this.backupForm.get(setting.key);
        if (control) {
          if (setting.data_type === 'boolean') {
            control.setValue(setting.value === 'true' || setting.value === '1');
          } else if (setting.data_type === 'integer') {
            control.setValue(setting.value ? parseInt(setting.value, 10) : 0);
          } else {
            control.setValue(setting.value || '');
          }
        }
      });
    }
  }

  loadPlanningCenterConfig(): void {
    this.settingsService.getPlanningCenterConfig().subscribe({
      next: (config) => {
        this.planningCenterConfig = config;
        this.planningCenterForm.patchValue({
          api_url: config.api_url,
          app_id: config.app_id || '',
          secret: config.secret || '',
          access_token: config.access_token || '',
          max_events: config.max_events,
          cache_ttl_minutes: config.cache_ttl_minutes,
          use_mock: config.use_mock
        });
      },
      error: (error) => {
        this.logger.error('Error loading Planning Center config', error);
      }
    });
  }

  onCategoryChange(index: number): void {
    if (index >= 0 && index < this.categories.length) {
      this.activeCategory = this.categories[index];
      this.activeCategoryIndex = index;
    }
  }

  get activeCategoryIndexValue(): number {
    return this.categories.indexOf(this.activeCategory);
  }

  saveCategory(): void {
    if (this.saving) return;

    let form: FormGroup;
    let categoryName: string;

    switch (this.activeCategory) {
      case 'system':
        form = this.systemForm;
        categoryName = 'System';
        break;
      case 'planning_center':
        form = this.planningCenterForm;
        categoryName = 'Planning Center';
        this.savePlanningCenterConfig();
        return;
      case 'security':
        form = this.securityForm;
        categoryName = 'Security';
        break;
      case 'backup':
        form = this.backupForm;
        categoryName = 'Backup';
        break;
      default:
        return;
    }

    if (!form.valid) {
      this.snackBar.open('Please fix validation errors', 'Close', { duration: 3000 });
      return;
    }

    this.saving = true;
    const updates: { [key: string]: string } = {};

    Object.keys(form.controls).forEach(key => {
      const control = form.get(key);
      if (control && control.dirty) {
        let value = control.value;
        if (typeof value === 'boolean') {
          value = value ? 'true' : 'false';
        } else if (typeof value === 'number') {
          value = value.toString();
        }
        updates[key] = value;
      }
    });

    if (Object.keys(updates).length === 0) {
      this.snackBar.open('No changes to save', 'Close', { duration: 2000 });
      this.saving = false;
      return;
    }

    this.settingsService.updateSettingsBatch(updates).subscribe({
      next: () => {
        this.snackBar.open(`${categoryName} settings saved successfully`, 'Close', { duration: 3000 });
        form.markAsPristine();
        this.saving = false;
        this.loadSettings(); // Reload to get updated values
      },
      error: (error) => {
        this.logger.error('Error saving settings', error);
        this.snackBar.open('Error saving settings', 'Close', { duration: 3000 });
        this.saving = false;
      }
    });
  }

  savePlanningCenterConfig(): void {
    if (!this.planningCenterForm.valid) {
      this.snackBar.open('Please fix validation errors', 'Close', { duration: 3000 });
      return;
    }

    this.saving = true;
    const config: PlanningCenterConfig = {
      api_url: this.planningCenterForm.value.api_url,
      app_id: this.planningCenterForm.value.app_id || null,
      secret: this.planningCenterForm.value.secret || null,
      access_token: this.planningCenterForm.value.access_token || null,
      max_events: this.planningCenterForm.value.max_events,
      cache_ttl_minutes: this.planningCenterForm.value.cache_ttl_minutes,
      use_mock: this.planningCenterForm.value.use_mock
    };

    this.settingsService.updatePlanningCenterConfig(config).subscribe({
      next: () => {
        this.snackBar.open('Planning Center settings saved successfully', 'Close', { duration: 3000 });
        this.planningCenterForm.markAsPristine();
        this.saving = false;
        this.loadPlanningCenterConfig();
      },
      error: (error) => {
        this.logger.error('Error saving Planning Center config', error);
        this.snackBar.open('Error saving Planning Center settings', 'Close', { duration: 3000 });
        this.saving = false;
      }
    });
  }

  cancelChanges(): void {
    this.loadSettings();
  }

  togglePlanningCenterSecrets(): void {
    this.showPlanningCenterSecrets = !this.showPlanningCenterSecrets;
  }

  getMaskedValue(value: string | null | undefined): string {
    if (!value) return '';
    return '•'.repeat(20);
  }
}
