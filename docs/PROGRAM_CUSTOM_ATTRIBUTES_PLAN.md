# Program Participant Custom Attributes Implementation Plan

## Overview
This plan outlines how to capture and manage both common program fields and program-specific custom attributes from Planning Center lists when importing participants. 

**Important**: The "Discipler Name" field will be used to automatically determine participant roles and create pairings between mentors (disciplers) and mentees (those being discipled).

## Current State Analysis

### Existing Fields in `ProgramParticipant` Model:
- ✅ `start_date` - Already exists (maps to "Date Life on Life Discipleship Started")
- ✅ `end_date` - Already exists (could map to "Date Life on Life Discipleship Completed")
- ✅ `status` - Already exists (active, paused, completed, ended)
- ✅ `notes` - Already exists (could store text fields)
- ✅ `progress_percentage` - Already exists
- ✅ `role_name` - Already exists

### Planning Center List Attributes to Capture:

#### Common/Standard Fields (should be added to model):
1. **`completion_date`** - Date program was completed (different from `end_date` which could be pause/end)
   - Maps to: "Date Life on Life Discipleship Completed"
   - Type: DateTime (nullable)
   - Purpose: Track actual completion vs. end/pause dates

#### Program-Specific Custom Fields (stored in JSON):
1. **`discipler_name`** - Name of the discipler/mentor
   - Maps to: "Discipler Name"
   - Type: String
   - Program-specific: Yes (Life on Life specific)

2. **`shape_profile_entered`** - Whether SHAPE profile was completed
   - Maps to: "SHAPE Profile Entered?"
   - Type: Boolean
   - Program-specific: Yes (Life on Life specific)

3. **`testimony_entered`** - Whether testimony was entered
   - Maps to: "Testimony Entered?"
   - Type: Boolean
   - Program-specific: Yes (Life on Life specific)

4. **`testimony_text`** - The actual testimony text
   - Maps to: "Life on Life Testimony"
   - Type: Text
   - Program-specific: Yes (Life on Life specific)

5. **`publish_testimony_permission`** - Permission to publish testimony
   - Maps to: "Would you allow us to publish your testimony?"
   - Type: Boolean
   - Program-specific: Yes (Life on Life specific)

6. **`started_discipling_date`** - Date they started discipling someone else
   - Maps to: "Date Started Discipling Someone Else"
   - Type: DateTime
   - Program-specific: Yes (Life on Life specific)

## Implementation Plan

### Phase 1: Database Schema Updates

#### 1.1 Add Common Fields to `ProgramParticipant` Model
```python
# Add to backend/app/models/program.py
completion_date = Column(DateTime(timezone=True), nullable=True)  # Actual completion date
```

#### 1.2 Add Custom Attributes JSON Column
```python
# Add to backend/app/models/program.py
custom_attributes = Column(JSON, nullable=True)  # Store program-specific fields
```

**Structure of `custom_attributes` JSON:**
```json
{
  "discipler_name": "Mike Laramee",
  "shape_profile_entered": false,
  "testimony_entered": false,
  "testimony_text": null,
  "publish_testimony_permission": null,
  "started_discipling_date": "2025-07-11T00:00:00Z"
}
```

#### 1.3 Create Migration
- Create Alembic migration to add `completion_date` and `custom_attributes` columns
- Make both nullable to support existing records

### Phase 2: Backend Schema Updates

#### 2.1 Update Pydantic Schemas
- Add `completion_date` to `ProgramParticipantBase`, `ProgramParticipantCreate`, `ProgramParticipantUpdate`
- Add `custom_attributes: Optional[Dict[str, Any]]` to response schema
- Add validation for custom attributes structure

#### 2.2 Program-Level Field Mapping Configuration
Add to `Program` model a field mapping configuration:
```python
# In Program model
field_mapping_config = Column(JSON, nullable=True)  # Maps PC list fields to our fields
```

