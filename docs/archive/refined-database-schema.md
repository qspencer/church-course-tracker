# Refined Database Schema - Church Course Tracker

## Core Entities

### 1. **people** (Church Members - Synced with Planning Center)
```sql
people:
- id (primary key)
- planning_center_id (unique, for sync with PC)
- first_name, last_name
- email, phone
- date_of_birth
- gender
- address1, address2, city, state, zip
- household_id (Planning Center household reference)
- household_name
- status (active, inactive, etc.)
- join_date
- last_synced_at (when last synced with Planning Center)
- is_active
- created_at, updated_at
- created_by, updated_by (audit trail)
```

### 2. **campus** (Church Locations)
```sql
campus:
- id (primary key)
- name
- address
- phone, email
- planning_center_location_id (if PC has location data)
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 3. **role** (System Roles)
```sql
role:
- id (primary key)
- name (admin, staff, member, guest)
- description
- permissions (JSON array of permissions)
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 4. **course** (Course Definitions - Maps to Planning Center Events)
```sql
course:
- id (primary key)
- name
- description
- duration_weeks
- prerequisites (JSON array of course IDs)
- planning_center_event_id (foreign key to PC Events)
- planning_center_event_name (cached from PC)
- event_start_date (from PC Event)
- event_end_date (from PC Event)
- max_capacity (from PC Event)
- current_registrations (cached count from PC)
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 5. **content** (Course Content/Modules)
```sql
content:
- id (primary key)
- course_id (foreign key)
- title
- content_type_id (foreign key)
- order_sequence
- file_path/url
- duration_minutes
- is_required
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 6. **content_type** (Extensible Content Types)
```sql
content_type:
- id (primary key)
- name (video, document, book, etc.)
- description
- icon_class (for UI)
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 7. **certification** (New Requirement)
```sql
certification:
- id (primary key)
- name
- description
- required_courses (JSON array of course IDs)
- validity_months (how long certification is valid)
- is_active
- created_at, updated_at
- created_by, updated_by
```

## Relationship Tables

### 8. **people_campus** (People assigned to campuses)
```sql
people_campus:
- id (primary key)
- people_id (foreign key)
- campus_id (foreign key)
- assigned_date
- is_primary (boolean - main campus)
- is_active
- created_at, updated_at
- created_by, updated_by
```

### 9. **people_role** (People's system roles)
```sql
people_role:
- id (primary key)
- people_id (foreign key)
- role_id (foreign key)
- assigned_date
- assigned_by
- is_active
- created_at, updated_at
```

### 10. **course_enrollment** (Course registrations - Maps to Planning Center Registrations)
```sql
course_enrollment:
- id (primary key)
- people_id (foreign key)
- course_id (foreign key)
- planning_center_registration_id (foreign key to PC Registration)
- enrollment_date
- status (enrolled, in_progress, completed, dropped)
- progress_percentage
- completion_date
- notes
- dependency_override (boolean - admin override)
- dependency_override_by (who overrode)
- planning_center_synced (boolean - synced back to PC)
- registration_status (registered, cancelled, waitlisted - from PC)
- registration_notes (from PC registration)
- created_at, updated_at
- created_by, updated_by
```

### 11. **course_role** (Course-specific roles - NEW!)
```sql
course_role:
- id (primary key)
- people_id (foreign key)
- course_id (foreign key)
- role_type (teacher, student, assistant, observer)
- assigned_date
- assigned_by
- is_active
- created_at, updated_at
```

### 12. **certification_progress** (Certification tracking)
```sql
certification_progress:
- id (primary key)
- people_id (foreign key)
- certification_id (foreign key)
- started_date
- completed_date
- status (in_progress, completed, expired)
- expires_date
- created_at, updated_at
- created_by, updated_by
```

### 13. **content_completion** (Content-level progress)
```sql
content_completion:
- id (primary key)
- course_enrollment_id (foreign key)
- content_id (foreign key)
- completed_at
- time_spent_minutes
- score (if applicable)
- notes
- created_at, updated_at
```

## Planning Center Integration Tables

### 14. **planning_center_sync_log** (Sync tracking)
```sql
planning_center_sync_log:
- id (primary key)
- sync_type (people, events, registrations, custom_fields)
- sync_direction (from_pc, to_pc)
- records_processed
- records_successful
- records_failed
- error_details (JSON)
- started_at
- completed_at
- created_by
```

### 15. **planning_center_webhook_events** (Webhook tracking)
```sql
planning_center_webhook_events:
- id (primary key)
- event_type (person.created, person.updated, event.created, registration.created, etc.)
- planning_center_id
- payload (JSON)
- processed (boolean)
- processed_at
- error_message
- created_at
```

### 16. **planning_center_events_cache** (Cached PC Events data)
```sql
planning_center_events_cache:
- id (primary key)
- planning_center_event_id (unique)
- event_name
- event_description
- start_date
- end_date
- max_capacity
- current_registrations_count
- registration_deadline
- event_status
- last_synced_at
- created_at, updated_at
```

### 17. **planning_center_registrations_cache** (Cached PC Registrations data)
```sql
planning_center_registrations_cache:
- id (primary key)
- planning_center_registration_id (unique)
- planning_center_event_id
- planning_center_person_id
- registration_status (registered, cancelled, waitlisted)
- registration_date
- registration_notes
- custom_field_responses (JSON)
- last_synced_at
- created_at, updated_at
```

## Audit Trail Table

### 18. **audit_log** (Comprehensive audit trail)
```sql
audit_log:
- id (primary key)
- table_name
- record_id
- action (insert, update, delete)
- old_values (JSON)
- new_values (JSON)
- changed_by
- changed_at
- ip_address
- user_agent
```

## Key Features Supported

✅ **Multi-campus support**  
✅ **Course-specific roles** (teacher/student per course)  
✅ **Prerequisites with admin override**  
✅ **Extensible content types**  
✅ **Certification tracking**  
✅ **Comprehensive audit trails**  
✅ **Planning Center integration** with OAuth 2.0  
✅ **Real-time webhook support**  
✅ **Bidirectional sync** (read from PC, write back course data)  
✅ **Sync logging and error tracking**  

## Planning Center Integration Strategy

### Data Flow:
1. **People Data**: Sync from Planning Center → Local database
2. **Events Data**: Sync from Planning Center → Local database (courses)
3. **Registrations Data**: Sync from Planning Center → Local database (enrollments)
4. **Progress Data**: Local database → Planning Center (via custom fields on registrations)
5. **Real-time Updates**: Webhooks for immediate sync
6. **Error Handling**: Comprehensive logging and retry mechanisms

### API Endpoints to Implement:
- `GET /api/v1/sync/people` - Sync people from Planning Center
- `GET /api/v1/sync/events` - Sync events from Planning Center
- `GET /api/v1/sync/registrations` - Sync registrations from Planning Center
- `POST /api/v1/sync/progress` - Push progress data to Planning Center
- `GET /api/v1/sync/status` - Get sync status and logs
- `POST /api/v1/webhooks/planning-center` - Handle PC webhooks

### Planning Center API Integration:
- **Events API**: `/events` - Get all events (courses)
- **Registrations API**: `/events/{event_id}/registrations` - Get event registrations
- **People API**: `/people` - Get people data
- **Custom Fields**: Update registration custom fields with progress data
- **Webhooks**: Listen for `event.created`, `registration.created`, `registration.updated`
