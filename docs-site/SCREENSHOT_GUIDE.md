# Screenshot Guide for Documentation

## Why Screenshots Matter

Screenshots are incredibly valuable for non-technical users because they:
- Show exactly what users will see on their screen
- Reduce confusion about where to find features
- Provide visual confirmation of actions
- Make the documentation more engaging and easier to follow

## Recommended Screenshot Locations

### Getting Started Guide

1. **Login Page** (Line 12)
   - Screenshot of the login page
   - Shows username/password fields clearly
   - Helps users identify the correct page

2. **Dashboard Overview** (Line 33)
   - Screenshot of the main dashboard
   - Highlight key areas (Quick Overview, Recent Activity, Navigation)
   - Shows what users see after logging in

3. **Navigation Menu** (Line 41)
   - Screenshot of the main navigation
   - Shows menu structure clearly
   - Helps users understand the layout

4. **Course Browsing** (Line 64)
   - Screenshot of the courses list page
   - Shows how courses are displayed

5. **Enrollment Process** (Line 70)
   - Screenshot showing the "Enroll" button
   - Screenshot of enrollment confirmation

### User Guide

1. **Dashboard** (Line 32)
   - Full dashboard screenshot with annotations
   - Highlight different sections

2. **Creating a Course** (Line 60)
   - Screenshot of "Create New Course" button
   - Screenshot of the course creation form
   - Shows all form fields

3. **Course Details Page** (Line 87)
   - Screenshot of a course detail view
   - Shows enrolled members, content, statistics

4. **Enrollment Form** (Line 108)
   - Screenshot of the enrollment form
   - Shows member selection, course selection, status

5. **Progress Tracking** (Line 143)
   - Screenshot of "My Progress" page
   - Shows completion percentages, modules

6. **Content Upload** (Line 88 in Getting Started)
   - Screenshot of content upload interface
   - Shows file upload area

7. **Reports** (User Guide)
   - Screenshot of a sample report
   - Shows what data is displayed

8. **User Management** (Line 100 in Getting Started)
   - Screenshot of user list
   - Screenshot of user creation form

## How to Add Screhots to MkDocs

### Step 1: Create Screenshots Directory

```bash
mkdir -p docs-site/docs/images/screenshots
```

### Step 2: Take Screenshots

Best practices:
- Use consistent browser window size (e.g., 1920x1080)
- Hide personal/sensitive information
- Use clear, descriptive filenames
- Consider using annotations/arrows to highlight important areas
- Take screenshots in both light and dark mode if your app supports it

### Step 3: Add Images to Markdown

MkDocs supports standard Markdown image syntax:

```markdown
![Alt text](images/screenshots/login-page.png)
```

Or with sizing:

```markdown
![Login Page](images/screenshots/login-page.png){ width="800" }
```

### Step 4: Organize Screenshots

Suggested structure:
```
docs-site/docs/images/
  screenshots/
    getting-started/
      login-page.png
      dashboard.png
      navigation-menu.png
    user-guide/
      create-course.png
      enrollment-form.png
      progress-tracking.png
```

## Screenshot Specifications

### Recommended Settings:
- **Format**: PNG (for screenshots with UI elements)
- **Resolution**: 1920x1080 or higher (scaled down if needed)
- **File Size**: Optimize to < 500KB per image
- **Naming**: Use descriptive names like `dashboard-overview.png`, `create-course-form.png`

### Tools for Screenshots:
- **Browser DevTools**: Built-in screenshot tools
- **Snipping Tool / Screenshot apps**: For annotations
- **Image optimization**: Use tools like `pngquant` or `optipng` to reduce file size

## Example Integration

Here's how a section with screenshots would look:

```markdown
## 🔐 Logging In

### First Time Login

If this is your first time using the system, you'll need login credentials from your administrator.

![Login Page](images/screenshots/getting-started/login-page.png)

### Logging In

1. Enter your username in the "Username" field
2. Enter your password in the "Password" field
3. Click the "Login" button

![Login Form](images/screenshots/getting-started/login-form.png){ width="600" }
```

## Priority Screenshots (Start Here)

If you can only add a few screenshots initially, prioritize:

1. **Login Page** - First thing users see
2. **Dashboard** - Main interface after login
3. **Navigation Menu** - Helps users understand structure
4. **Create Course Form** - Common task for staff
5. **Enrollment Process** - Key workflow
6. **Progress Tracking** - Important for members

## Maintenance

- Update screenshots when UI changes
- Keep screenshots consistent with current application version
- Remove outdated screenshots
- Consider versioning screenshots if UI changes frequently

