# Program Business Object - Detailed Design

## Requirements Summary

1. ✅ **Multiple roles** (not just 2) - flexible role system
2. ✅ **Multiple mentees allowed** - configurable relationship constraints per program
3. ✅ **Own content** - programs have their own content, but content should be reusable across courses and programs
4. ✅ **Program administrators** - one or more admins who can set up pairings
5. ✅ **Flexible progress** - track content completion OR session completion
6. ✅ **Same attributes as courses** - all optional except name/description
7. ✅ **Planning Center integration** - needed

## Data Model Design

### 1. Program Table
```python
class Program(Base):
    """Program model - Ongoing mentoring/discipleship programs"""
    
    __tablename__ = "programs"
    
    id: int
    title: str  # Required
    description: Text  # Required
    
    # Flexible role system
    role_definitions: JSON  # [
    #   {"name": "Mentor", "min_participants": 1, "max_participants": 1, "is_primary": true},
    #   {"name": "Mentee", "min_participants": 1, "max_participants": 3, "is_primary": false}
    # ]
    
    # Relationship configuration
    relationship_config: JSON  # {
    #   "allow_multiple_secondary": true,  # Can one primary have multiple secondary?
    #   "max_secondary_per_primary": 3,  # Max secondary participants per primary
    #   "require_pairing": true  # Must participants be explicitly paired?
    # }
    
    # Optional attributes (same as courses)
    locations: JSON  # Optional
    delivery_modes: JSON  # Optional
    prerequisites: JSON  # Optional (could reference other programs or courses)
    
    # Planning Center integration
    planning_center_event_template_id: String  # Optional
    planning_center_event_id: String  # Optional
    planning_center_event_name: String  # Optional
    
    is_active: Boolean
    
    # Relationships
    program_admins: relationship("ProgramAdmin")  # Administrators
    program_participants: relationship("ProgramParticipant")
    program_content: relationship("ProgramContent")
    program_pairings: relationship("ProgramPairing")
    program_sessions: relationship("ProgramSession")
    
    created_at: DateTime
    updated_at: DateTime
    created_by: int
    updated_by: int
```

### 2. ProgramAdmin Table
```python
class ProgramAdmin(Base):
    """Program administrators who can manage pairings and participants"""
    
    __tablename__ = "program_admins"
    
    id: int
    program_id: int  # Foreign key to Program
    user_id: int  # Foreign key to User
    
    # Permissions (for future expansion)
    can_manage_participants: Boolean = True
    can_manage_pairings: Boolean = True
    can_manage_content: Boolean = True
    
    created_at: DateTime
    created_by: int
```

### 3. ProgramParticipant Table
```python
class ProgramParticipant(Base):
    """People participating in a program with a specific role"""
    
    __tablename__ = "program_participants"
    
    id: int
    program_id: int  # Foreign key to Program
    people_id: int  # Foreign key to People
    
    role_name: str  # e.g., "Mentor", "Mentee" - must match role_definitions in Program
    
    start_date: DateTime
    end_date: DateTime  # Nullable (for active participants)
    status: str  # "active", "paused", "completed", "ended"
    
    notes: Text
    
    # Progress summary
    progress_percentage: Float  # 0-100
    last_activity_date: DateTime
    
    created_at: DateTime
    updated_at: DateTime
    created_by: int
    updated_by: int
```

### 4. ProgramPairing Table
```python
class ProgramPairing(Base):
    """Explicit pairing between participants (e.g., Mentor-Mentee relationship)"""
    
    __tablename__ = "program_pairings"
    
    id: int
    program_id: int  # Foreign key to Program
    
    primary_participant_id: int  # Foreign key to ProgramParticipant (e.g., Mentor)
    secondary_participant_id: int  # Foreign key to ProgramParticipant (e.g., Mentee)
    
    # Relationship details
    start_date: DateTime
    end_date: DateTime  # Nullable (for active pairings)
    status: str  # "active", "paused", "completed", "ended"
    
    notes: Text
    
    created_at: DateTime
    updated_at: DateTime
    created_by: int  # Program admin who created the pairing
    updated_by: int
```

### 5. ProgramContent Table
```python
class ProgramContent(Base):
    """Content items for programs (similar to CourseContent but for programs)"""
    
    __tablename__ = "program_content"
    
    id: int
    program_id: int  # Foreign key to Program
    
    # Reference to shared content (if reusable)
    shared_content_id: int  # Foreign key to SharedContent (optional)
    
    # OR program-specific content (if not shared)
    title: str
    description: Text
    content_type: Enum(ContentType)
    storage_type: Enum(StorageType)
    
    # File information
    file_name: String
    file_size: Integer
    file_path: String
    mime_type: String
    
    # External content
    external_url: String
    embedded_content: Text
    
    # Metadata
    duration: Integer
    order_index: Integer
    is_active: Boolean
    
    created_at: DateTime
    updated_at: DateTime
    created_by: int
    updated_by: int
```

### 6. SharedContent Table (NEW - for reusability)
```python
class SharedContent(Base):
    """Shared content library that can be used by both courses and programs"""
    
    __tablename__ = "shared_content"
    
    id: int
    title: str
    description: Text
    content_type: Enum(ContentType)
    storage_type: Enum(StorageType)
    
    # File information
    file_name: String
    file_size: Integer
    file_path: String
    mime_type: String
    
    # External content
    external_url: String
    embedded_content: Text
    
    # Metadata
    duration: Integer
    is_active: Boolean
    
    # Usage tracking
    used_in_courses: JSON  # List of course IDs using this content
    used_in_programs: JSON  # List of program IDs using this content
    
    created_at: DateTime
    updated_at: DateTime
    created_by: int
    updated_by: int
```

