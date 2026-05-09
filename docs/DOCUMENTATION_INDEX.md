# Church Course Tracker - Documentation Index

**Last Updated:** May 9, 2026
**Documents:** 18 active, 125+ archived

This directory contains the active documentation for the Church Course Tracker project. Historical and completed documentation has been moved to the `archive/` subdirectory.

---

## 📖 **User Documentation**

These documents are for end users of the application.

### **[USER_GUIDE.md](USER_GUIDE.md)**
Comprehensive guide for using the Church Course Tracker. Covers all features with step-by-step instructions for:
- Dashboard and navigation
- Course management
- **Program management** (participants, pairings, sessions, progress)
- Enrollments and progress tracking
- Content management
- Members and reporting
- User management and profiles
- Activity and audit logs

**Audience:** Administrators, Staff, and Members
**Status:** ✅ Current and maintained (Updated: January 13, 2026)

### **[FEATURES.md](FEATURES.md)**
Overview of all features available in the system. Explains what each feature does and who can use it:
- Core features (courses, **programs**, enrollments, progress, content, members)
- Program management (participants, pairings, sessions)
- Reporting and analytics
- User management and role-based access
- Planning Center integration
- Security and audit logging

**Audience:** All users, especially new users and decision makers
**Status:** ✅ Current and maintained (Updated: January 13, 2026)

### **[GETTING_STARTED.md](GETTING_STARTED.md)**
Quick start guide for first-time users. Covers:
- Accessing the application
- Logging in
- Dashboard overview
- Basic navigation (including Programs)
- First steps for each user role
- Common questions and troubleshooting

**Audience:** New users
**Status:** ✅ Current and maintained (Updated: January 13, 2026)

---

## 🛠️ **Technical Documentation**

These documents are for developers and administrators working with the system.

### **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**
Explains the project organization:
- Directory structure
- File organization
- Scripts location
- Documentation organization
- Naming conventions

**Audience:** Developers
**Status:** ✅ Current and maintained

### **[PLANNING_CENTER_INTEGRATION_SETUP.md](PLANNING_CENTER_INTEGRATION_SETUP.md)**
Setup guide for Planning Center integration:
- Configuration steps
- API credentials
- Sync settings
- Troubleshooting

**Audience:** Administrators, Developers
**Status:** ✅ Current and maintained

### **[PLANNING_CENTER_QUICK_START.md](PLANNING_CENTER_QUICK_START.md)**
Quick reference for Planning Center features:
- Basic operations
- Common tasks
- Quick troubleshooting

**Audience:** Administrators, Staff
**Status:** ✅ Current and maintained

### **[ERROR_HANDLING.md](ERROR_HANDLING.md)**
Comprehensive guide to error handling patterns:
- Custom exception classes
- Backend error handling
- Frontend error tracking
- Transaction management
- Testing approaches
- Best practices

**Generated:** January 14, 2026
**Audience:** Developers, Tech Leads
**Status:** ✅ Active technical reference

### **[LOGGING.md](LOGGING.md)**
Complete logging infrastructure guide:
- LoggerService implementation
- Sentry integration setup
- Context and structured logging
- Production debugging
- Best practices

**Generated:** January 14, 2026
**Audience:** Developers, Tech Leads
**Status:** ✅ Active technical reference

---

## 📋 **Planning & Analysis Documentation**

These documents contain planning, analysis, and recommendations for current or future work.

### **[CODE_REVIEW_AND_IMPROVEMENTS.md](CODE_REVIEW_AND_IMPROVEMENTS.md)**
Comprehensive code review with actionable recommendations:
- Security improvements needed
- Code quality issues
- Performance optimization opportunities
- Architecture recommendations
- Best practices
- Implementation priorities

**Generated:** January 12, 2026
**Audience:** Developers, Tech Leads
**Status:** ✅ Active reference document

### **[IMPROVEMENT_RECOMMENDATIONS.md](IMPROVEMENT_RECOMMENDATIONS.md)** ⭐ **NEW**
Comprehensive improvement recommendations based on code analysis:
- **Error Handling**: 7 critical bare exception clauses, 90+ broad handlers
- **Transaction Management**: 5+ consistency issues identified
- **Security**: SQL injection patterns, information disclosure
- **Incomplete Features**: 4 TODOs requiring completion
- **Frontend Issues**: 50+ console.log statements, missing error messages
- **Implementation Plan**: 4-week prioritized roadmap

