# Church Course Tracker Documentation Site

This directory contains the source files for the Church Course Tracker documentation website.

## 📚 Documentation URL

The documentation is available at: **https://docs.quentinspencer.com/churchcoursetracker/**

## 🛠️ Development

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Serve documentation locally:
   ```bash
   mkdocs serve
   ```

3. Access at: http://127.0.0.1:8000

### Building

Build the static site:

```bash
mkdocs build
```

Output will be in the `site/` directory.

### Project Structure

```
docs-site/
├── docs/                    # Source Markdown files
│   ├── index.md            # Home page
│   ├── getting-started.md  # Getting started guide
│   ├── user-guide.md       # Complete user guide
│   └── features.md         # Features overview
├── mkdocs.yml              # MkDocs configuration
├── requirements.txt        # Python dependencies
├── docs_overrides/         # Theme customizations
└── theme/                  # Custom CSS
```

## 📝 Updating Documentation

1. Edit the Markdown files in the `docs/` directory
2. Test locally: `mkdocs serve`
3. Build: `mkdocs build`
4. Commit and push changes (auto-deploys via GitHub Actions)

## 🚀 Deployment

The documentation is automatically deployed when changes are pushed to the main branch. The deployment process:

1. Builds the documentation site
2. Uploads to S3 bucket
3. Invalidates CloudFront cache

See `.github/workflows/deploy-docs.yml` for the deployment workflow.

## 🔗 Links

- **Live Documentation**: https://docs.quentinspencer.com/churchcoursetracker/
- **Main Application**: https://apps.quentinspencer.com
- **API Documentation**: https://api.quentinspencer.com/docs


