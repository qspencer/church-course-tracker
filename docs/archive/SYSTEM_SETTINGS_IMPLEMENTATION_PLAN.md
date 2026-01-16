# System Settings Implementation Plan

## Overview

This document outlines the implementation plan for the System Settings feature, which will allow administrators to configure system parameters, manage Planning Center integration, set security policies, and configure backup/maintenance schedules through a web UI.

## Current Status

### ✅ Existing Infrastructure
- Configuration management via `backend/app/core/config.py`
- Planning Center integration exists
- Admin role and authentication system
- Audit logging system

### ❌ Missing Components
- System Settings database model
- System Settings API endpoints
- System Settings frontend component
- System Settings route and navigation

## Feature Requirements (From Documentation)

Based on `docs/archive/ROLE_USE_CASES.md` and `docs/FEATURES.md`, System Settings should include:

1. **System Configuration**
   - Configure system settings and parameters
   - Manage Planning Center API integration settings
   - Set up security policies and access controls
   - Configure backup and maintenance schedules

2. **Planning Center Integration Management**
   - Manage synchronization with Planning Center
   - Resolve data sync conflicts
   - Configure mapping between systems
   - Monitor integration health

## Implementation Phases

### Phase 1: Backend Foundation (8-10 hours)

#### 1.1 Database Model (2 hours)

**File:** `backend/app/models/system_settings.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # 'system', 'planning_center', 'security', 'backup'
    data_type = Column(String(20), nullable=False)  # 'string', 'integer', 'boolean', 'json'
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # For passwords/secrets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)  # User ID who last updated
```

**Tasks:**
- [ ] Create model file
- [ ] Add to `backend/app/models/__init__.py`
- [ ] Create Alembic migration
- [ ] Seed initial settings from current config

#### 1.2 Pydantic Schemas (1 hour)

**File:** `backend/app/schemas/system_settings.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SystemSettingsBase(BaseModel):
    key: str
    value: Optional[str] = None
    category: str
    data_type: str
    description: Optional[str] = None
    is_sensitive: bool = False

class SystemSettingsCreate(SystemSettingsBase):
    pass

class SystemSettingsUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettings(SystemSettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class SystemSettingsCategory(BaseModel):
    category: str
    settings: list[SystemSettings]
```

**Tasks:**
- [ ] Create schema file
- [ ] Add validation for data types
- [ ] Add category validation

#### 1.3 Service Layer (2-3 hours)

**File:** `backend/app/services/system_settings_service.py`

**Key Methods:**
```python
class SystemSettingsService:
    def get_setting(self, key: str) -> Optional[SystemSettings]
    def get_settings_by_category(self, category: str) -> List[SystemSettings]
    def get_all_settings(self) -> Dict[str, List[SystemSettings]]
    def update_setting(self, key: str, value: str, updated_by: int) -> SystemSettings
    def update_settings_batch(self, settings: Dict[str, str], updated_by: int) -> List[SystemSettings]
    def get_planning_center_config(self) -> Dict[str, Any]
    def update_planning_center_config(self, config: Dict[str, Any], updated_by: int) -> Dict[str, SystemSettings]
    def validate_setting_value(self, key: str, value: str) -> bool
    def sync_to_environment(self) -> None  # Sync DB settings to environment
```

**Tasks:**
- [ ] Create service file
- [ ] Implement CRUD operations
- [ ] Add validation logic
- [ ] Add environment variable sync
- [ ] Add audit logging for changes

#### 1.4 API Endpoints (2-3 hours)

**File:** `backend/app/api/v1/endpoints/system_settings.py`

**Endpoints:**
```python
@router.get("", response_model=Dict[str, List[SystemSettings]])
async def get_all_settings(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.get("/{key}", response_model=SystemSettings)
async def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.patch("/{key}", response_model=SystemSettings)
async def update_setting(
    key: str,
    setting_update: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.patch("/batch", response_model=List[SystemSettings])
async def update_settings_batch(
    settings: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.get("/planning-center/config", response_model=Dict[str, Any])
async def get_planning_center_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.patch("/planning-center/config", response_model=Dict[str, SystemSettings])
async def update_planning_center_config(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)

@router.post("/sync-to-env")
async def sync_to_environment(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_admin_user)
)
```

**Tasks:**
- [ ] Create endpoints file
- [ ] Add to `backend/app/api/v1/api.py` router
- [ ] Add admin-only authorization
- [ ] Add input validation
- [ ] Add error handling

#### 1.5 Database Migration (1 hour)

**File:** `backend/migrations/versions/XXXX_add_system_settings.py`

**Tasks:**
- [ ] Create migration script
- [ ] Add initial settings seed data
- [ ] Test migration up/down

#### 1.6 Initial Settings Seed (1 hour)

**File:** `backend/scripts/seed_system_settings.py`