**Generated:** January 13, 2026
**Audience:** Developers, Tech Leads, Project Managers
**Status:** ✅ Active reference document - **ACTION REQUIRED**


### **[PROJECT_PLAN_HTML_DOCUMENTATION.md](PROJECT_PLAN_HTML_DOCUMENTATION.md)**
Project plan for HTML documentation site:
- Documentation website structure
- Content organization
- Deployment plan

**Audience:** Tech Writers, Developers
**Status:** ⚠️ Planning document

---

## 🧪 **Testing & Quality Documentation**

These documents relate to testing strategy, test analysis, and quality improvements.

### **[TEST_REVIEW_AND_IMPROVEMENTS.md](TEST_REVIEW_AND_IMPROVEMENTS.md)**
Comprehensive test review with improvements:
- Test coverage analysis
- Positive and negative scenario coverage
- Edge case testing
- Tests added (65+ new tests)
- Coverage areas (security, concurrency, validation)

**Generated:** January 11, 2026
**Audience:** Developers, QA Engineers
**Status:** ✅ Active reference document

### **[EVALUATION_2026-05-09.md](EVALUATION_2026-05-09.md)**
Independent application evaluation covering backend, frontend, tests, infrastructure, and documentation:
- Critical security findings and prioritized fix list
- Code quality issues with file:line citations
- Infrastructure concerns
- Test suite status (unit + e2e)
- Documentation hygiene assessment
- Strengths worth preserving
- Recommended next steps

**Generated:** May 9, 2026
**Audience:** Tech Leads, Maintainers
**Status:** ✅ Active reference document

---

## 📂 Archived Reports

The following point-in-time reports have been moved to `archive/` (May 9, 2026 cleanup):
- Skipped-tests analyses → `archive/SKIPPED_TESTS_ANALYSIS.md`, `archive/E2E_SKIPPED_TESTS_COMPLETE_ANALYSIS.md`
- Documentation reviews → `archive/DOCUMENTATION_ACCURACY_REPORT.md`, `archive/DOCUMENTATION_REVIEW_REPORT_JAN_2026.md`
- Phase / completion reports (Jan 17, 2026) → `archive/CODE_QUALITY_IMPROVEMENTS_JAN_17_2026.md`, `archive/PHASE_3_PROGRESS_JAN_17_2026.md`, `archive/SENTRY_ERROR_FIX_JAN_17_2026.md`, `archive/CUSTOM_TAB_IMPORT_COMPLETION.md`
- Test-result snapshots → `archive/TEST_RESULTS_SUMMARY_2026-01-17.md`, `archive/BACKEND_TEST_RESULTS_SUMMARY.md`, `archive/FRONTEND_TEST_RESULTS_SUMMARY.md`, `archive/FRONTEND_TEST_INVESTIGATION.md`
- E2E iteration logs → 12 `archive/E2E_*.md` files

For current test/quality status, see `EVALUATION_2026-05-09.md`.

---

## 📂 **Archive**

Historical documentation has been moved to **[docs/archive/](archive/)** for reference. This includes:

- Completed status reports and summaries (43+ documents)
- Completed fix and test summaries (23+ documents)
- Completed implementation summaries (10+ documents)
- Completed upgrade and testing docs (8+ documents)
- Specific issue investigations (10+ documents)
- Design proposals and research (12+ documents)
- Operational guides (5+ documents)

**Total archived documents:** 103+

**Recently Archived (January 16, 2026):**
- DOCUMENTATION_UPDATE_SUMMARY_JAN_13_2026.md
- FINALIZE_FIXES_COMPLETION_REPORT.md
- FINALIZE_OPERATOR_FIXES_SUMMARY.md
- TESTING_SUMMARY.md
- COMPLETE_TESTING_REPORT.md
- TESTING_FINAL_SUMMARY.md
- FINAL_TESTING_STATUS.md
- WHY_TESTS_ARE_SKIPPED.md

View the archive directory for historical context on past work, but note that information may be outdated.

---

## 🗂️ **Documentation Organization**

### Active Documents (16)
These are current, maintained documents that are regularly referenced.

### Archived Documents (103+)
Historical documents that are kept for reference but are no longer actively used.

