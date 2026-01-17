# Planning Center Custom Tab Mapping System

**Date**: January 17, 2026
**Status**: In Development

## Overview

The Planning Center Custom Tab Mapping system provides a flexible, configurable way to import participant data from arbitrary Planning Center custom tabs into Church Course Tracker programs. This eliminates hard-coded field mappings and allows each program to define its own data import rules.

## Architecture

### Problem Statement

Different churches use Planning Center custom tabs differently:
- Tab names vary ("Life On Life Discipleship", "Mentorship Program", "Leadership Track")
- Field names differ ("Role" vs "Type" vs "Participant Type")
- Field values vary ("Mentor/Mentee" vs "Leader/Follower" vs custom values)
- Some use dates, checkboxes, text fields, dropdowns, etc.

**Solution**: Store flexible field mapping configuration in each Program, allowing admins to map any Planning Center custom tab to program fields through the UI.

### Data Model

#### Program Model Addition

```python
# backend/app/models/program.py

planning_center_tab_config = Column(JSON, nullable=True)
```

**Configuration Structure**:

```json
{
  "enabled": true,
  "tab_slug": "life_on_life_discipleship",
  "tab_name": "Life On Life Discipleship",
  "field_mappings": [
    {
      "pc_field_name": "Role",
      "pc_field_slug": "role",
      "pc_field_type": "select",
      "target_type": "participant_role",
      "mapping_rules": [
        {"when": "Mentor", "assign_role": "Mentor"},
        {"when": "Mentee", "assign_role": "Mentee"},
        {"when": "Discipler", "assign_role": "Mentor"},
        {"when": "Disciple", "assign_role": "Mentee"}
      ]
    },
    {
      "pc_field_name": "Start Date",
      "pc_field_slug": "start_date",
      "pc_field_type": "date",
      "target_type": "participant_start_date",
      "mapping_rules": null
    },
    {
      "pc_field_name": "Notes",
      "pc_field_slug": "notes",
      "pc_field_type": "text",
      "target_type": "participant_notes",
      "mapping_rules": null
    },
    {
      "pc_field_name": "Active Status",
      "pc_field_slug": "active_status",
      "pc_field_type": "checkbox",
      "target_type": "participant_status",
      "mapping_rules": [
        {"when": true, "assign_status": "active"},
        {"when": false, "assign_status": "paused"}
      ]
    }
  ],
  "default_status": "active",
  "update_existing": false,
  "sync_on_import": true
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Whether tab import is enabled for this program |
| `tab_slug` | string | Planning Center tab slug (from API) |
| `tab_name` | string | Human-readable tab name (for display) |
| `field_mappings` | array | Array of field mapping configurations |
| `default_status` | string | Default participant status on import ('active', 'paused', etc.) |
| `update_existing` | boolean | Whether to update existing participants |
| `sync_on_import` | boolean | Whether to sync people from PC if not found locally |

### Field Mapping Structure

Each field mapping has:

| Field | Type | Description |
|-------|------|-------------|
| `pc_field_name` | string | Planning Center field name (display) |
| `pc_field_slug` | string | Planning Center field slug (from API) |
| `pc_field_type` | string | Field type: 'text', 'select', 'checkbox', 'date', 'number' |
| `target_type` | string | Where this maps to (see Target Types below) |
| `mapping_rules` | array/null | Conditional mapping rules or null for direct mapping |

### Target Types

Available target types:

| Target Type | Maps To | Example |
|-------------|---------|---------|
| `participant_role` | ProgramParticipant.role_name | "Mentor", "Mentee" |
| `participant_status` | ProgramParticipant.status | "active", "paused", "completed" |
| `participant_start_date` | ProgramParticipant.start_date | ISO date string |
| `participant_end_date` | ProgramParticipant.end_date | ISO date string |
| `participant_notes` | ProgramParticipant.notes | Free text |
| `participant_progress` | ProgramParticipant.progress_percentage | 0-100 |
| `ignore` | (not imported) | Skip this field |

### Mapping Rules

**Direct Mapping** (mapping_rules = null):
- Value is copied directly from PC field to target field
- Used for dates, text, numbers

**Conditional Mapping** (mapping_rules = array):
- Value is transformed based on conditions
- Used for select fields, checkboxes, role assignment

**Example Conditional Rules**:

```json
{
  "pc_field_name": "Role",
  "target_type": "participant_role",
  "mapping_rules": [
    {"when": "Mentor", "assign_role": "Mentor"},
    {"when": "Mentee", "assign_role": "Mentee"},
    {"when": "Leader", "assign_role": "Mentor"},
    {"when": "Apprentice", "assign_role": "Mentee"}
  ]
}
```

**Checkbox Mapping**:

```json
{
  "pc_field_name": "Is Active",
  "target_type": "participant_status",
  "mapping_rules": [
    {"when": true, "assign_status": "active"},
    {"when": false, "assign_status": "ended"}
  ]
}
```

## Implementation

### Phase 1: Service Layer Methods (Completed)

✅ Added `planning_center_tab_config` to Program model
✅ Added field to Program schemas
✅ Created database migration

### Phase 2: Planning Center API Methods (In Progress)

Add these methods to `PlanningCenterSyncService`:

#### 1. Discover Available Tabs

```python
def get_person_tabs(self, person_id: str) -> List[Dict[str, Any]]:
    """
    Get all custom tabs available for a person

    Returns:
        [
          {
            "id": "12345",
            "type": "Tab",
            "attributes": {
              "name": "Life On Life Discipleship",
              "slug": "life_on_life_discipleship",
              "tab_id": 67890
            }
          }
        ]
    """