**Example mapping config for "Life on Life Discipleship":**
```json
{
  "standard_fields": {
    "start_date": "Date Life on Life Discipleship Started",
    "completion_date": "Date Life on Life Discipleship Completed"
  },
  "custom_fields": {
    "discipler_name": "Discipler Name",
    "shape_profile_entered": "SHAPE Profile Entered?",
    "testimony_entered": "Testimony Entered?",
    "testimony_text": "Life on Life Testimony",
    "publish_testimony_permission": "Would you allow us to publish your testimony?",
    "started_discipling_date": "Date Started Discipling Someone Else"
  },
  "field_types": {
    "discipler_name": "string",
    "shape_profile_entered": "boolean",
    "testimony_entered": "boolean",
    "testimony_text": "text",
    "publish_testimony_permission": "boolean",
    "started_discipling_date": "date"
  }
}
```

### Phase 3: Import Service Updates

#### 3.1 Enhance `get_list_people` to Include Field Values
- Modify `PlanningCenterSyncService.get_list_people()` to fetch field values
- PC API endpoint: `/people/v2/lists/{list_id}/people` with `include=field_values`

#### 3.2 Create Field Mapping Service
Create `FieldMappingService` to:
- Map PC field names to our field names using program's `field_mapping_config`
- Convert PC field values to appropriate types (string, boolean, date, etc.)
- Handle "No answer given" and null values

#### 3.3 Create Role Detection Service
Create `RoleDetectionService` to:
- Parse "Discipler Name" field from imported participants
- Match discipler names to People records (fuzzy matching if needed)
- Determine roles:
  - If person has a discipler → Role = "Mentee" (or secondary role)
  - If person is listed as discipler for others → Role = "Mentor" (or primary role)
  - If person is both → May need both roles or primary role with multiple pairings
- Handle edge cases:
  - Discipler name not found in system
  - Discipler not yet imported (defer pairing creation)
  - Ambiguous name matches (multiple people with same name)

#### 3.4 Update Bulk Import Logic
In `ProgramService.bulk_import_participants_from_pc_list()`:
1. Fetch field values from PC list person data
2. Use program's field mapping config to map fields
3. Extract standard fields (start_date, completion_date) to direct columns
4. Store custom fields in `custom_attributes` JSON
5. Handle date parsing for all date fields
6. **NEW**: Detect roles from discipler relationships:
   - First pass: Import all participants with detected roles
   - Second pass: Create pairings based on discipler relationships
7. **NEW**: Create automatic pairings:
   - For each participant with a discipler:
     - Find discipler participant record
     - Create ProgramPairing with:
       - `primary_participant_id` = discipler participant
       - `secondary_participant_id` = mentee participant
       - `program_id` = current program
       - `status` = "active"
       - `start_date` = participant's start_date

### Phase 4: API Updates

#### 4.1 Update Endpoints
- Ensure `ProgramParticipant` response includes `completion_date` and `custom_attributes`
- Add endpoint to update custom attributes: `PUT /programs/{program_id}/participants/{participant_id}/custom-attributes`

#### 4.2 Update Bulk Import Endpoints
- Accept field mapping overrides in import request (optional)
- Return summary of mapped fields in response

### Phase 5: Frontend Updates

#### 5.1 Display Custom Attributes
- Update participant detail views to show custom attributes
- Group by program (since attributes are program-specific)
- Render fields based on type (text, boolean, date)

#### 5.2 Import UI Enhancements
- Show field mapping preview before import
- Allow manual field mapping configuration
- Display which fields will be imported/mapped

#### 5.3 Participant Management
- Add form to edit custom attributes
- Validate based on program's field mapping config
- Show/hide fields based on program configuration

## Data Flow

### Import Flow:
```
1. User selects PC list and program for import
2. System fetches PC list people with field_values
3. System loads program's field_mapping_config
4. **First Pass - Import Participants:**
   For each person:
   a. Map standard fields (start_date, completion_date) → direct columns
   b. Extract "Discipler Name" field
   c. Detect role based on discipler relationship:
      - Has discipler? → Role = "Mentee" (or program's secondary role name)
      - Is discipler? → Role = "Mentor" (or program's primary role name)
   d. Map custom fields → custom_attributes JSON (including discipler_name)
   e. Create/update ProgramParticipant with detected role
   
5. **Second Pass - Create Pairings:**
   For each participant with a discipler_name:
   a. Match discipler_name to People record (by full name)
   b. Find discipler's ProgramParticipant record in this program
   c. If both found, create ProgramPairing:
      - primary_participant_id = discipler participant
      - secondary_participant_id = mentee participant
      - status = "active"
      - start_date = mentee's start_date
   d. Track errors for unmapped discipler names
   
6. Return import summary including:
   - Participants imported
   - Pairings created
   - Warnings for unmatched discipler names
```