**Settings to Seed:**
- System Configuration:
  - `app_name`
  - `app_version`
  - `environment`
  - `debug_mode`
  - `session_timeout_minutes`
  - `max_upload_size_mb`
  
- Planning Center:
  - `planning_center_api_url`
  - `planning_center_app_id` (sensitive)
  - `planning_center_secret` (sensitive)
  - `planning_center_access_token` (sensitive)
  - `planning_center_max_events`
  - `planning_center_cache_ttl_minutes`
  - `use_mock_planning_center`
  
- Security:
  - `password_min_length`
  - `password_require_uppercase`
  - `password_require_lowercase`
  - `password_require_numbers`
  - `password_require_special`
  - `account_lockout_attempts`
  - `account_lockout_duration_minutes`
  - `session_idle_timeout_minutes`
  
- Backup & Maintenance:
  - `backup_enabled`
  - `backup_frequency_days`
  - `backup_retention_days`
  - `maintenance_window_start`
  - `maintenance_window_end`

**Tasks:**
- [ ] Create seed script
- [ ] Map current config.py values
- [ ] Run seed script
- [ ] Verify settings in database

---

### Phase 2: Frontend Implementation (12-15 hours)

#### 2.1 Settings Component Structure (2 hours)

**Files to Create:**
- `frontend/church-course-tracker/src/app/components/settings/settings.component.ts`
- `frontend/church-course-tracker/src/app/components/settings/settings.component.html`
- `frontend/church-course-tracker/src/app/components/settings/settings.component.scss`
- `frontend/church-course-tracker/src/app/components/settings/settings.module.ts`

**Component Structure:**
```typescript
@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  settings: Map<string, SystemSetting[]> = new Map();
  categories = ['system', 'planning_center', 'security', 'backup'];
  activeCategory = 'system';
  loading = false;
  saving = false;
  
  // Form groups for each category
  systemForm: FormGroup;
  planningCenterForm: FormGroup;
  securityForm: FormGroup;
  backupForm: FormGroup;
}
```

**Tasks:**
- [ ] Create component files
- [ ] Set up module structure
- [ ] Create basic component skeleton
- [ ] Add Material Design imports

#### 2.2 Settings Service (2 hours)

**File:** `frontend/church-course-tracker/src/app/services/settings.service.ts`

**Service Methods:**
```typescript
@Injectable({ providedIn: 'root' })
export class SettingsService {
  getSettings(category?: string): Observable<Map<string, SystemSetting[]>>
  getSetting(key: string): Observable<SystemSetting>
  updateSetting(key: string, value: string): Observable<SystemSetting>
  updateSettingsBatch(settings: {[key: string]: string}): Observable<SystemSetting[]>
  getPlanningCenterConfig(): Observable<PlanningCenterConfig>
  updatePlanningCenterConfig(config: PlanningCenterConfig): Observable<SystemSetting[]>
  syncToEnvironment(): Observable<void>
}
```

**Tasks:**
- [ ] Create service file
- [ ] Implement HTTP methods
- [ ] Add error handling
- [ ] Add TypeScript interfaces

#### 2.3 Settings UI - Main Component (4-5 hours)

**Features:**
- Tabbed interface for categories:
  - System Configuration
  - Planning Center Integration
  - Security Policies
  - Backup & Maintenance
- Form fields for each setting
- Save/Cancel buttons
- Success/error notifications
- Loading states
- Sensitive field masking (for passwords/secrets)

**UI Layout:**
```
┌─────────────────────────────────────────┐
│  System Settings                        │
├─────────────────────────────────────────┤
│ [System] [Planning Center] [Security]  │
│           [Backup]                      │
├─────────────────────────────────────────┤
│                                         │
│  Setting Name: [input field]            │
│  Description: [help text]               │
│                                         │
│  Setting Name: [input field]            │
│  Description: [help text]               │
│                                         │
│  [Cancel]  [Save Changes]               │
└─────────────────────────────────────────┘
```

**Tasks:**
- [ ] Create tabbed interface
- [ ] Create form groups for each category
- [ ] Add form validation
- [ ] Add save/cancel functionality
- [ ] Add loading states
- [ ] Add success/error notifications
- [ ] Style with Material Design

#### 2.4 Planning Center Integration UI (2-3 hours)

**Special Features:**
- Test connection button
- Show connection status
- Sync status indicator
- Last sync timestamp
- Manual sync trigger button

**Tasks:**
- [ ] Create Planning Center section
- [ ] Add connection test functionality
- [ ] Add sync status display
- [ ] Add manual sync trigger
- [ ] Add validation for API credentials

#### 2.5 Security Settings UI (2 hours)

**Features:**
- Password policy configuration
- Account lockout settings
- Session timeout settings
- Security policy toggles

