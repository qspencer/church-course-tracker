# Program Business Object - Design Proposal

## Overview
A **Program** is similar to a Course but designed for ongoing, flexible mentoring/discipleship relationships rather than structured courses with fixed durations.

## Key Differences from Courses

| Feature | Course | Program |
|---------|--------|---------|
| Duration | Fixed (weeks) | Indefinite (ongoing) |
| Relationship Model | Many students : Few teachers | Flexible (e.g., 1:1 mentoring) |
| Schedule | Set schedule | Flexible, established by participants |
| Role Terminology | Fixed ("Instructor", "Student") | Customizable (e.g., "Mentor"/"Mentee") |
| Completion | Has completion date | Ongoing, no completion |

## Proposed Data Model

### Program Table
```python
class Program(Base):
    id: int
    title: str  # e.g., "Discipleship Program", "Mentoring Program"
    description: Text
    
    # Customizable role names
    primary_role_name: str  # e.g., "Mentor", "Teacher", "Coach" (default: "Teacher")
    secondary_role_name: str  # e.g., "Mentee", "Student", "Coachee" (default: "Student")
    
    # Curriculum - can reference courses or have own content
    curriculum_course_ids: JSON  # List of course IDs that form the curriculum
    # OR
    program_content: relationship("ProgramContent")  # Similar to CourseContent
    
    # Attributes (similar to courses but adapted)
    locations: JSON  # Optional locations
    delivery_modes: JSON  # Optional delivery modes
    is_active: Boolean
    
    # No duration_weeks (programs are ongoing)
    # No prerequisites (or make optional)
    
    # Relationships
    program_participants: relationship("ProgramParticipant")
    program_content: relationship("ProgramContent")
```

### ProgramParticipant Table (instead of Enrollment)
```python
class ProgramParticipant(Base):
    id: int
    program_id: int  # Foreign key to Program
    people_id: int  # Foreign key to People
    
    role: str  # "primary" or "secondary" (maps to primary_role_name/secondary_role_name)
    # OR use the actual role name from program
    
    # Pairing/Relationship tracking
    paired_with_id: int  # Foreign key to another ProgramParticipant (for 1:1 relationships)
    # OR use a separate ProgramPairing table for more flexibility
    
    start_date: DateTime
    status: str  # "active", "paused", "completed", "ended"
    notes: Text
    
    # Progress tracking (similar to enrollment but for programs)
    progress_percentage: Float
    last_activity_date: DateTime
```

## Design Questions & Considerations

### 1. Role Terminology Flexibility
**Question**: How flexible should the role naming be?
- **Option A**: Two configurable role names per program (primary/secondary)
  - Simple, covers most cases
  - Example: "Mentor" and "Mentee"
- **Option B**: Multiple roles with custom names
  - More flexible but more complex
  - Example: Could have "Mentor", "Mentee", "Observer" roles

**Recommendation**: Start with Option A (two roles), can expand later if needed.

### 2. Relationship Model
**Question**: Should we support only 1:1 relationships or allow flexibility?
- **Option A**: Strict 1:1 (one primary role : one secondary role)
  - Matches your current use case
  - Simpler to implement
- **Option B**: Flexible (one primary can have multiple secondary, or vice versa)
  - More flexible for future needs
  - More complex to manage

**Recommendation**: Start with Option B (flexible) but design UI to make 1:1 easy.

### 3. Curriculum/Content
**Question**: How should programs reference curriculum?
- **Option A**: Programs reference existing Courses as curriculum
  - Reuse existing course content
  - Programs become "playlists" of courses
- **Option B**: Programs have their own content (similar to CourseContent)
  - More independent
  - Can have program-specific content
- **Option C**: Both - can reference courses AND have own content
  - Maximum flexibility
  - Most complex

**Recommendation**: Option C (both) for maximum flexibility, but start simple.

### 4. Pairing/Relationship Tracking
**Question**: How should we track who is paired with whom?
- **Option A**: `paired_with_id` in ProgramParticipant
  - Simple for 1:1 relationships
  - Works well for your use case
- **Option B**: Separate `ProgramPairing` table
  - More flexible (could support group pairings later)
  - Better for many-to-many relationships
- **Option C**: Use role + program_id to infer pairs
  - Simplest but less explicit

**Recommendation**: Option B (separate table) for future flexibility, but can start with Option A.

### 5. Schedule/Sessions
**Question**: Should we track meetings/sessions even though there's no set schedule?
- **Option A**: No schedule tracking
  - Simplest, matches "no set schedule" requirement
- **Option B**: Optional session tracking
  - Can log meetings when they happen
  - Useful for accountability and progress tracking
  - Doesn't enforce a schedule, just records it

**Recommendation**: Option B (optional session tracking) - useful for reporting without enforcing schedule.

### 6. Progress Tracking
**Question**: How should progress be tracked?
- Similar to course enrollments? (progress_percentage, content completion)
- Or simpler? (just active/inactive status)

**Recommendation**: Similar to courses but adapted for ongoing nature.

### 7. Attributes from Courses
**Question**: Which course attributes should programs have?
- ✅ Title, Description
- ✅ Custom role names
- ✅ Locations? (probably yes, for flexibility)
- ✅ Delivery modes? (probably yes)
- ❌ Duration (programs are indefinite)
- ❌ Instructors (handled via participants)
- ❌ Prerequisites? (probably not, or make optional)
- ❌ Planning Center integration? (probably not needed)

## Proposed Implementation Plan

### Phase 1: Core Program Model
1. Create `Program` model with:
   - Basic info (title, description)
   - Custom role names (primary_role_name, secondary_role_name)
   - Curriculum reference (course_ids JSON or relationship)
   - Similar attributes to courses (locations, delivery_modes, is_active)

2. Create `ProgramParticipant` model:
   - Links person to program
   - Role assignment (primary/secondary)
   - Status tracking
   - Start date, notes

3. Create `ProgramPairing` model (optional, for 1:1 relationships):
   - Links two participants together
   - Start date, status
   - Notes

### Phase 2: Content/Curriculum
- Decide on curriculum approach (reference courses vs own content)
- Implement chosen approach

### Phase 3: Progress & Tracking
- Progress tracking for programs
- Optional session/meeting logging
- Reporting

## Questions for You

1. **Role Flexibility**: Do you need just two roles (e.g., "Mentor"/"Mentee") or could there be more roles in the future?

2. **Relationship Model**: Is it always 1:1, or could there be cases where one mentor has multiple mentees (or vice versa)?

3. **Curriculum**: Should programs reference existing courses as curriculum, have their own content, or both?

4. **Pairing**: How explicit should the pairing be? Should we have a "pairing" concept, or just track participants and infer pairs from roles?

5. **Schedule/Sessions**: Even though there's no set schedule, would it be useful to optionally log meetings/sessions when they occur?

6. **Attributes**: Which course attributes should programs inherit? (locations, delivery_modes, etc.)

7. **Planning Center**: Do programs need Planning Center integration, or are they purely internal?

8. **Content Sharing**: Can the same content be used in both courses and programs, or should they be separate?

## Recommendation Summary

Based on your description, I recommend:

1. **Two customizable role names** per program (simple, covers your needs)
2. **Flexible relationship model** (support 1:1 but allow flexibility)
3. **ProgramPairing table** for explicit 1:1 tracking
4. **Reference courses as curriculum** (reuse existing content)
5. **Optional session tracking** (log meetings without enforcing schedule)
6. **Similar attributes to courses** (locations, delivery_modes) for consistency
7. **No duration, no prerequisites** (programs are ongoing and flexible)

Would you like me to proceed with this design, or do you have preferences on the questions above?


