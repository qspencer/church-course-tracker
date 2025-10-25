# Church Course Tracker - Database ER Diagram

## 📊 **Database Schema Overview**

This document provides a comprehensive Entity-Relationship (ER) diagram for the Church Course Tracker database.

---

## 🏗️ **Core Entities**

### **1. USERS Table**
```
┌─────────────────────────────────────────────────────────┐
│                        USERS                             │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ username - String(50), Unique, Index                   │
│ email - String(255), Unique, Index, NOT NULL           │
│ full_name - String(200), NOT NULL                       │
│ hashed_password - String(255), NOT NULL                 │
│ role - String(20), Default: 'staff'                     │
│ is_active - Boolean, Default: True                      │
│ data_source - String(20), NULL                          │
│ csv_loaded_at - DateTime(timezone=True), NULL          │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
│ last_login - DateTime(timezone=True), NULL              │
└─────────────────────────────────────────────────────────┘
```

### **2. PEOPLE Table** (Church Members from Planning Center)
```
┌─────────────────────────────────────────────────────────┐
│                        PEOPLE                           │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ planning_center_id - String(50), Unique, Index          │
│ first_name - String(100), NOT NULL                      │
│ last_name - String(100), NOT NULL                       │
│ email - String(255), Index                              │
│ phone - String(20)                                      │
│ date_of_birth - Date                                    │
│ gender - String(10)                                     │
│ address1 - String(255)                                  │
│ address2 - String(255)                                  │
│ city - String(100)                                      │
│ state - String(50)                                      │
│ zip - String(20)                                        │
│ household_id - String(50)                               │
│ household_name - String(255)                            │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

### **3. COURSES Table**
```
┌─────────────────────────────────────────────────────────┐
│                       COURSES                           │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ title - String(200), NOT NULL, Index                    │
│ description - Text                                      │
│ duration_weeks - Integer                               │
│ prerequisites - JSON (List of course IDs)              │
│ planning_center_event_id - String(50), Unique, Index    │
│ planning_center_event_name - String(200)                │
│ event_start_date - DateTime(timezone=True)              │
│ event_end_date - DateTime(timezone=True)                │
│ max_capacity - Integer                                  │
│ current_registrations - Integer, Default: 0             │
│ is_active - Boolean, Default: True                       │
│ content_unlock_mode - String(20), Default: 'immediate'  │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

### **4. COURSE_ENROLLMENT Table** (Junction Table)
```
┌─────────────────────────────────────────────────────────┐
│                  COURSE_ENROLLMENT                      │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ people_id (FK) - Integer, NOT NULL, Index               │
│ course_id (FK) - Integer, NOT NULL, Index               │
│ planning_center_registration_id - String(50), Unique    │
│ enrollment_date - DateTime(timezone=True)               │
│ status - String(20), Default: 'enrolled'                │
│ progress_percentage - Float, Default: 0.0               │
│ completion_date - DateTime(timezone=True)               │
│ notes - Text                                            │
│ dependency_override - Boolean, Default: False           │
│ dependency_override_by - Integer                        │
│ planning_center_synced - Boolean, Default: False         │
│ registration_status - String(20)                        │
│ registration_notes - Text                               │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔗 **Relationships**

### **Core Relationships:**
```
PEOPLE ──┐
         ├──→ COURSE_ENROLLMENT ←── COURSES
         │         │
         │         └──→ PROGRESS (Content Completion)
         │
         └──→ PEOPLE_CAMPUS ←── CAMPUS
```

### **Detailed Entity Relationships:**

1. **PEOPLE → COURSE_ENROLLMENT** (One-to-Many)
   - One person can enroll in multiple courses
   - Foreign Key: `people_id`

2. **COURSES → COURSE_ENROLLMENT** (One-to-Many)
   - One course can have multiple enrollments
   - Foreign Key: `course_id`

3. **COURSE_ENROLLMENT → PROGRESS** (One-to-Many)
   - One enrollment can have multiple progress records
   - Tracks completion of individual content items

4. **PEOPLE → PEOPLE_CAMPUS** (One-to-Many)
   - One person can be associated with multiple campuses
   - Junction table for many-to-many relationship

5. **CAMPUS → PEOPLE_CAMPUS** (One-to-Many)
   - One campus can have multiple people
   - Junction table for many-to-many relationship

---

## 📋 **Supporting Tables**

### **CAMPUS Table**
```
┌─────────────────────────────────────────────────────────┐
│                       CAMPUS                           │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ name - String(100), NOT NULL                           │
│ address - String(255)                                  │
│ city - String(100)                                     │
│ state - String(50)                                     │
│ zip - String(20)                                       │
│ phone - String(20)                                     │
│ email - String(255)                                    │
│ is_active - Boolean, Default: True                      │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

### **PROGRESS Table** (Content Completion Tracking)
```
┌─────────────────────────────────────────────────────────┐
│                      PROGRESS                          │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ enrollment_id (FK) - Integer, NOT NULL                  │
│ content_id (FK) - Integer, NOT NULL                     │
│ completed_at - DateTime(timezone=True)                  │
│ completion_percentage - Float                          │
│ notes - Text                                            │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

### **CONTENT Table** (Course Content Items)
```
┌─────────────────────────────────────────────────────────┐
│                      CONTENT                           │
├─────────────────────────────────────────────────────────┤
│ id (PK) - Integer, Primary Key                          │
│ course_id (FK) - Integer, NOT NULL                      │
│ title - String(200), NOT NULL                           │
│ description - Text                                      │
│ content_type - String(50)                               │
│ order_index - Integer                                   │
│ is_required - Boolean, Default: True                     │
│ data_source - String(20)                               │
│ csv_loaded_at - DateTime(timezone=True)                │
│ created_at - DateTime(timezone=True)                    │
│ updated_at - DateTime(timezone=True)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 **Key Features**

### **Source Tracking System:**
- All tables include `data_source` and `csv_loaded_at` fields
- Allows tracking of data origin (CSV, API, manual entry)
- Enables selective data management and clearing

### **Planning Center Integration:**
- `planning_center_id` fields for syncing with external system
- `planning_center_synced` flags for tracking sync status
- Support for event and registration mapping

### **Audit Trail:**
- `created_at` and `updated_at` timestamps on all tables
- Comprehensive tracking of data changes

### **Flexible Content Management:**
- JSON fields for complex data (prerequisites)
- Support for different content types and unlock modes
- Progress tracking at granular level

---

## 🔄 **Data Flow**

```
Planning Center → PEOPLE (Members)
                ↓
Planning Center → COURSES (Events)
                ↓
Planning Center → COURSE_ENROLLMENT (Registrations)
                ↓
Application → PROGRESS (Content Completion)
```

---

## 📊 **Summary Statistics**

- **Core Tables:** 6 (Users, People, Courses, Enrollments, Campus, Content)
- **Junction Tables:** 2 (Course_Enrollment, People_Campus)
- **Tracking Tables:** 1 (Progress)
- **Total Relationships:** 8 major relationships
- **Source Tracking:** All tables support CSV data loading
- **Planning Center Integration:** Full bidirectional sync support

---

*This ER diagram represents the complete database schema for the Church Course Tracker application, supporting course management, member enrollment, progress tracking, and integration with Planning Center.*
