# Implementation Plan: Stubbed Features

## Overview
This document outlines the plan to implement the currently stubbed/not implemented features in the Church Course Tracker application.

## Current Status

### ✅ Backend Ready (Frontend Stubbed)
- Module CRUD operations: Backend endpoints exist and are functional
  - `POST /api/v1/content/modules` - Create module ✅
  - `GET /api/v1/content/modules/{course_id}` - List modules ✅
  - `GET /api/v1/content/modules/single/{module_id}` - Get module ✅
  - `PUT /api/v1/content/modules/{module_id}` - Update module ✅
  - `DELETE /api/v1/content/modules/{module_id}` - Delete module ✅

### ❌ Frontend Stubbed
- Module creation UI
- Module editing UI
- Module deletion UI
- Embedded content viewer

---

## Implementation Plan

### Phase 1: Module Management UI (High Priority)

#### 1.1 Create Module Dialog Component
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** None

**Tasks:**
- [ ] Create `module-dialog.component.ts`
- [ ] Create `module-dialog.component.html` with form:
  - Title (required)
  - Description (optional, textarea)
  - Order/Sequence number (optional)
- [ ] Create `module-dialog.component.scss` for styling
- [ ] Add form validation
- [ ] Support both create and edit modes
- [ ] Integrate with `CourseContentService` to call backend API
- [ ] Handle success/error responses
- [ ] Add to `course-content.module.ts`

**Acceptance Criteria:**
- Users can create new modules for a course
- Form validation prevents invalid submissions
- Success message displayed on creation
- Module list refreshes after creation
- Error handling for API failures

#### 1.2 Module Service Methods
**Priority:** ✅ Already Implemented  
**Status:** Service methods already exist in `CourseContentService`
- ✅ `createModule()` - Line 30
- ✅ `getCourseModules()` - Line 34
- ✅ `getModule()` - Line 38
- ✅ `updateModule()` - Line 42
- ✅ `deleteModule()` - Line 46

**Note:** No work needed - service layer is complete!

#### 1.3 Update Course Content Component
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** 1.1, 1.2

**Tasks:**
- [ ] Implement `createModule()` method:
  - Open module dialog in create mode
  - Handle dialog result
  - Refresh module list on success
- [ ] Implement `editModule()` method:
  - Open module dialog in edit mode with module data
  - Handle dialog result
  - Refresh module list on success
- [ ] Implement `deleteModule()` method:
  - Show confirmation dialog
  - Call delete API on confirmation
  - Refresh module list on success
  - Handle errors gracefully

**Files to Modify:**
- `frontend/church-course-tracker/src/app/components/course-content/course-content.component.ts`
- `frontend/church-course-tracker/src/app/components/course-content/course-content.component.html` (if needed)

**Acceptance Criteria:**
- All three methods work end-to-end
- User feedback for all operations (success/error messages)
- Module list updates automatically after changes
- Proper error handling

#### 1.4 Module Dialog UI/UX
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Dependencies:** 1.1

**Tasks:**
- [ ] Design module dialog form layout
- [ ] Add Material Design form fields
- [ ] Implement form validation messages
- [ ] Add loading states during API calls
- [ ] Style dialog consistently with other dialogs

**Acceptance Criteria:**
- Dialog matches design system
- Form is intuitive and user-friendly
- Validation messages are clear
- Loading indicators shown during API calls

---

### Phase 2: Embedded Content Viewer (Medium Priority)

#### 2.1 Embedded Content Viewer Component
**Priority:** Medium  
**Estimated Time:** 3-4 hours  
**Dependencies:** None

**Tasks:**
- [ ] Create `embedded-content-viewer.component.ts`
- [ ] Create `embedded-content-viewer.component.html`
  - Use `[innerHTML]` to render embedded content
  - Add safety sanitization
  - Handle iframe embeds
  - Support video embeds (YouTube, Vimeo, etc.)
- [ ] Create `embedded-content-viewer.component.scss`
- [ ] Add sanitization service (use Angular DomSanitizer)
- [ ] Handle different embed types (HTML, iframe, video)
- [ ] Add fullscreen option if needed
- [ ] Create dialog wrapper for viewing

**Files to Create:**
- `frontend/church-course-tracker/src/app/components/course-content/embedded-content-viewer/embedded-content-viewer.component.ts`
- `frontend/church-course-tracker/src/app/components/course-content/embedded-content-viewer/embedded-content-viewer.component.html`
- `frontend/church-course-tracker/src/app/components/course-content/embedded-content-viewer/embedded-content-viewer.component.scss`