### 7. ProgramSession Table
```python
class ProgramSession(Base):
    """Logs meetings/sessions between participants"""
    
    __tablename__ = "program_sessions"
    
    id: int
    program_id: int
    pairing_id: int  # Foreign key to ProgramPairing (optional - could be group session)
    
    # Session details
    session_date: DateTime
    duration_minutes: Integer
    location: String  # Optional
    session_type: str  # "in_person", "online", "phone", etc.
    
    # Participants who attended
    participant_ids: JSON  # List of ProgramParticipant IDs
    
    # Session content/topics
    topics_covered: Text
    notes: Text
    
    # Progress tracking
    content_completed: JSON  # List of ProgramContent IDs completed in this session
    milestones_achieved: JSON  # List of milestone IDs
    
    created_at: DateTime
    created_by: int  # Who logged the session
```

### 8. ProgramProgress Table
```python
class ProgramProgress(Base):
    """Flexible progress tracking for programs"""
    
    __tablename__ = "program_progress"
    
    id: int
    program_id: int
    participant_id: int  # Foreign key to ProgramParticipant
    
    # Progress type
    progress_type: str  # "content_completion", "session_completion", "milestone"
    
    # Content completion (if progress_type is "content_completion")
    content_id: int  # Foreign key to ProgramContent (optional)
    completion_date: DateTime
    completion_percentage: Integer  # 0-100
    
    # Session completion (if progress_type is "session_completion")
    session_id: int  # Foreign key to ProgramSession (optional)
    
    # Milestone (if progress_type is "milestone")
    milestone_name: str  # Optional
    milestone_description: Text  # Optional
    
    notes: Text
    
    created_at: DateTime
    created_by: int
```

## Key Design Decisions

### 1. Flexible Role System
- **Role Definitions**: Stored as JSON in Program table
- Each role has: name, min_participants, max_participants, is_primary flag
- Allows any number of roles per program
- Example:
  ```json
  [
    {"name": "Mentor", "min_participants": 1, "max_participants": 1, "is_primary": true},
    {"name": "Mentee", "min_participants": 1, "max_participants": 3, "is_primary": false},
    {"name": "Observer", "min_participants": 0, "max_participants": 5, "is_primary": false}
  ]
  ```

### 2. Relationship Configuration
- **relationship_config** JSON field defines:
  - Can one primary have multiple secondary? (yes/no)
  - Max secondary per primary (number)
  - Require explicit pairing? (yes/no)
- Validated when creating pairings

### 3. Content Reusability
- **SharedContent** table for reusable content
- **ProgramContent** can reference SharedContent OR have program-specific content
- **CourseContent** can also reference SharedContent
- Allows content to be used in both courses and programs

### 4. Program Administrators
- **ProgramAdmin** table links Users to Programs
- Admins can manage participants, pairings, and content
- Created by program creator or other admins

### 5. Flexible Progress Tracking
- **ProgramProgress** table supports multiple progress types:
  - Content completion (like courses)
  - Session completion (new)
  - Custom milestones
- **ProgramSession** tracks meetings with optional content completion

### 6. Pairing Management
- **ProgramPairing** explicitly links participants
- Supports 1:1 and 1:many relationships
- Validated against relationship_config
- Created by program admins

## Implementation Phases

### Phase 1: Core Models
1. Program model with role definitions and relationship config
2. ProgramAdmin model
3. ProgramParticipant model
4. ProgramPairing model

### Phase 2: Content System
1. SharedContent model
2. ProgramContent model (with shared content reference)
3. Update CourseContent to optionally reference SharedContent

### Phase 3: Progress & Sessions
1. ProgramSession model
2. ProgramProgress model
3. Progress tracking logic

### Phase 4: Planning Center Integration
1. Add Planning Center fields to Program
2. Sync logic for programs

### Phase 5: Frontend
1. Program management UI
2. Participant management
3. Pairing management
4. Content management
5. Session logging
6. Progress tracking

## Questions for Clarification

1. **SharedContent**: Should existing CourseContent be automatically available as SharedContent, or should it be a separate library that content is explicitly added to?

2. **Role Validation**: Should we validate that participants match the role definitions when they're added? (e.g., ensure "Mentor" role exists in program's role_definitions)

3. **Pairing Constraints**: Should the system enforce relationship_config constraints (e.g., prevent creating more than max_secondary_per_primary), or just warn?

4. **Session Attendance**: Should we track which participants attended each session, or is it assumed all paired participants attend?

5. **Progress Calculation**: How should overall progress_percentage be calculated?
   - Based on content completion?
   - Based on sessions completed?
   - Custom formula per program?

6. **Content Organization**: Should ProgramContent support modules (like CourseModule), or just flat content items?

## Next Steps

Once you confirm this design, I'll:
1. Create the database models
2. Create the migrations
3. Create the Pydantic schemas
4. Create the service layer
5. Create the API endpoints
6. Create the frontend components

Would you like me to proceed with this design, or do you have any modifications?