**Tasks:**
- [ ] Create security settings form
- [ ] Add password policy inputs
- [ ] Add account lockout settings
- [ ] Add session timeout settings
- [ ] Add validation

#### 2.6 Backup & Maintenance UI (1-2 hours)

**Features:**
- Backup enable/disable toggle
- Backup frequency settings
- Retention period settings
- Maintenance window configuration

**Tasks:**
- [ ] Create backup settings form
- [ ] Add backup configuration inputs
- [ ] Add maintenance window picker
- [ ] Add validation

#### 2.7 Routing and Navigation (1 hour)

**Tasks:**
- [ ] Add route to `app-routing.module.ts`:
  ```typescript
  {
    path: 'settings',
    loadChildren: () => import('./components/settings/settings.module').then(m => m.SettingsModule),
    canActivate: [AuthGuard, AdminGuard]
  }
  ```
- [ ] Add navigation link in main navigation (admin only)
- [ ] Add icon (settings icon)
- [ ] Test routing

---

### Phase 3: Integration and Testing (8-10 hours)

#### 3.1 Backend Unit Tests (3 hours)

**File:** `backend/tests/test_system_settings.py`

**Test Cases:**
- [ ] Test SystemSettingsService CRUD operations
- [ ] Test setting validation
- [ ] Test category filtering
- [ ] Test batch updates
- [ ] Test Planning Center config methods
- [ ] Test environment sync
- [ ] Test sensitive field handling

#### 3.2 Backend API Tests (2 hours)

**File:** `backend/tests/test_system_settings_endpoints.py`

**Test Cases:**
- [ ] Test GET /api/v1/settings (all settings)
- [ ] Test GET /api/v1/settings?category=system
- [ ] Test GET /api/v1/settings/{key}
- [ ] Test PATCH /api/v1/settings/{key}
- [ ] Test PATCH /api/v1/settings/batch
- [ ] Test GET /api/v1/settings/planning-center/config
- [ ] Test PATCH /api/v1/settings/planning-center/config
- [ ] Test POST /api/v1/settings/sync-to-env
- [ ] Test admin-only authorization
- [ ] Test validation errors
- [ ] Test audit logging

#### 3.3 Frontend Unit Tests (2 hours)

**File:** `frontend/church-course-tracker/src/app/components/settings/settings.component.spec.ts`

**Test Cases:**
- [ ] Test component initialization
- [ ] Test form loading
- [ ] Test category switching
- [ ] Test form validation
- [ ] Test save functionality
- [ ] Test error handling
- [ ] Test service integration

#### 3.4 E2E Tests (2-3 hours)

**File:** `tests/e2e/role-based-access.spec.ts` (update existing test)

**Test Cases:**
- [ ] Test admin can access settings page
- [ ] Test admin can view all settings categories
- [ ] Test admin can update system settings
- [ ] Test admin can update Planning Center config
- [ ] Test admin can update security settings
- [ ] Test admin can update backup settings
- [ ] Test non-admin cannot access settings
- [ ] Test settings persist after save
- [ ] Test validation errors display correctly

---

### Phase 4: Security and Validation (4-5 hours)

#### 4.1 Security Considerations (2 hours)

**Tasks:**
- [ ] Encrypt sensitive settings in database
- [ ] Add rate limiting for settings updates
- [ ] Add audit logging for all changes
- [ ] Validate admin permissions
- [ ] Sanitize all inputs
- [ ] Add CSRF protection
- [ ] Mask sensitive values in API responses
- [ ] Add confirmation dialogs for critical changes

#### 4.2 Input Validation (1-2 hours)

**Validation Rules:**
- [ ] Validate data types (string, integer, boolean, json)
- [ ] Validate ranges (e.g., timeout values)
- [ ] Validate formats (e.g., URLs, email patterns)
- [ ] Validate Planning Center credentials format
- [ ] Validate maintenance window times
- [ ] Add custom validators for complex fields

#### 4.3 Error Handling (1 hour)

**Tasks:**
- [ ] Add comprehensive error messages
- [ ] Handle network errors gracefully
- [ ] Handle validation errors
- [ ] Handle permission errors
- [ ] Add user-friendly error messages
- [ ] Log errors for debugging

---

### Phase 5: Documentation and Deployment (2-3 hours)

#### 5.1 API Documentation (1 hour)

**Tasks:**
- [ ] Add OpenAPI/Swagger documentation
- [ ] Document all endpoints
- [ ] Document request/response schemas
- [ ] Document error responses
- [ ] Add example requests

#### 5.2 User Documentation (1 hour)

**Tasks:**
- [ ] Update USER_GUIDE.md with settings section
- [ ] Add screenshots
- [ ] Document each setting category
- [ ] Add troubleshooting guide

#### 5.3 Deployment Considerations (1 hour)

