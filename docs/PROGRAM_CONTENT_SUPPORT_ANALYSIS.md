# Program Content Hierarchical Structure - Support Analysis

## Summary

The **database models and schemas support** the hierarchical structure you need (Program → Categories → Lessons), but the **API endpoints and UI are missing**.

## What IS Supported (Backend Models & Schemas)

### Database Models ✅
- `ProgramModule` - Categories for organizing content (4 categories)
  - Located in: `backend/app/models/program_content.py`
  - Fields: `program_id`, `title`, `description`, `order_index`, `is_active`
  
- `ProgramContent` - Individual lessons/content items (21 lessons)
  - Located in: `backend/app/models/program_content.py`
  - Fields: `program_id`, `module_id` (links to category), `title`, `description`, `order_index`, etc.

### Pydantic Schemas ✅
- Located in: `backend/app/schemas/program_content.py`
- Schemas available:
  - `ProgramModuleCreate`, `ProgramModuleUpdate`, `ProgramModule`
  - `ProgramContentCreate`, `ProgramContentUpdate`, `ProgramContent`

## What's MISSING

### Backend API Endpoints ❌
- **No API endpoints** for managing program modules or content
- No file: `backend/app/api/v1/endpoints/program_content.py`
- Not registered in the API router (`backend/app/api/v1/api.py`)
- **Note:** Courses have similar endpoints in `backend/app/api/v1/endpoints/course_content.py` that could serve as a template

### Backend Service ❌
- No service layer for program content management
- **Note:** Courses have `ContentService` in `backend/app/services/content_service.py` that could serve as a template

### Frontend UI ❌
- **No program-content component** for managing modules and content
- **Note:** Courses have a `course-content` component in `frontend/church-course-tracker/src/app/components/course-content/` that could serve as a template
- No frontend service for program content
- No frontend models/interfaces for program modules/content

## Current State

You can:
- ✅ Create and manage Programs (via Programs Management UI)
- ✅ Manage participants, pairings, sessions, and progress for programs
- ❌ **Cannot** create or manage categories (ProgramModule) via UI
- ❌ **Cannot** create or manage lessons (ProgramContent) via UI

## Recommendation

To support your use case (1 program with 4 categories and 21 lessons), you would need to:

1. **Create backend API endpoints** for program modules and content (similar to `course_content.py`)
2. **Create a backend service** for program content management (similar to `ContentService`)
3. **Create frontend UI components** for managing program content (similar to `course-content` component)
4. **Create frontend service** for program content API calls

This would be a significant feature addition, but could follow the same patterns as the existing course content management feature.

## Reference: Course Content Feature

The course content feature provides a good template:
- Backend: `backend/app/api/v1/endpoints/course_content.py`
- Backend Service: `backend/app/services/content_service.py`
- Frontend Component: `frontend/church-course-tracker/src/app/components/course-content/`
- Frontend Service: `frontend/church-course-tracker/src/app/services/course-content.service.ts`

The course-content component allows users to:
- View modules (categories) in a "Modules" tab
- Create/edit/delete modules
- View content items in a "Content" tab
- Create/edit/delete content items
- Assign content items to modules
- Order modules and content using `order_index`

## Next Steps

Would you like me to:
1. Implement the missing backend API endpoints and services?
2. Implement the missing frontend UI components?
3. Or would you prefer to document this as a future enhancement and proceed with manual data entry via the database for now?


