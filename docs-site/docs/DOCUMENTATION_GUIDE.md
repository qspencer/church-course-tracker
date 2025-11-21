# Documentation Website Guide

This guide explains how to work with, maintain, and update the Church Course Tracker documentation website.

!!! info "For Contributors"
    This guide is for developers and content creators who want to update or maintain the documentation site.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Local Development](#local-development)
5. [Adding Content](#adding-content)
6. [Adding Screenshots](#adding-screenshots)
7. [Building the Site](#building-the-site)
8. [Deployment](#deployment)
9. [Customization](#customization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The documentation website is built using **MkDocs** with the **Material for MkDocs** theme. It's a static site generator that converts Markdown files into a beautiful, searchable documentation website.

### Key Features

- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔍 **Full-Text Search** - Built-in search functionality
- 🌓 **Dark Mode** - Automatic dark/light theme support
- 📑 **Table of Contents** - Auto-generated navigation
- 🎨 **Custom Styling** - Branded with Church Course Tracker colors
- ⚡ **Fast Loading** - Static HTML files served via CDN

### URL Structure

The documentation is hosted at:
- **Production**: `https://docs.quentinspencer.com/churchcoursetracker/`
- **Local Development**: `http://localhost:8000`

---

## Technology Stack

### Core Technologies

- **MkDocs** (v1.5.0+) - Static site generator
- **Material for MkDocs** (v9.4.0+) - Modern theme
- **Python 3.11+** - Runtime environment
- **Markdown** - Content format

### Plugins

- **Search** - Full-text search functionality
- **Minify** - HTML, CSS, and JavaScript minification

### Markdown Extensions

- `pymdownx.highlight` - Code syntax highlighting
- `pymdownx.superfences` - Enhanced code blocks
- `pymdownx.tabbed` - Tabbed content sections
- `admonition` - Callout boxes (info, warning, tip, etc.)
- `pymdownx.details` - Collapsible sections
- `tables` - Enhanced table support
- `toc` - Table of contents generation

---

## Project Structure

```
docs-site/
├── docs/                          # Documentation source files
│   ├── index.md                   # Home page
│   ├── getting-started.md         # Getting started guide
│   ├── user-guide.md              # Comprehensive user guide
│   ├── features.md                # Features overview
│   ├── images/                    # Images and screenshots
│   │   └── screenshots/
│   │       ├── getting-started/   # Getting started screenshots
│   │       └── user-guide/        # User guide screenshots
│   └── robots.txt                 # Search engine configuration
├── docs_overrides/                # Custom theme overrides
│   ├── partials/
│   │   └── footer.html            # Custom footer
│   ├── main.html                  # Main template with SEO
│   └── 404.html                   # Custom 404 page
├── theme/                         # Custom CSS
│   └── custom.css                 # Custom styling
├── scripts/                       # Utility scripts
│   ├── build.sh                   # Build script
│   ├── deploy.sh                  # Deployment script
│   └── capture-screenshots.ts     # Screenshot capture script
├── mkdocs.yml                     # MkDocs configuration
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── site/                          # Generated site (not in git)
```

---

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Navigate to the docs-site directory:**
   ```bash
   cd docs-site
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Development Server

1. **Start the server:**
   ```bash
   mkdocs serve
   ```

2. **Access the site:**
   - Open your browser to `http://localhost:8000`
   - The server auto-reloads when you make changes

3. **Stop the server:**
   - Press `Ctrl+C` in the terminal

### Alternative: Using the Start Script

```bash
./scripts/start-server.sh
```

Or if you prefer to specify the address:

```bash
mkdocs serve --dev-addr=0.0.0.0:8000
```

---

## Adding Content

### Creating a New Page

1. **Create a new Markdown file:**
   ```bash
   touch docs/your-new-page.md
   ```

2. **Add content using Markdown:**
   ```markdown
   # Your Page Title

   Your content here...
   ```

3. **Add it to navigation in `mkdocs.yml`:**
   ```yaml
   nav:
     - Home: index.md
     - Getting Started: getting-started.md
     - Your New Page: your-new-page.md
   ```

4. **Save and view:**
   - The server will auto-reload
   - Navigate to the new page in your browser

### Editing Existing Pages

1. **Open the Markdown file:**
   ```bash
   code docs/getting-started.md  # or use your preferred editor
   ```

2. **Make your changes:**
   - Use standard Markdown syntax
   - See [Markdown Extensions](#markdown-extensions) for advanced features

3. **Save and preview:**
   - The development server will auto-reload
   - Check your changes in the browser

### Markdown Extensions

#### Admonitions (Callout Boxes)

```markdown
!!! info "Information"
    This is an informational callout.

!!! tip "Tip"
    This is a helpful tip.

!!! warning "Warning"
    This is a warning message.

!!! danger "Danger"
    This is a danger/critical message.

!!! success "Success"
    This indicates a successful action.
```

#### Code Blocks

````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

#### Tabbed Content

````markdown
=== "Tab 1"
    Content for tab 1

=== "Tab 2"
    Content for tab 2
````

#### Collapsible Sections

````markdown
??? "Click to expand"
    Hidden content here
````

#### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

---

## Adding Screenshots

### Automatic Screenshot Capture

We have a script that automatically captures screenshots from the live application.

#### Prerequisites

- Node.js and npm installed
- Playwright installed (automatically installed by the script)
- Access to the application (for authenticated screenshots)

#### Running the Screenshot Script

1. **Capture public screenshots only:**
   ```bash
   cd docs-site
   node scripts/capture-screenshots.js
   ```

2. **Capture all screenshots (including authenticated pages):**
   ```bash
   cd docs-site
   DOCS_USERNAME="Admin" DOCS_PASSWORD="Admin123!" node scripts/capture-screenshots.js
   ```

#### Screenshot Locations

Screenshots are automatically saved to:
- `docs/images/screenshots/getting-started/` - Getting started screenshots
- `docs/images/screenshots/user-guide/` - User guide screenshots

#### Adding Screenshots to Pages

1. **Place the screenshot file** in the appropriate directory
2. **Reference it in Markdown:**
   ```markdown
   ![Screenshot Description](images/screenshots/getting-started/screenshot-name.png)
   *Optional caption text*
   ```

#### Manual Screenshot Guidelines

If you need to take screenshots manually:

1. **Resolution**: Use 1920x1080 or higher
2. **Format**: PNG for UI screenshots
3. **File Size**: Keep under 500KB per image (optimize if needed)
4. **Naming**: Use descriptive, lowercase names with hyphens
5. **Content**: Hide sensitive information, use test data
6. **Annotations**: Consider adding arrows or highlights for clarity

---

## Building the Site

### Manual Build

1. **Activate the virtual environment:**
   ```bash
   cd docs-site
   source venv/bin/activate
   ```

2. **Build the site:**
   ```bash
   mkdocs build
   ```

3. **Output location:**
   - Generated files are in `docs-site/site/`
   - This directory contains the static HTML files

### Using the Build Script

```bash
cd docs-site
./scripts/build.sh
```

### Build Output

The build process:
- Converts Markdown to HTML
- Applies the Material theme
- Minifies HTML, CSS, and JavaScript
- Generates search index
- Creates sitemap.xml
- Copies static assets

---

## Deployment

### Deployment Architecture

The documentation is deployed to:
- **S3 Bucket**: Static file storage
- **CloudFront**: CDN for fast global delivery
- **Route 53**: DNS management
- **ACM**: SSL certificate management

### Deployment Process

#### Using the Deployment Script

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Update deployment script variables:**
   Edit `scripts/deploy.sh`:
   ```bash
   S3_BUCKET="your-bucket-name"
   CLOUDFRONT_DIST_ID="your-distribution-id"
   DOCS_PATH="churchcoursetracker"
   ```

3. **Run the deployment script:**
   ```bash
   cd docs-site
   ./scripts/deploy.sh
   ```

#### Manual Deployment

1. **Build the site:**
   ```bash
   mkdocs build
   ```

2. **Sync to S3:**
   ```bash
   aws s3 sync site/ s3://your-bucket-name/churchcoursetracker/ --delete
   ```

3. **Invalidate CloudFront cache:**
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id YOUR_DIST_ID \
     --paths "/churchcoursetracker/*"
   ```

### CI/CD Integration

The deployment can be automated using GitHub Actions:

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'docs-site/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd docs-site
          pip install -r requirements.txt
          mkdocs build
          # Add S3 sync and CloudFront invalidation steps
```

---

## Customization

### Changing Colors

Edit `theme/custom.css`:

```css
:root {
  --cct-primary: #667eea;
  --cct-secondary: #764ba2;
}
```

### Modifying Navigation

Edit `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Your Section:
    - Page 1: page1.md
    - Page 2: page2.md
```

### Custom Footer

Edit `docs_overrides/partials/footer.html` to add custom links or content.

### SEO Settings

Edit `docs_overrides/main.html` to modify:
- Meta tags
- Open Graph tags
- Twitter Card tags
- Keywords

---

## Troubleshooting

### Server Won't Start

**Problem**: `mkdocs serve` fails to start

**Solutions**:
1. Check Python version: `python3 --version` (needs 3.11+)
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check for port conflicts: `lsof -i :8000`

### Images Not Showing

**Problem**: Screenshots don't appear in the documentation

**Solutions**:
1. Verify image path is correct (relative to `docs/` directory)
2. Check file exists: `ls docs/images/screenshots/...`
3. Ensure image file is not corrupted
4. Check file permissions

### Build Errors

**Problem**: `mkdocs build` fails

**Solutions**:
1. Check for syntax errors in Markdown files
2. Verify all referenced files exist
3. Check `mkdocs.yml` for configuration errors
4. Review error messages for specific issues

### Search Not Working

**Problem**: Search functionality doesn't work

**Solutions**:
1. Rebuild the site: `mkdocs build`
2. Clear browser cache
3. Check that search plugin is enabled in `mkdocs.yml`

### Styling Issues

**Problem**: Custom CSS not applying

**Solutions**:
1. Verify `extra_css` is set in `mkdocs.yml`
2. Check file path is correct
3. Rebuild the site
4. Clear browser cache

---

## Best Practices

### Content Writing

1. **Use clear, simple language** - Write for non-technical users
2. **Include examples** - Show, don't just tell
3. **Add screenshots** - Visual aids are invaluable
4. **Keep it organized** - Use headings and structure
5. **Test your changes** - Always preview before committing

### Screenshot Guidelines

1. **Use consistent resolution** - 1920x1080 recommended
2. **Hide sensitive data** - Use test accounts and data
3. **Add annotations** - Highlight important areas
4. **Optimize file sizes** - Keep images under 500KB
5. **Update when UI changes** - Keep screenshots current

### Maintenance

1. **Regular updates** - Keep content current with application changes
2. **Review screenshots** - Update when UI changes
3. **Test links** - Verify all links work
4. **Check search** - Ensure search returns relevant results
5. **Monitor feedback** - Address user questions and suggestions

---

## Resources

### Documentation

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)

### Support

- **Project Repository**: [GitHub](https://github.com/qspencer/church-course-tracker)
- **Application**: [https://apps.quentinspencer.com](https://apps.quentinspencer.com)
- **API Documentation**: [https://api.quentinspencer.com/docs](https://api.quentinspencer.com/docs)

---

## Quick Reference

### Common Commands

```bash
# Start development server
mkdocs serve

# Build site
mkdocs build

# Capture screenshots
node scripts/capture-screenshots.js

# Deploy to production
./scripts/deploy.sh
```

### File Locations

- **Configuration**: `mkdocs.yml`
- **Source Files**: `docs/`
- **Screenshots**: `docs/images/screenshots/`
- **Custom CSS**: `theme/custom.css`
- **Build Output**: `site/`

---

!!! tip "Need Help?"
    If you encounter issues or have questions about maintaining the documentation, refer to the troubleshooting section above or check the MkDocs and Material for MkDocs documentation.