**Acceptance Criteria:**
- Embedded HTML content renders safely
- Iframe embeds work correctly
- Video embeds (YouTube, Vimeo) work
- Content is sanitized to prevent XSS attacks
- Viewer can be opened in a dialog
- Proper error handling for invalid content

#### 2.2 Security Considerations
**Priority:** High  
**Estimated Time:** 1-2 hours  
**Dependencies:** 2.1

**Tasks:**
- [ ] Implement proper HTML sanitization
- [ ] Whitelist allowed iframe sources if needed
- [ ] Test for XSS vulnerabilities
- [ ] Add CSP (Content Security Policy) considerations
- [ ] Document security measures

**Acceptance Criteria:**
- No XSS vulnerabilities introduced
- Sanitization properly configured
- Security tested and documented

#### 2.3 Update Course Content Component for Embedded Content
**Priority:** Medium  
**Estimated Time:** 1 hour  
**Dependencies:** 2.1

**Tasks:**
- [ ] Update `viewContent()` method in `course-content.component.ts`
- [ ] Open embedded content viewer dialog for embedded content type
- [ ] Remove "not implemented yet" message
- [ ] Handle errors gracefully

**Files to Modify:**
- `frontend/church-course-tracker/src/app/components/course-content/course-content.component.ts`

**Acceptance Criteria:**
- Embedded content opens in viewer dialog
- User can view embedded content without errors
- Error messages are clear if content cannot be displayed

---

### Phase 3: Testing and Quality Assurance

#### 3.1 Unit Tests
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Dependencies:** Phase 1, Phase 2

**Tasks:**
- [ ] Write unit tests for module dialog component
- [ ] Write unit tests for embedded content viewer component
- [ ] Update tests for course-content component (remove placeholder tests)
- [ ] Test form validation
- [ ] Test API integration
- [ ] Test error handling

**Acceptance Criteria:**
- All new components have >80% test coverage
- All tests pass
- Edge cases covered

#### 3.2 Integration Tests
**Priority:** Medium  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1, Phase 2

**Tasks:**
- [ ] Test module CRUD operations end-to-end
- [ ] Test embedded content viewing
- [ ] Test error scenarios
- [ ] Test with different user roles (admin, staff, viewer)

**Acceptance Criteria:**
- All features work end-to-end
- Error scenarios handled correctly
- Role-based access working

#### 3.3 E2E Tests
**Priority:** Medium  
**Estimated Time:** 2-3 hours  
**Dependencies:** Phase 1, Phase 2

**Tasks:**
- [ ] Add E2E tests for module creation
- [ ] Add E2E tests for module editing
- [ ] Add E2E tests for module deletion
- [ ] Add E2E tests for embedded content viewing
- [ ] Verify tests pass in CI/CD

**Acceptance Criteria:**
- E2E tests cover new features
- Tests are reliable and not flaky
- Tests pass in CI/CD pipeline

---

## Implementation Order

### Sprint 1: Module Management (Backend Integration)
1. ✅ Module Service Methods (1.2) - **Already Complete** (0 hours)
2. Create Module Dialog Component (1.1) - **3 hours**
3. Update Course Content Component - Create Module (1.3) - **1 hour**
4. Update Course Content Component - Edit Module (1.3) - **1 hour**
5. Update Course Content Component - Delete Module (1.3) - **1 hour**
6. Module Dialog UI/UX (1.4) - **2 hours**
7. Unit Tests for Module Management (3.1) - **2 hours**
8. Integration Tests (3.2) - **1 hour**

**Sprint 1 Total:** ~11 hours (reduced from 13 hours since service methods exist)

### Sprint 2: Embedded Content Viewer
1. Embedded Content Viewer Component (2.1) - **4 hours**
2. Security Considerations (2.2) - **2 hours**
3. Update Course Content Component for Embedded Content (2.3) - **1 hour**
4. Unit Tests for Embedded Viewer (3.1) - **2 hours**
5. Integration Tests (3.2) - **1 hour**

**Sprint 2 Total:** ~10 hours

### Sprint 3: Testing and Polish
1. E2E Tests (3.3) - **3 hours**
2. Bug fixes and refinements - **2 hours**
3. Documentation updates - **1 hour**

**Sprint 3 Total:** ~6 hours

**Total Estimated Time:** ~27 hours (approximately 3.5 days of focused work)

**Note:** Service layer for modules is already complete, saving ~2 hours

