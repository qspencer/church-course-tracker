# Screenshots Directory

This directory contains screenshots for the documentation.

## Directory Structure

```
screenshots/
├── getting-started/
│   ├── login-page.png
│   ├── login-form.png
│   ├── dashboard.png
│   └── navigation-menu.png
└── user-guide/
    ├── create-course-form.png
    ├── enrollment-form.png
    ├── progress-tracking.png
    └── reports-example.png
```

## Screenshot Guidelines

1. **Resolution**: Use 1920x1080 or higher, but optimize file size
2. **Format**: PNG for UI screenshots
3. **File Size**: Keep under 500KB per image
4. **Naming**: Use descriptive, lowercase names with hyphens
5. **Content**: Hide sensitive information, use test data
6. **Annotations**: Consider adding arrows or highlights for clarity

## Taking Screenshots

1. Use browser DevTools or screenshot tools
2. Ensure consistent browser window size
3. Use the same browser/theme for consistency
4. Consider both light and dark mode if applicable
5. Optimize images before committing

## Adding Screenshots to Documentation

Use standard Markdown image syntax:

```markdown
![Alt text](images/screenshots/section/filename.png)
```

With sizing:

```markdown
![Alt text](images/screenshots/section/filename.png){ width="800" }
```