### Display Flow:
```
1. Load ProgramParticipant with custom_attributes
2. Load program's field_mapping_config
3. Render standard fields (start_date, completion_date)
4. Render custom fields based on mapping config and types
```

## Field Type Handling

### Standard Types:
- **String**: Direct mapping
- **Boolean**: Convert "Yes"/"No"/"No answer given" → true/false/null
- **Date**: Parse PC date format → DateTime
- **Text**: Direct mapping (multi-line text)

### Null/Empty Handling:
- "No answer given" → `null` in database
- Empty strings → `null` for optional fields
- Empty dates → `null`

## Configuration Strategy

### Option A: Program-Level Configuration (Recommended)
- Each program defines its field mapping in `field_mapping_config`
- Flexible, allows different programs to have different fields
- Can be configured via UI when creating/editing programs

### Option B: Global Field Mapping
- Single global mapping configuration
- Less flexible, but simpler to manage
- Not recommended for multiple programs with different needs

## Migration Strategy

### For Existing Participants:
- `completion_date` defaults to `null`
- `custom_attributes` defaults to `null` or `{}`
- Can backfill via import if PC data is re-imported

### Backward Compatibility:
- All new fields are nullable
- Existing code continues to work
- New features gracefully handle missing data

## Testing Considerations

1. **Unit Tests:**
   - Field mapping logic
   - Type conversion (boolean, date parsing)
   - Null handling

2. **Integration Tests:**
   - End-to-end import with field mapping
   - Custom attributes storage/retrieval
   - Update operations

3. **Edge Cases:**
   - Missing field mapping config
   - Unknown field types
   - Malformed date strings
   - Special characters in text fields

## Future Enhancements

1. **Field Validation Rules**: Add validation rules to field mapping config
2. **Field Dependencies**: Define relationships between fields (e.g., testimony_text required if testimony_entered=true)
3. **Bulk Updates**: Allow bulk updating of custom attributes
4. **Export**: Export custom attributes back to PC lists
5. **Field Templates**: Create reusable field mapping templates for similar programs

## Implementation Priority

### High Priority (Phase 1-2):
1. Add `completion_date` and `custom_attributes` columns
2. Update schemas
3. Enhance import to fetch and store field values
4. Basic field mapping for Life on Life program
5. **NEW**: Role detection from discipler relationships
6. **NEW**: Automatic pairing creation during import

### Medium Priority (Phase 3-4):
1. Program-level field mapping configuration
2. Field type handling and validation
3. API endpoints for custom attributes
4. Discipler name matching improvements (fuzzy matching for edge cases)

### Low Priority (Phase 5):
1. Frontend UI for custom attributes
2. Field mapping configuration UI
3. Advanced validation and dependencies
4. UI for reviewing/editing auto-created pairings

## Questions to Resolve

1. **Date Field for Completion**: Should `completion_date` be separate from `end_date`, or can we use `end_date` when status="completed"?
   - **Recommendation**: Keep separate - `end_date` could be pause date, `completion_date` is actual completion

2. **Custom Attributes vs. Direct Columns**: Should program-specific fields always go in JSON, or add columns for common ones?
   - **Recommendation**: Use JSON for flexibility, add columns only for fields used across many programs

3. **Field Mapping UI**: When should field mapping be configured? During program creation or during import?
   - **Recommendation**: During import first, then save to program for future imports

4. **Updating Existing Participants**: Should re-import update custom attributes?
   - **Recommendation**: Yes, if `update_existing=True`, update both standard and custom fields

