# Course Attributes Research

## Current Course Attributes

Your current Course model has:
1. **title** - Course name/title
2. **description** - Course description
3. **duration_weeks** - Duration in weeks
4. **prerequisites** - List of prerequisite course IDs
5. **is_active** - Whether the course is active
6. **content_unlock_mode** - How content is unlocked ('immediate' or 'progressive')
7. **max_file_size_mb** - Maximum file size for uploads
8. **planning_center_event_template_id** - Integration with Planning Center
9. **data_source** - Source of data (csv, api, manual)
10. **csv_loaded_at** - When loaded from CSV
11. **created_at/updated_at** - Timestamps
12. **created_by/updated_by** - Audit fields

## Commonly Found Course Attributes in LMS Systems

Based on research of major LMS platforms (Moodle, Canvas, Blackboard, etc.) and educational systems, here are additional attributes commonly found:

### Core Course Information
- **Course Code/Number** - Unique identifier (e.g., "BIB101", "FAITH-101")
- **Short Name/Abbreviation** - Short form for display (e.g., "Intro Faith")
- **Category/Department** - Organizational grouping (e.g., "Bible Study", "Discipleship", "Ministry Training")
- **Level** - Difficulty level (e.g., "Beginner", "Intermediate", "Advanced")
- **Language** - Language of instruction
- **Tags/Keywords** - For searchability and filtering

### Scheduling & Delivery
- **Start Date** - When the course begins (you have this in CourseInstance)
- **End Date** - When the course ends (you have this in CourseInstance)
- **Schedule** - Days/times when sessions occur (e.g., "Tuesdays 7-9 PM")
- **Location** - Physical or virtual location (e.g., "Room 101", "Online", "Zoom")
- **Mode of Delivery** - "In-person", "Online", "Hybrid", "Self-paced"
- **Time Zone** - For scheduling consistency

### Capacity & Enrollment
- **Max Capacity** - Maximum enrollments (you have this, but it's deprecated on Course)
- **Min Enrollment** - Minimum required to run the course
- **Waitlist Enabled** - Whether to allow waitlisting
- **Enrollment Type** - "Open", "Closed", "Invitation Only", "Approval Required"
- **Enrollment Start Date** - When enrollment opens
- **Enrollment End Date** - When enrollment closes

### Instructional
- **Instructor/Teacher** - Primary instructor (could be User ID or name)
- **Co-Instructors** - Additional instructors
- **Learning Objectives** - What students will learn (array of objectives)
- **Syllabus** - Detailed course outline/syllabus (could be text or file)
- **Course Materials** - Required materials list
- **Resources** - Links to external resources

### Assessment & Completion
- **Completion Criteria** - Requirements to complete (e.g., "80% progress", "all modules")
- **Passing Grade** - Minimum grade to pass (if graded)
- **Assessment Methods** - Types of assessments (e.g., "Quiz", "Assignment", "Participation")
- **Certificate Available** - Whether a certificate is issued upon completion
- **Credits/Credit Hours** - Credits awarded (if applicable)

### Content & Structure
- **Estimated Hours** - Total estimated time to complete
- **Number of Modules** - Count of modules (could be calculated)
- **Number of Lessons** - Count of lessons (could be calculated)
- **Content Type** - "Video", "Reading", "Interactive", "Mixed"

### Visibility & Access
- **Visibility** - "Public", "Private", "Members Only"
- **Access Level** - Who can access (e.g., "All", "Members", "Leaders Only")
- **Requires Approval** - Whether enrollment requires approval
- **Age Restriction** - Minimum/maximum age requirements

### Financial
- **Cost/Fee** - Course fee (if any)
- **Payment Required** - Whether payment is required
- **Scholarship Available** - Whether scholarships are available

### Metadata
- **Thumbnail/Image** - Course image/thumbnail URL
- **Video Preview** - Preview video URL
- **Tags** - For categorization and search
- **Difficulty Rating** - 1-5 difficulty rating
- **Popularity Score** - Based on enrollments/ratings

### Church-Specific Attributes
- **Ministry Area** - Which ministry this serves (e.g., "Children's Ministry", "Youth", "Adult")
- **Age Group** - Target age group (e.g., "Children", "Youth", "Adult", "Senior")
- **Spiritual Maturity Level** - "New Believer", "Growing", "Mature", "Leader"
- **Bible Study Type** - "Book Study", "Topical", "Character Study", "Doctrinal"
- **Small Group Compatible** - Whether suitable for small groups
- **Requires Baptism** - Whether baptism is required
- **Denomination Specific** - Whether specific to a denomination

## Recommendations for Church Course Tracker

Based on your use case (church course tracking with Planning Center integration), here are the most valuable additions:

### High Priority
1. **Course Code** - Useful for church course numbering (e.g., "DISC-101")
2. **Category/Department** - Organize by ministry area (e.g., "Discipleship", "Bible Study", "Ministry Training")
3. **Level** - Beginner/Intermediate/Advanced helps students choose appropriately
4. **Instructor** - Track who teaches the course (User ID foreign key)
5. **Location** - Where the course meets (important for in-person courses)
6. **Mode of Delivery** - In-person/Online/Hybrid (important post-COVID)
7. **Ministry Area** - Church-specific categorization
8. **Age Group** - Target demographic

### Medium Priority
9. **Learning Objectives** - What students will learn (JSON array or text)
10. **Estimated Hours** - Total time commitment
11. **Tags** - For searchability
12. **Thumbnail/Image** - Visual representation
13. **Enrollment Type** - Open/Closed/Approval Required
14. **Certificate Available** - Whether completion certificate is issued

### Low Priority (Nice to Have)
15. **Cost/Fee** - If courses have fees
16. **Short Name** - Abbreviation for display
17. **Language** - If offering multilingual courses
18. **Difficulty Rating** - User-submitted rating

## Implementation Notes

- Many scheduling-related attributes (start date, end date, capacity) are already handled in your `CourseInstance` model, which is the correct approach
- Some attributes like "Number of Modules" can be calculated from relationships rather than stored
- Consider using JSON fields for flexible attributes like "Learning Objectives" or "Tags"
- Some attributes might be better as separate tables (e.g., Instructors as a many-to-many relationship)