### When to Archive a Document
A document should be archived when:
- The work it describes is complete
- It's a status report that's no longer current
- It's been superseded by a newer document
- It's a specific issue investigation that's resolved
- It's a plan that's been fully implemented

### When to Keep a Document Active
A document should remain active when:
- It's user-facing documentation
- It's an implementation plan for ongoing work
- It contains actionable recommendations
- It's a reference guide for active features
- It's regularly updated or referenced

---

## 📝 **Document Maintenance**

### Keeping Documentation Current
- Review active documents quarterly
- Update user guides when features change
- Archive completed plans and status reports
- Consolidate redundant documents
- Keep the DOCUMENTATION_INDEX.md updated

### Document Naming Conventions
- **USER_GUIDE.md** - User-facing guides
- **FEATURES.md** - Feature descriptions
- **_PLAN.md** - Implementation plans
- **_ANALYSIS.md** - Analysis documents
- **_REVIEW.md** - Review documents
- **_STATUS.md** - Status reports (**archive when complete**)
- **_SUMMARY.md** - Summaries (**archive when work complete**)
- **_REPORT.md** - Reports and assessments

---

## 🔍 **Finding Documentation**

### By Role
- **New Users:** Start with GETTING_STARTED.md → USER_GUIDE.md
- **End Users:** USER_GUIDE.md, FEATURES.md
- **Administrators:** USER_GUIDE.md, PLANNING_CENTER_*.md
- **Developers:** PROJECT_STRUCTURE.md, CODE_REVIEW_AND_IMPROVEMENTS.md, TEST_REVIEW_AND_IMPROVEMENTS.md
- **QA Engineers:** TEST_REVIEW_AND_IMPROVEMENTS.md, EVALUATION_2026-05-09.md (test status section)

### By Topic
- **Getting Started:** GETTING_STARTED.md
- **Features:** FEATURES.md, USER_GUIDE.md
- **Planning Center:** PLANNING_CENTER_INTEGRATION_SETUP.md, PLANNING_CENTER_QUICK_START.md
- **Code Quality:** CODE_REVIEW_AND_IMPROVEMENTS.md, IMPROVEMENT_RECOMMENDATIONS.md
- **Error Handling:** ERROR_HANDLING.md
- **Logging:** LOGGING.md
- **Testing:** TEST_REVIEW_AND_IMPROVEMENTS.md, EVALUATION_2026-05-09.md
- **Documentation:** EVALUATION_2026-05-09.md (Documentation section)
- **Project Structure:** PROJECT_STRUCTURE.md

---

## 📧 **Contributing to Documentation**

When adding new documentation:
1. Follow the naming conventions above
2. Add an entry to this index
3. Place in the appropriate category
4. Include audience, status, and last updated date
5. Archive old versions if superseded

When updating existing documentation:
1. Update the "Last Updated" date in the document
2. Update the status if it changes
3. Notify relevant stakeholders of significant changes

---

## 📊 **Documentation Statistics**

- **Total Active Documents:** 18
- **Total Archived Documents:** 125+
- **User Documentation:** 3 documents (all ✅ accurate and updated)
- **Technical Documentation:** 5 documents (structure, Planning Center x2, error handling, logging)
- **Planning & Analysis:** 3 documents (code review, improvements, HTML plan)
- **Testing & Quality:** 2 documents (test review, skipped tests analysis)
- **Documentation Maintenance:** 2 documents (accuracy report, review report)
- **Archive:** 103+ documents

**Recent Updates (January 16, 2026):**
- ✅ Archived 8 historical completion reports and summaries
- ✅ Reduced active documents from 24 to 16 (33% reduction)
- ✅ Added ERROR_HANDLING.md and LOGGING.md to index
- ✅ Added DOCUMENTATION_REVIEW_REPORT_JAN_2026.md
- ✅ Updated documentation statistics and counts
- ✅ Improved organization and clarity

**Previous Updates (January 13, 2026):**
- ✅ Fixed admin credentials in all documentation
- ✅ Added comprehensive Programs feature documentation
- ✅ Archived 2 obsolete System Settings documents
- ✅ Updated USER_GUIDE.md with Programs section
- ✅ Updated FEATURES.md with Programs feature
- ✅ Updated GETTING_STARTED.md navigation

---

**Last Major Cleanup:** January 16, 2026
**Next Review:** April 2026 (quarterly review)