5. **Role Detection Logic**: How should we handle people who are both disciplers and being discipled?
   - **Option A**: Assign primary role (Mentor) and create pairings where they're secondary
   - **Option B**: Support multiple roles per participant (would require schema changes)
   - **Option C**: Create separate participant records for each role (not recommended)
   - **Recommendation**: Option A - assign based on their primary function (if they're discipling others, they're primarily a Mentor)

6. **Discipler Name Matching**: How strict should name matching be?
   - **Option A**: Exact match only (first_name + last_name)
   - **Option B**: Fuzzy matching (handles typos, variations)
   - **Option C**: Allow manual mapping for ambiguous cases
   - **Recommendation**: Start with Option A, add fuzzy matching if needed, provide manual resolution UI

7. **Pairing Creation**: Should we create pairings if discipler hasn't been imported yet?
   - **Option A**: Create participant only, skip pairing (can be created later)
   - **Option B**: Defer pairing creation until discipler is imported
   - **Option C**: Attempt to import discipler if found in PC
   - **Recommendation**: Option A + C - try to find and import discipler, but don't fail if not found

## Next Steps - Investigation Needed

### Planning Center API Research Required:
1. **Field Values Endpoint**: Need to verify the exact endpoint and parameters for fetching list person field values
   - Likely: `GET /people/v2/lists/{list_id}/people/{person_id}/field_data` or similar
   - Or: Field values included in list people response with `?include=field_data` parameter
   - Need to test actual API response structure

2. **Field Data Structure**: Need to understand the structure of field values in PC API:
   - How are field values nested in the response?
   - What is the structure for different field types (text, date, boolean, etc.)?
   - How are field definitions (names, IDs) structured?

3. **Testing Required**: 
   - Make test API calls to PC to see actual response structure
   - Document field value structure for implementation

## Recommended Implementation Order

### Step 1: Research & Prototype (1-2 days)
1. Test Planning Center API calls to understand field values structure
2. Create prototype code to extract and parse field values
3. Document field mapping patterns
4. **NEW**: Test discipler name matching logic with sample data

### Step 2: Database Schema (1 day)
1. Create migration for `completion_date` and `custom_attributes`
2. Add to model and schemas
3. Test migration

### Step 3: Import Logic - Phase 1 (2-3 days)
1. Enhance `get_list_people` to fetch field values
2. Create field mapping service
3. Update bulk import to map and store custom attributes
4. Add program-level field mapping config

### Step 3: Import Logic - Phase 2 (2-3 days) **NEW**
1. Create role detection service:
   - Parse discipler_name from custom_attributes
   - Match discipler names to People records
   - Determine roles (Mentor vs. Mentee)
2. Update bulk import to detect and assign roles automatically
3. Create pairing creation service:
   - Match discipler participants to mentee participants
   - Create ProgramPairing records automatically
   - Handle edge cases (missing discipler, ambiguous matches)
4. Add import summary with pairing creation statistics

### Step 4: API & Frontend (2-3 days)
1. Update API responses to include custom attributes
2. Create UI to display custom attributes
3. Add import summary showing:
   - Participants imported
   - Pairings auto-created
   - Warnings for unmatched disciplers
4. Add field mapping configuration UI (optional for v1)

## Summary

This plan provides a flexible, scalable approach to capturing both common program fields and program-specific attributes. The key design decisions:

- **Standard Fields**: Use direct database columns for common fields (`completion_date`)
- **Custom Fields**: Use JSON column for program-specific flexibility
- **Field Mapping**: Store mapping configuration at program level for flexibility
- **Type Safety**: Convert PC field values to appropriate types during import
- **Automatic Role Detection**: Parse "Discipler Name" to determine participant roles (Mentor/Mentee)
- **Automatic Pairing Creation**: Create ProgramPairing records automatically based on discipler relationships

**Critical Enhancement**: The "Discipler Name" field enables automatic role assignment and pairing creation, which significantly streamlines the import process for mentorship/discipleship programs like "Life on Life Discipleship".

The implementation can be done incrementally, starting with basic field capture and expanding to role detection and pairing creation as needed.