```

#### 2. Get Tab Field Definitions

```python
def get_tab_field_definitions(self, tab_id: str) -> List[Dict[str, Any]]:
    """
    Get field definitions for a custom tab

    Returns:
        [
          {
            "id": "11111",
            "type": "FieldDefinition",
            "attributes": {
              "name": "Role",
              "slug": "role",
              "data_type": "select",
              "options": ["Mentor", "Mentee"],
              "required": true
            }
          }
        ]
    """
```

#### 3. Get Person Tab Data

```python
def get_person_tab_data(self, person_id: str, tab_slug: str) -> List[Dict[str, Any]]:
    """
    Get tab field data for a specific person

    Returns:
        [
          {
            "id": "22222",
            "type": "FieldDatum",
            "attributes": {
              "value": "Mentor",
              "field_definition_id": "11111",
              "field_definition": {
                "name": "Role",
                "slug": "role",
                "data_type": "select"
              }
            }
          }
        ]
    """
```

#### 4. Bulk Import with Tab Data

```python
def get_list_people_with_tab_data(
    self,
    list_id: str,
    tab_slug: str
) -> List[Dict[str, Any]]:
    """
    Get all people from a list WITH their custom tab data

    Returns list of people with 'custom_tab_data' array added
    """
```

### Phase 3: Generic Import Logic

#### Apply Field Mappings

```python
def apply_tab_field_mappings(
    self,
    person_data: Dict[str, Any],
    tab_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply field mappings from tab config to person data

    Args:
        person_data: Person dict with 'custom_tab_data' array
        tab_config: Program's planning_center_tab_config

    Returns:
        {
          "role_name": "Mentor",
          "status": "active",
          "start_date": "2026-01-15",
          "notes": "Experienced mentor",
          "progress_percentage": 0
        }
    """
    result = {}
    tab_data = person_data.get("custom_tab_data", [])

    # Create field lookup by slug
    fields_by_slug = {}
    for field in tab_data:
        field_attrs = field.get("attributes", {})
        field_def = field_attrs.get("field_definition", {})
        slug = field_def.get("slug")
        if slug:
            fields_by_slug[slug] = field_attrs.get("value")

    # Apply each field mapping
    for mapping in tab_config.get("field_mappings", []):
        pc_slug = mapping.get("pc_field_slug")
        target_type = mapping.get("target_type")
        mapping_rules = mapping.get("mapping_rules")

        if pc_slug not in fields_by_slug:
            continue  # Field not present

        pc_value = fields_by_slug[pc_slug]

        # Apply mapping
        if target_type == "participant_role":
            result["role_name"] = self._apply_mapping_rules(
                pc_value, mapping_rules, "assign_role"
            )
        elif target_type == "participant_status":
            result["status"] = self._apply_mapping_rules(
                pc_value, mapping_rules, "assign_status"
            ) or tab_config.get("default_status", "active")
        elif target_type == "participant_start_date":
            result["start_date"] = pc_value  # Direct mapping
        elif target_type == "participant_end_date":
            result["end_date"] = pc_value
        elif target_type == "participant_notes":
            result["notes"] = pc_value
        elif target_type == "participant_progress":
            result["progress_percentage"] = int(pc_value) if pc_value else 0
        # target_type == "ignore" -> skip

    return result


def _apply_mapping_rules(
    self,
    value: Any,
    rules: Optional[List[Dict[str, Any]]],
    assign_key: str
) -> Any:
    """
    Apply conditional mapping rules

    If rules is None, return value directly (direct mapping)
    Otherwise, find matching rule and return assigned value
    """
    if rules is None:
        return value

    for rule in rules:
        if rule.get("when") == value:
            return rule.get(assign_key)

    return None  # No matching rule
```

### Phase 4: API Endpoints

Add to `backend/app/api/v1/endpoints/programs.py`:

#### Get Available Tabs (Discovery)

```python
@router.get("/planning-center/tabs/{person_id}", response_model=List[Dict])
def get_planning_center_tabs(
    person_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available Planning Center custom tabs for a person
    (Used for configuration UI)
    """
    pc_service = PlanningCenterSyncService(db)
    return pc_service.get_person_tabs(person_id)
```

#### Get Tab Field Definitions

```python
@router.get("/planning-center/tabs/{tab_id}/fields", response_model=List[Dict])
def get_tab_field_definitions(
    tab_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get field definitions for a custom tab
    (Used for mapping configuration UI)
    """
    pc_service = PlanningCenterSyncService(db)
    return pc_service.get_tab_field_definitions(tab_id)
```

#### Import from List with Tab Mapping

```python
@router.post("/participants/bulk-from-pc-list-with-tabs")
def bulk_import_participants_from_pc_list_with_tabs(
    request: BulkImportWithTabsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import participants from Planning Center list using custom tab mappings
    """
    # Validate program exists and user has permission
    program = program_service.get_program(request.program_id)
    if not program:
        raise HTTPException(404, "Program not found")

    if not program.planning_center_tab_config:
        raise HTTPException(400, "Program does not have tab configuration")

    tab_config = program.planning_center_tab_config
    if not tab_config.get("enabled"):
        raise HTTPException(400, "Tab import is not enabled for this program")

    # Get people with tab data
    pc_service = PlanningCenterSyncService(db)
    people_with_tabs = pc_service.get_list_people_with_tab_data(
        request.pc_list_id,
        tab_config["tab_slug"]
    )

    imported = []
    errors = []

    for person in people_with_tabs:
        try:
            # Apply field mappings
            mapped_data = pc_service.apply_tab_field_mappings(
                person,
                tab_config
            )

            # Sync person to local database if needed
            if tab_config.get("sync_on_import", True):
                people_service = PeopleService(db)
                local_person = people_service.sync_person_from_pc(person)
                people_id = local_person.id
            else:
                # Find existing person
                people_id = people_service.get_by_pc_id(person["id"])
                if not people_id:
                    errors.append(f"Person {person['id']} not found locally")
                    continue

            # Create participant with mapped data
            participant_data = {
                "program_id": request.program_id,
                "people_id": people_id,
                **mapped_data
            }

            participant, error = program_service.add_participant(
                participant_data,
                current_user.id
            )

            if participant:
                imported.append(participant)
            else:
                errors.append(f"Failed to add {person['id']}: {error}")

        except Exception as e:
            errors.append(f"Error processing {person.get('id')}: {str(e)}")

    return {
        "imported_count": len(imported),
        "error_count": len(errors),
        "imported": imported,
        "errors": errors
    }
```

### Phase 5: Frontend UI

#### Tab Configuration Component

Create `tab-mapping-dialog.component.ts`:

**Features**:
1. **Tab Selection**: Browse available Planning Center tabs
2. **Field Discovery**: Fetch fields from selected tab
3. **Field Mapping**: Drag-and-drop or dropdown mapping UI
4. **Rule Builder**: Visual interface for conditional mappings
5. **Preview**: Test mapping with sample data
6. **Save**: Store configuration in program

**UI Flow**:

```
1. Admin clicks "Configure PC Tab Import" in program
2. Dialog opens with:
   - Step 1: Select Planning Center Tab (dropdown of available tabs)
   - Step 2: Map Fields
     For each PC field:
       - PC Field Name: "Role"
       - Type: "select"
       - Map to: [dropdown: Role | Status | Start Date | Notes | Ignore]
       - If "Role" selected: Show mapping rules UI
   - Step 3: Preview
     - Fetch sample person data
     - Show: PC Value → Mapped Value
   - Step 4: Save Configuration
```

## Usage Example

### Step 1: Configure Tab Mapping

Admin opens program "Life On Life 2026" and clicks "Configure PC Import":

1. Select tab: "Life On Life Discipleship"
2. Map fields:
   - **Role** (select) → Participant Role
     - "Mentor" → "Mentor"
     - "Mentee" → "Mentee"
     - "Discipler" → "Mentor"
   - **Start Date** (date) → Start Date (direct)
   - **Notes** (text) → Notes (direct)
   - **Is Active** (checkbox) → Status
     - true → "active"
     - false → "paused"
3. Set defaults:
   - Default status: "active"
   - Update existing: No
   - Sync from PC: Yes
4. Save configuration

### Step 2: Import Participants

1. Navigate to "Life On Life 2026" program
2. Click "Import from Planning Center"
3. Select list: "Life on Life Discipleship Roll"
4. Click "Import with Tab Data"
5. System:
   - Fetches all people from list
   - Gets custom tab data for each person
   - Applies field mappings
   - Creates participants with correct roles
6. Shows results: "25 mentors imported, 50 mentees imported"

## Benefits

1. **Flexibility**: Works with any custom tab structure
2. **No Code Changes**: Configuration through UI, no developer needed
3. **Reusable**: Different programs can use different tabs/mappings
4. **Transparent**: Clear mapping preview before import
5. **Maintainable**: Changes to PC tabs don't break imports
6. **Multi-Organization**: Each church can configure their own mappings

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/planning-center/tabs/{person_id}` | Discover available tabs |
| GET | `/planning-center/tabs/{tab_id}/fields` | Get tab field definitions |
| POST | `/programs/{id}/participants/bulk-from-pc-list-with-tabs` | Import with tab mapping |
| PUT | `/programs/{id}` | Update program (includes tab config) |
| GET | `/programs/{id}` | Get program (includes tab config) |

## Configuration Storage

Tab configuration is stored in the `planning_center_tab_config` JSON column of the `programs` table. This allows:

- Per-program configuration
- Version control through git (if exported)
- Easy backup/restore
- API-driven updates

## Future Enhancements

1. **Template Library**: Save/share common mapping configurations
2. **Auto-Detection**: Suggest mappings based on field names
3. **Validation**: Preview errors before import
4. **Scheduled Sync**: Auto-import on schedule with tab mappings
5. **Multi-Tab Support**: Import from multiple tabs per person
6. **Complex Rules**: Support AND/OR logic, regex matching
7. **Custom Scripts**: Allow JavaScript for advanced transformations

## Testing Plan

1. **Unit Tests**:
   - `test_apply_tab_field_mappings()` - Various mapping scenarios
   - `test_mapping_rules()` - Conditional logic
   - `test_direct_mapping()` - Simple value copies

2. **Integration Tests**:
   - Mock Planning Center API responses
   - Test full import flow with sample tab data
   - Verify participant creation with correct fields

3. **E2E Tests**:
   - UI workflow: configure → preview → import
   - Multiple programs with different configs
   - Error handling for invalid mappings

## Migration Path

### For Existing Deployments

1. Run migration: `alembic upgrade head`
2. Existing programs continue working (tab_config is nullable)
3. Admins configure tab mapping on programs that need it
4. Old import methods still work (backward compatible)

### For New Programs

1. During program creation, optionally configure tab import
2. Or configure later through "Edit Program"

## Documentation Links

- Planning Center API: https://developer.planning.center/docs/#/apps/people
- Custom Tabs Endpoint: `/people/v2/people/{id}/tabs`
- Field Data Endpoint: `/people/v2/people/{id}/tabs/{tab_id}/field_data`

---

**Status**: Architecture complete, implementation in progress
**Next Steps**: Implement tab discovery methods in PlanningCenterSyncService
**Estimated Completion**: 2-3 days development + 1 day testing