**Tasks:**
- [ ] Update migration scripts
- [ ] Add settings to environment variable documentation
- [ ] Create deployment checklist
- [ ] Document rollback procedure

---

## Technical Specifications

### Database Schema

```sql
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    category VARCHAR(50) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_system_settings_category ON system_settings(category);
CREATE INDEX idx_system_settings_key ON system_settings(key);
```

### API Response Examples

**GET /api/v1/settings**
```json
{
  "system": [
    {
      "id": 1,
      "key": "app_name",
      "value": "Church Course Tracker",
      "category": "system",
      "data_type": "string",
      "description": "Application name",
      "is_sensitive": false
    }
  ],
  "planning_center": [...],
  "security": [...],
  "backup": [...]
}
```

**PATCH /api/v1/settings/app_name**
```json
{
  "value": "New App Name"
}
```

### Frontend Models

```typescript
export interface SystemSetting {
  id: number;
  key: string;
  value: string | null;
  category: string;
  data_type: 'string' | 'integer' | 'boolean' | 'json';
  description: string | null;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string | null;
  updated_by: number | null;
}

export interface PlanningCenterConfig {
  api_url: string;
  app_id: string;
  secret: string;  // Masked in UI
  access_token: string;  // Masked in UI
  max_events: number;
  cache_ttl_minutes: number;
  use_mock: boolean;
}
```

---

## Implementation Timeline

### Sprint 1: Backend Foundation (Week 1)
- Day 1-2: Database model and migration
- Day 3-4: Service layer and API endpoints
- Day 5: Testing and bug fixes

**Estimated Time:** 8-10 hours

### Sprint 2: Frontend Core (Week 2)
- Day 1-2: Component structure and service
- Day 3-4: Main settings UI
- Day 5: Testing and refinements

**Estimated Time:** 12-15 hours

### Sprint 3: Advanced Features (Week 3)
- Day 1-2: Planning Center integration UI
- Day 3: Security and Backup UI
- Day 4-5: Integration testing and bug fixes

**Estimated Time:** 8-10 hours

### Sprint 4: Polish and Deploy (Week 4)
- Day 1-2: Security hardening and validation
- Day 3: Documentation
- Day 4-5: Final testing and deployment

**Estimated Time:** 6-8 hours

**Total Estimated Time:** 34-43 hours (~4-5 weeks)

---

## Risk Assessment

### High Risk
- **Sensitive Data Storage**: Passwords and API keys need encryption
- **Environment Variable Sync**: Need to ensure DB and env stay in sync
- **Breaking Changes**: Settings changes could affect running system

### Medium Risk
- **Planning Center Integration**: Changes could break existing integration
- **Security Settings**: Incorrect settings could compromise security
- **Backup Configuration**: Wrong settings could affect data safety

### Low Risk
- **UI/UX**: Standard form implementation
- **Basic CRUD**: Standard patterns

### Mitigation Strategies
1. **Encryption**: Use application-level encryption for sensitive settings
2. **Validation**: Comprehensive validation before saving
3. **Audit Logging**: Log all changes for rollback capability
4. **Staging Testing**: Test all changes in staging environment
5. **Gradual Rollout**: Deploy to production gradually
6. **Backup Before Changes**: Always backup before major changes

---

## Success Criteria

1. ✅ Admin can access System Settings page
2. ✅ Admin can view all settings by category
3. ✅ Admin can update individual settings
4. ✅ Admin can update settings in batch
5. ✅ Admin can configure Planning Center integration
6. ✅ Admin can configure security policies
7. ✅ Admin can configure backup/maintenance
8. ✅ Settings persist correctly
9. ✅ Sensitive settings are masked in UI
10. ✅ All changes are audited
11. ✅ Non-admin users cannot access settings
12. ✅ All tests pass
13. ✅ Documentation is complete

---

## Dependencies

### Backend
- SQLAlchemy models
- FastAPI endpoints
- Pydantic schemas
- Authentication/Authorization system
- Audit logging system

### Frontend
- Angular Material components
- Reactive Forms
- HTTP Client
- Routing system
- Admin guard

### External
- Planning Center API (for integration testing)
- Database (PostgreSQL/SQLite)

---

## Next Steps

1. **Review and Approve Plan**
2. **Create Feature Branch**: `feature/system-settings`
3. **Begin Phase 1**: Backend foundation
4. **Code Review**: After each phase
5. **Testing**: Unit → Integration → E2E
6. **Documentation**: Update as implementation progresses
7. **Deploy**: Staging → Production

---

## Notes

- Settings stored in database will take precedence over environment variables
- Environment variable sync is one-way (DB → Env) for security
- Sensitive settings should never be logged or exposed in error messages
- All setting changes should trigger audit log entries
- Consider adding a "Reset to Defaults" feature for each category
- Consider adding setting change history/versioning
- Planning Center credentials should be validated before saving