---

## Technical Considerations

### Module Dialog Component Structure
```typescript
export interface ModuleDialogData {
  module?: CourseModule;  // If editing, pass existing module
  courseId: number;       // Required for creating
  mode: 'create' | 'edit';
}

@Component({
  selector: 'app-module-dialog',
  templateUrl: './module-dialog.component.html',
  styleUrls: ['./module-dialog.component.scss']
})
export class ModuleDialogComponent {
  moduleForm: FormGroup;
  isSubmitting = false;
  
  // Form fields: title, description, order_index (optional)
}
```

### Embedded Content Viewer Structure
```typescript
@Component({
  selector: 'app-embedded-content-viewer',
  templateUrl: './embedded-content-viewer.component.html',
  styleUrls: ['./embedded-content-viewer.component.scss']
})
export class EmbeddedContentViewerComponent {
  content: string;  // HTML/embed code
  
  constructor(private sanitizer: DomSanitizer) {}
  
  getSafeHtml(content: string): SafeHtml {
    return this.sanitizer.sanitize(SecurityContext.HTML, content);
  }
}
```

### API Integration Points

**Module Service Methods (Already Implemented):**
```typescript
// In course-content.service.ts - Already exists!
createModule(moduleData: CourseModuleCreate): Observable<CourseModule>
getCourseModules(courseId: number): Observable<CourseModule[]>
getModule(moduleId: number): Observable<CourseModule>
updateModule(moduleId: number, moduleData: CourseModuleUpdate): Observable<CourseModule>
deleteModule(moduleId: number): Observable<void>
```

**Implementation Note:** These methods are already in place and working. We just need to:
1. Create the UI components to use them
2. Wire them up in the course-content component

---

## Risk Assessment

### Low Risk
- Module management (backend already exists)
- Module service methods (straightforward API calls)

### Medium Risk
- Embedded content viewer (security concerns, content sanitization)
- Cross-browser compatibility for embedded content

### Mitigation Strategies
1. **Security:** Use Angular's DomSanitizer, whitelist allowed sources
2. **Testing:** Comprehensive unit and integration tests
3. **User Feedback:** Clear error messages for unsupported content types
4. **Progressive Enhancement:** Graceful degradation for unsupported embed types

---

## Success Metrics

1. ✅ All "not implemented yet" messages removed
2. ✅ Module CRUD operations work end-to-end
3. ✅ Embedded content displays correctly
4. ✅ >80% test coverage for new features
5. ✅ No security vulnerabilities
6. ✅ User-friendly error messages and validation

---

## Next Steps

1. **Review and Approve Plan**
2. **Create Implementation Branch:** `feature/module-management-and-embedded-viewer`
3. **Begin Sprint 1:** Implement module management
4. **Code Review:** After each major feature
5. **Testing:** Unit → Integration → E2E
6. **Merge to Main:** After all tests pass

---

## Notes

- **Module Service Methods Already Exist:** The `CourseContentService` already has all module CRUD methods implemented (createModule, updateModule, deleteModule, getCourseModules). No additional service work needed.
- **Modules Already Loading:** The `CourseContentComponent.loadData()` method already loads modules (line 92-102). We just need to wire up the UI actions.
- **Existing Patterns:** Follow the pattern used in `ContentDialogComponent` for the module dialog.
- **Security:** Embedded content viewer requires careful security considerations with DomSanitizer.
- **User Experience:** Follow existing Material Design patterns used in other dialogs.
- **Accessibility:** Ensure all new components are accessible.

## Quick Start Implementation Order

### Step 1: Module Dialog Component (2-3 hours)
1. Copy structure from `ContentDialogComponent` as reference
2. Create `module-dialog/` folder in `course-content/` directory
3. Create TypeScript component with form handling
4. Create HTML template with Material form fields
5. Create SCSS styling
6. Add to module declarations

### Step 2: Wire Up Module Actions (2-3 hours)
1. Update `createModule()` to open dialog and refresh
2. Update `editModule()` to open dialog with module data and refresh
3. Update `deleteModule()` to show confirmation and refresh
4. Test each action end-to-end

### Step 3: Embedded Content Viewer (4-5 hours)
1. Create embedded content viewer component
2. Add DomSanitizer for security
3. Update `viewContent()` method
4. Test with various embed types

### Step 4: Testing (3-4 hours)
1. Unit tests for all new components
2. Integration tests
3. E2E tests
4. Security testing for embedded content

**Total: ~11-15 hours of implementation work**

