# Custom Attributes and Attribute Mapping Documentation

## Overview

The Church Course Tracker now supports **Custom Attributes** - a flexible system for storing and managing additional data fields that don't have direct equivalents in the standard database schema. This is particularly useful when importing data from Planning Center, where custom fields may vary by program or event.

The system includes:
1. **Custom Attributes Storage**: Flexible key-value storage for any entity type
2. **Attribute Mapping UI**: Interactive dialog for mapping Planning Center attributes to CCT fields
3. **Intelligent Matching**: Automatic fuzzy matching of Planning Center attributes to local fields
4. **Planning Center Integration**: Seamless import with attribute mapping decisions

## Table of Contents

- [Custom Attributes System](#custom-attributes-system)
- [Attribute Mapping UI](#attribute-mapping-ui)
- [Planning Center Integration](#planning-center-integration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Database Schema](#database-schema)

---

## Custom Attributes System

### What Are Custom Attributes?

Custom attributes allow you to store additional information about entities (people, courses, programs, enrollments, program participants) that doesn't fit into the standard schema. For example:

- **Program-specific fields**: "Discipler Name", "Testimony Entered?", "SHAPE Profile Entered?"
- **Event-specific fields**: Custom registration questions, special requirements
- **Temporary data**: Fields that may change or be program-specific

### Supported Entity Types

Custom attributes can be attached to:
- `person` - People/members
- `course` - Courses
- `program` - Programs
- `enrollment` - Course enrollments
- `program_participant` - Program participants

### Data Model

Each custom attribute stores:
- **Entity Type**: Which type of entity this belongs to
- **Entity ID**: The specific entity's ID
- **Attribute Name**: The name of the custom attribute (e.g., "discipler_name")
- **Attribute Value**: The actual value (stored as string, can be converted based on type)
- **Attribute Type**: Inferred or specified type (string, integer, date, boolean, json)
- **Source**: Where it came from (e.g., "planning_center", "manual")
- **Planning Center Source ID**: Original PC ID if imported from Planning Center

---

## Attribute Mapping UI

### Overview

When importing participants or enrollments from Planning Center, the system presents an **Attribute Mapping Dialog** that allows you to:

1. **Review** all attributes found in Planning Center
2. **Accept** automatic matches to CCT fields
3. **Remap** attributes to different CCT fields
4. **Save as Custom** attributes that don't have CCT equivalents
5. **Ignore** attributes you don't want to import

### Accessing the Mapping Dialog

The mapping dialog automatically appears when:
- Bulk importing participants from a Planning Center event
- Bulk importing participants from a Planning Center list
- Bulk enrolling from a Planning Center event
- Bulk enrolling from a Planning Center list

### Mapping Options

For each Planning Center attribute, you can choose:

#### 1. Accept Match (for matched attributes)
- **When**: Attribute was automatically matched to a CCT field
- **Action**: Accepts the match and imports the value to the standard CCT field
- **Example**: "first_name" → `first_name` field in People table

#### 2. Remap to Different CCT Attribute
- **When**: You want to map to a different CCT field than suggested
- **Action**: Select a different CCT attribute from the dropdown
- **Example**: "mobile" → `phone` field instead of creating a custom attribute

#### 3. Save as Custom Attribute
- **When**: The attribute doesn't have a CCT equivalent
- **Action**: Creates a new custom attribute with the specified name
- **Example**: "Discipler Name" → Custom attribute `discipler_name`

#### 4. Ignore
- **When**: You don't want to import this attribute
- **Action**: Skips this attribute during import
- **Example**: Internal Planning Center fields you don't need

### Matching Indicators

The UI shows:
- **Matched** (green chip): Automatically matched with confidence score
- **Unmatched** (red chip): No automatic match found

---

## Planning Center Integration

### Import Flow

1. **User initiates bulk import** from Planning Center (event or list)
2. **System fetches PC data** and extracts all attributes
3. **Intelligent matching** runs automatically using fuzzy matching
4. **Mapping dialog appears** with proposed matches
5. **User reviews and decides** for each attribute
6. **Import proceeds** with user's mapping decisions applied

### Intelligent Matching

The system uses:
- **Predefined mappings**: Common field name variations (e.g., "email_address" → "email")
- **Fuzzy matching**: Similarity-based matching using `rapidfuzz` library
- **Confidence scores**: Each match includes a similarity score (0-100%)

See [ATTRIBUTE_MATCHING_IMPLEMENTATION.md](./ATTRIBUTE_MATCHING_IMPLEMENTATION.md) for detailed technical information.

### Example: Importing Program Participants

**Planning Center List Attributes:**
```
- first_name: "John"
- last_name: "Doe"
- email: "john@example.com"
- Discipler Name: "Jane Smith"
- SHAPE Profile Entered?: "Yes"
- Testimony Entered?: "No"
- Date Life on Life Discipleship Started: "2024-01-15"
```

**Mapping Decisions:**
- `first_name` → **Accept** → Maps to `People.first_name`
- `last_name` → **Accept** → Maps to `People.last_name`
- `email` → **Accept** → Maps to `People.email`
- `Discipler Name` → **Save as Custom** → Creates `discipler_name` custom attribute
- `SHAPE Profile Entered?` → **Save as Custom** → Creates `shape_profile_entered` custom attribute
- `Testimony Entered?` → **Save as Custom** → Creates `testimony_entered` custom attribute
- `Date Life on Life Discipleship Started` → **Remap** → Maps to `ProgramParticipant.start_date`

**Result:**
- Person record created with standard fields populated
- Program participant created with `start_date` set
- Three custom attributes created and linked to the participant

---

## API Reference

### Custom Attributes Endpoints

#### Create Custom Attribute
```http
POST /api/v1/custom-attributes/
Content-Type: application/json
Authorization: Bearer <token>

{
  "entity_type": "program_participant",
  "entity_id": 123,
  "attribute_name": "discipler_name",
  "attribute_value": "Jane Smith",
  "attribute_type": "string",
  "source": "planning_center",
  "planning_center_source_id": "pc_person_456"
}
```

#### Get Custom Attributes for Entity
```http
GET /api/v1/custom-attributes/?entity_type=program_participant&entity_id=123
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "entity_type": "program_participant",
    "entity_id": 123,
    "attribute_name": "discipler_name",
    "attribute_value": "Jane Smith",
    "attribute_type": "string",
    "source": "planning_center",
    "planning_center_source_id": "pc_person_456",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### Get Single Custom Attribute
```http
GET /api/v1/custom-attributes/{attribute_id}
Authorization: Bearer <token>
```

#### Update Custom Attribute
```http
PUT /api/v1/custom-attributes/{attribute_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "attribute_value": "Updated Value",
  "attribute_type": "string"
}
```

#### Delete Custom Attribute
```http
DELETE /api/v1/custom-attributes/{attribute_id}
Authorization: Bearer <token>
```

### Attribute Mapping Endpoints

#### Get Attribute Mappings (for review)
```http
GET /api/v1/planning-center/attribute-mappings?source_type=event&source_id=pc_event_123&target_type=course&target_id=456
Authorization: Bearer <token>
```

**Response:**
```json
{
  "source_type": "event",
  "source_id": "pc_event_123",
  "target_type": "course",
  "target_id": 456,
  "mappings": [
    {
      "pc_attribute": "name",
      "local_attribute": "title",
      "similarity_score": 0.95,
      "is_predefined": false,
      "match_status": "matched"
    },
    {
      "pc_attribute": "custom_field_1",
      "local_attribute": null,
      "similarity_score": 0.0,
      "is_predefined": false,
      "match_status": "unmatched"
    }
  ]
}
```

#### Save Attribute Mapping Decisions
```http
POST /api/v1/planning-center/attribute-mappings/decisions
Content-Type: application/json
Authorization: Bearer <token>

{
  "source_type": "event",
  "source_id": "pc_event_123",
  "target_type": "course",
  "target_id": 456,
  "decisions": [
    {
      "pc_attribute": "name",
      "action": "accept",
      "local_attribute": "title",
      "pc_value": "Test Event"
    },
    {
      "pc_attribute": "custom_field_1",
      "action": "custom",
      "custom_attribute_name": "custom_field_1",
      "pc_value": "Custom Value"
    }
  ]
}
```

---

## Usage Examples

### Example 1: Importing with Custom Attributes

**Scenario**: Import program participants from a Planning Center list that includes custom fields.

**Steps:**
1. Navigate to Enrollments Management
2. Select "Programs" view
3. Click "Bulk Import" for a program
4. Select "Import from Planning Center List"
5. Choose the list and role
6. **Attribute Mapping Dialog appears**
7. Review each attribute:
   - Standard fields (name, email) → Accept matches
   - Custom fields (Discipler Name) → Save as Custom
8. Click "Continue Import"
9. Participants are imported with custom attributes stored

### Example 2: Viewing Custom Attributes

**Via API:**
```bash
curl -X GET "https://api.example.com/api/v1/custom-attributes/?entity_type=program_participant&entity_id=123" \
  -H "Authorization: Bearer <token>"
```

**In Frontend:**
- Custom attributes are displayed in participant detail views
- Can be edited through the participant management interface

### Example 3: Using Custom Attributes for Pairing

**Scenario**: Use "Discipler Name" custom attribute to automatically create mentor-mentee pairings.

**Implementation:**
1. Import participants with `discipler_name` as custom attribute
2. System reads `discipler_name` from custom attributes
3. Matches discipler name to participant names
4. Creates program pairings automatically

---

## Database Schema

### Custom Attributes Table

```sql
CREATE TABLE custom_attributes (
    id INTEGER PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    attribute_name VARCHAR(200) NOT NULL,
    pc_attribute_name VARCHAR(200),
    attribute_value TEXT,
    attribute_type VARCHAR(50),
    source VARCHAR(50) NOT NULL DEFAULT 'planning_center',
    planning_center_source_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id)
);

CREATE INDEX ix_custom_attributes_entity ON custom_attributes(entity_type, entity_id);
CREATE INDEX ix_custom_attributes_attribute_name ON custom_attributes(attribute_name);
CREATE INDEX ix_custom_attributes_planning_center_source_id ON custom_attributes(planning_center_source_id);
```

### Key Constraints

- **Entity uniqueness**: Multiple custom attributes can exist for the same entity
- **Attribute name**: Can be repeated (e.g., multiple "notes" attributes)
- **Source tracking**: Tracks where the attribute came from for audit purposes

---

## Best Practices

### Naming Conventions

- Use **snake_case** for custom attribute names (e.g., `discipler_name`, `testimony_entered`)
- Use **descriptive names** that indicate what the attribute represents
- **Avoid conflicts** with standard field names

### When to Use Custom Attributes

✅ **Use custom attributes for:**
- Program-specific fields that vary by program
- Temporary or experimental fields
- Fields that may not apply to all entities
- Planning Center custom fields that don't map to standard fields

❌ **Don't use custom attributes for:**
- Standard fields that should be in the main schema
- Fields that need database-level constraints
- Fields that need to be indexed for frequent queries
- Fields that are required for all entities

### Performance Considerations

- Custom attributes are stored in a separate table
- Queries filtering by custom attributes require JOINs
- Consider adding standard columns for frequently-queried custom attributes
- Use indexes on `entity_type` and `entity_id` for efficient lookups

---

## Troubleshooting

### Attribute Mapping Dialog Not Appearing

**Possible causes:**
- Planning Center API not returning attribute data
- Network issues fetching PC data
- Browser console errors

**Solutions:**
- Check browser console for errors
- Verify Planning Center API connectivity
- Ensure user has proper permissions

### Custom Attributes Not Saving

**Possible causes:**
- Missing required fields in API request
- Permission issues (admin/staff only)
- Database constraint violations

**Solutions:**
- Verify all required fields are provided
- Check user role (must be admin or staff)
- Review database logs for constraint errors

### Incorrect Attribute Matching

**Possible causes:**
- Similarity threshold too low
- Unusual attribute naming in Planning Center
- Missing predefined mappings

**Solutions:**
- Review matches in the mapping dialog
- Manually remap incorrect matches
- Add predefined mappings for common variations

---

## Related Documentation

- [ATTRIBUTE_MATCHING_IMPLEMENTATION.md](./ATTRIBUTE_MATCHING_IMPLEMENTATION.md) - Technical details on fuzzy matching
- [PROGRAM_CUSTOM_ATTRIBUTES_PLAN.md](./PROGRAM_CUSTOM_ATTRIBUTES_PLAN.md) - Original implementation plan
- [README.md](./README.md) - General project documentation

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API error messages in browser console
3. Check application logs for backend errors
4. Contact the development team

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0




