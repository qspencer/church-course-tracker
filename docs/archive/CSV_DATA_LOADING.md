# CSV Data Loading System Documentation

## Overview

The Church Course Tracker includes a comprehensive CSV data loading system that allows you to populate the database with test data from CSV files. This system is particularly useful for development, testing, and demonstration purposes.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [CSV File Format](#csv-file-format)
- [Management Commands](#management-commands)
- [Integration](#integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Source Tracking System](#source-tracking-system)

## Features

### Core Capabilities
- **Automatic Loading**: CSV data loads automatically when the application starts (if enabled)
- **Dependency Management**: Data loads in the correct order to maintain referential integrity
- **Error Handling**: Graceful handling of missing files and invalid data
- **Logging**: Comprehensive logging of the loading process
- **Safety**: CSV loading is disabled by default to protect production data
- **Source Tracking**: ⭐ **NEW** - Tracks data source (CSV, manual, API) for selective management
- **Selective Clearing**: ⭐ **NEW** - Remove only CSV data while preserving user data

### Data Types Supported
- **Campuses**: Church locations and campuses
- **Roles**: User roles and permissions
- **Users**: System user accounts
- **People**: Church members and attendees
- **Courses**: Course offerings and programs
- **Modules**: Course modules and sections
- **Content**: Course content and materials
- **Enrollments**: Course enrollments and registrations

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    CSV Data Loading System                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   CSV Files     │    │  CSV Loader     │                │
│  │   (data/csv/)   │───▶│  (csv_loader.py)│                │
│  └─────────────────┘    └─────────────────┘                │
│                                │                            │
│                                ▼                            │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Data Manager   │    │   Database      │                │
│  │ (csv_data_mgr) │───▶│   (SQLAlchemy)  │                │
│  └─────────────────┘    └─────────────────┘                │
│                                │                            │
│                                ▼                            │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  FastAPI App    │    │   Application   │                │
│  │  (main.py)      │◀───│   Startup       │                │
│  └─────────────────┘    └─────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
backend/
├── app/
│   └── core/
│       ├── csv_loader.py          # Original CSV loading logic
│       └── enhanced_csv_loader.py # Enhanced CSV loader with source tracking
├── data/
│   └── csv/                      # CSV data files
│       ├── campuses.csv
│       ├── roles.csv
│       ├── users.csv
│       ├── people.csv
│       ├── courses.csv
│       ├── modules.csv
│       ├── content.csv
│       └── enrollments.csv
├── scripts/
│   └── csv_data_manager.py       # CLI management tool
├── main.py                       # Application entry point
└── env.csv.example              # Environment configuration
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOAD_CSV_DATA` | `false` | Enable CSV data loading on startup |
| `CSV_DATA_DIR` | `data/csv` | Directory containing CSV files |
| `FORCE_RELOAD_CSV` | `false` | Force reload data even if it exists |

### Configuration Example

```bash
# Enable CSV data loading
export LOAD_CSV_DATA=true

# Set custom data directory
export CSV_DATA_DIR=data/csv

# Force reload on every startup (development only)
export FORCE_RELOAD_CSV=true
```

### Application Integration

The CSV loading system is integrated into the FastAPI application startup process:

```python
# In main.py
@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("Starting Church Course Tracker API...")
    
    # Load CSV data if enabled
    try:
        load_csv_data_on_startup()
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")
    
    logger.info("Application startup completed")
```

## Usage

### Quick Start

1. **Enable CSV Loading**:
   ```bash
   export LOAD_CSV_DATA=true
   ```

2. **Create Sample Data**:
   ```bash
   cd backend
   python scripts/csv_data_manager.py full-setup
   ```

3. **Start Application**:
   ```bash
   python main.py
   ```

### Manual Data Management

```bash
# Create sample CSV files
python scripts/csv_data_manager.py create

# Load data into database
python scripts/csv_data_manager.py load

# Force reload data (overwrites existing)
python scripts/csv_data_manager.py load --force

# Show database summary
python scripts/csv_data_manager.py summary

# Show CSV data summary only (NEW)
python scripts/csv_data_manager.py csv-summary

# Clear only CSV data (SAFE - preserves user data)
python scripts/csv_data_manager.py clear-csv

# Clear all database data (WARNING!)
python scripts/csv_data_manager.py clear
```

## CSV File Format

### Campuses (`campuses.csv`)

```csv
name,address,phone,email,is_active
Main Campus,123 Church St,555-1234,main@church.com,true
North Campus,456 North Ave,555-5678,north@church.com,true
South Campus,789 South Blvd,555-9012,south@church.com,true
```

### Roles (`roles.csv`)

```csv
name,description,permissions,is_active
admin,Administrator,["all"],true
staff,Church Staff,["read","write","manage_courses"],true
viewer,Course Viewer,["read"],true
```

### Users (`users.csv`)

```csv
username,email,password,full_name,role,is_active
admin,admin@church.com,admin123,Administrator,admin,true
staff,staff@church.com,staff123,Church Staff,staff,true
viewer,viewer@church.com,viewer123,Course Viewer,viewer,true
pastor,pastor@church.com,pastor123,Pastor John,admin,true
```

### People (`people.csv`)

```csv
first_name,last_name,email,phone,address,city,state,zip_code,campus,is_active
John,Doe,john@example.com,555-0001,123 Main St,Anytown,CA,12345,Main Campus,true
Jane,Smith,jane@example.com,555-0002,456 Oak Ave,Anytown,CA,12345,Main Campus,true
```

### Courses (`courses.csv`)

```csv
title,description,duration_weeks,max_capacity,is_active
Introduction to Faith,A foundational course on Christian faith and beliefs,6,30,true
Bible Study Methods,Learn how to study and interpret the Bible effectively,8,25,true
Church History,Explore the history of Christianity and the church,10,20,true
```

### Modules (`modules.csv`)

```csv
course_title,title,description,order_index,is_active
Introduction to Faith,What is Faith?,Understanding the concept of faith in Christianity,1,true
Introduction to Faith,The Trinity,"Exploring the Father, Son, and Holy Spirit",2,true
Bible Study Methods,Reading the Bible,How to read and understand biblical texts,1,true
```

### Content (`content.csv`)

```csv
course_title,module_title,title,description,content_type,storage_type,order_index,is_active
Introduction to Faith,What is Faith?,Faith Definition Video,A video explaining the definition of faith,video,database,1,true
Introduction to Faith,What is Faith?,Faith Study Guide,A comprehensive study guide on faith,document,database,2,true
Introduction to Faith,The Trinity,Trinity Explained,Understanding the concept of the Trinity,document,database,1,true
```

### Enrollments (`enrollments.csv`)

```csv
course_title,first_name,last_name,status,is_active
Introduction to Faith,John,Doe,enrolled,true
Introduction to Faith,Jane,Smith,enrolled,true
Bible Study Methods,John,Doe,enrolled,true
Bible Study Methods,Bob,Johnson,enrolled,true
```

## Management Commands

### Command Line Interface

```bash
python scripts/csv_data_manager.py [command] [options]
```

### Available Commands

#### `create`
Creates sample CSV files with realistic test data.

```bash
python scripts/csv_data_manager.py create
```

#### `load`
Loads CSV data into the database.

```bash
# Load data (skip if already exists)
python scripts/csv_data_manager.py load

# Force reload data (overwrites existing)
python scripts/csv_data_manager.py load --force
```

#### `summary`
Shows a summary of data in the database.

```bash
python scripts/csv_data_manager.py summary
```

#### `csv-summary` ⭐ **NEW**
Shows a summary of CSV-loaded data only (with source tracking).

```bash
python scripts/csv_data_manager.py csv-summary
```

**Example Output:**
```
📊 CSV Data Summary (CSV-loaded data only):
==================================================
  CSV Users: 4
  CSV Courses: 5
  CSV Modules: 0
  CSV Content: 0
  CSV People: 5
  CSV Campuses: 3
  CSV Roles: 3
  CSV Enrollments: 0

✅ Total CSV-loaded records: 20
💡 Use 'clear-csv' command to remove only CSV data
```

#### `clear-csv` ⭐ **NEW - SAFE**
Clears only CSV-loaded data, preserving user-entered data.

```bash
python scripts/csv_data_manager.py clear-csv
```

**✅ SAFE:** This only removes data that was loaded from CSV files, preserving:
- User-created courses, users, people, etc.
- Data entered through the API
- Data entered through the web interface
- Any data not marked with `data_source='csv'`

**Example:**
```bash
# Before clearing CSV data
📊 Database Summary:
  Users: 5 (CSV: 4, Manual: 1)
  Courses: 6 (CSV: 5, Manual: 1)

# After clearing CSV data
📊 Database Summary:
  Users: 1 (CSV: 0, Manual: 1)  # CSV users removed, manual user preserved
  Courses: 1 (CSV: 0, Manual: 1)  # CSV courses removed, manual course preserved
```

#### `clear`
Clears all data from the database (WARNING: Destructive operation).

```bash
python scripts/csv_data_manager.py clear
```

**⚠️ WARNING:** This will delete ALL data from the database!

#### `full-setup`
Performs complete setup: creates CSV files, loads data, and shows summary.

```bash
python scripts/csv_data_manager.py full-setup
```

### Command Options

- `--force`: Force reload data even if it already exists
- `--data-dir DATA_DIR`: Override the CSV data directory
- `--help`: Show help message

## Integration

### Application Startup

The CSV loading system is automatically integrated into the FastAPI application startup process:

```python
# In app/core/csv_loader.py
def load_csv_data_on_startup(force_reload: bool = None):
    """
    Load CSV data when the application starts up
    """
    try:
        from app.core.config import settings
        
        if not settings.LOAD_CSV_DATA:
            logger.info("CSV data loading is disabled")
            return
        
        data_dir = settings.CSV_DATA_DIR
        if not os.path.exists(data_dir):
            logger.warning(f"CSV data directory not found: {data_dir}")
            return
        
        if force_reload is None:
            force_reload = settings.FORCE_RELOAD_CSV
        
        loader = CSVDataLoader(data_dir)
        db = next(get_db())
        
        try:
            results = loader.load_all_data(db, force_reload)
            logger.info(f"Successfully loaded CSV data: {results}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")
```

### Database Integration

The system uses SQLAlchemy ORM for database operations:

```python
class CSVDataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def load_all_data(self, db: Session, force_reload: bool = False) -> dict:
        results = {}
        results['campuses'] = self.load_campuses(db, force_reload)
        results['roles'] = self.load_roles(db, force_reload)
        results['users'] = self.load_users(db, force_reload)
        results['people'] = self.load_people(db, force_reload)
        results['courses'] = self.load_courses(db, force_reload)
        results['modules'] = self.load_modules(db, force_reload)
        results['content'] = self.load_content(db, force_reload)
        results['enrollments'] = self.load_enrollments(db, force_reload)
        db.commit()
        logger.info("✅ CSV data loaded successfully!")
        return results
```

## Troubleshooting

### Common Issues

#### 1. CSV Loading Disabled
**Problem**: CSV data is not loading on startup.

**Solution**: Check environment variables:
```bash
echo $LOAD_CSV_DATA  # Should be 'true'
echo $CSV_DATA_DIR   # Should point to data/csv
```

#### 2. Missing CSV Files
**Problem**: Error "CSV file not found".

**Solution**: Create CSV files:
```bash
python scripts/csv_data_manager.py create
```

#### 3. Database Connection Issues
**Problem**: Database connection errors during loading.

**Solution**: Check database configuration and ensure the database is accessible.

#### 4. Data Already Exists
**Problem**: "Data already exists" error when loading.

**Solution**: Use force reload:
```bash
python scripts/csv_data_manager.py load --force
```

### Debugging

Enable debug logging to see detailed information about the loading process:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Logs

The system provides comprehensive logging:

```
INFO:app.core.csv_loader:Loading CSV data from data/csv
INFO:app.core.csv_loader:Loading campuses...
INFO:app.core.csv_loader:✅ Loaded 3 campuses
INFO:app.core.csv_loader:Loading roles...
INFO:app.core.csv_loader:✅ Loaded 3 roles
INFO:app.core.csv_loader:✅ CSV data loaded successfully!
```

## Best Practices

### Development

1. **Use CSV Loading for Development**: Enable CSV loading in development environments for consistent test data.

2. **Version Control**: Keep CSV files in version control for team consistency.

3. **Customize Data**: Edit CSV files to match your specific testing needs.

### Production

1. **Disable in Production**: Keep `LOAD_CSV_DATA=false` in production environments.

2. **Backup Before Changes**: Always backup production data before making changes.

3. **Use Environment Variables**: Use environment variables for configuration rather than hardcoding values.

### Testing

1. **Isolated Test Data**: Use different CSV files for different test scenarios.

2. **Reset Between Tests**: Clear and reload data between test runs for consistency.

3. **Mock External Dependencies**: Mock external services when testing CSV loading.

### Data Management

1. **Regular Updates**: Keep CSV files updated with realistic data.

2. **Data Validation**: Validate CSV data before loading to catch errors early.

3. **Documentation**: Document any custom CSV file formats or requirements.

4. **Selective Clearing**: ⭐ **NEW** - Use `clear-csv` to remove only test data while preserving user data.

5. **Source Tracking**: ⭐ **NEW** - Monitor data sources with `csv-summary` to understand what data is CSV-loaded vs user-entered.

## Examples

### Custom CSV Data

To add custom data, edit the CSV files:

```csv
# Add a new course to courses.csv
title,description,duration_weeks,max_capacity,is_active
Advanced Theology,Deep dive into theological concepts,12,15,true
```

### Environment-Specific Configuration

```bash
# Development
export LOAD_CSV_DATA=true
export FORCE_RELOAD_CSV=true

# Staging
export LOAD_CSV_DATA=true
export FORCE_RELOAD_CSV=false

# Production
export LOAD_CSV_DATA=false
```

### Selective Data Management ⭐ **NEW**

```bash
# Load CSV test data
python scripts/csv_data_manager.py full-setup

# Add user data through web interface or API
# (data will be marked as 'manual' source)

# View only CSV data
python scripts/csv_data_manager.py csv-summary

# Clear only CSV data (preserves user data)
python scripts/csv_data_manager.py clear-csv

# Verify user data is preserved
python scripts/csv_data_manager.py summary
```

### Automated Testing

```python
# In test files
def test_csv_loading():
    # Load test data
    os.environ["LOAD_CSV_DATA"] = "true"
    os.environ["FORCE_RELOAD_CSV"] = "true"
    
    # Run application startup
    load_csv_data_on_startup(force_reload=True)
    
    # Verify data was loaded
    assert db.query(Course).count() > 0
    assert db.query(User).count() > 0
```

## 🔍 **Source Tracking System** ⭐ **NEW**

The enhanced CSV data loading system includes source tracking to distinguish between CSV-loaded data and user-entered data.

### **How It Works:**
- **CSV Data**: Marked with `data_source='csv'` and `csv_loaded_at` timestamp
- **User Data**: Marked with `data_source='manual'` or `data_source=None`
- **API Data**: Marked with `data_source='api'` (when implemented)

### **Benefits:**
- **Safe Clearing**: Remove only CSV data while preserving user data
- **Data Audit**: Track where data came from
- **Selective Management**: Different operations for different data sources

### **Database Schema:**
All relevant tables now include:
```sql
data_source VARCHAR(20)     -- 'csv', 'manual', 'api', etc.
csv_loaded_at DATETIME       -- When loaded from CSV
```

### **Example Usage:**
```bash
# Load CSV data (marked with source tracking)
python scripts/csv_data_manager.py full-setup

# Add user data (marked as 'manual')
# (through web interface or API)

# View CSV data only
python scripts/csv_data_manager.py csv-summary

# Clear only CSV data (preserves user data)
python scripts/csv_data_manager.py clear-csv
```

### **Safety Features:**
- ✅ **`clear-csv`**: Only removes CSV data, preserves user data
- ⚠️ **`clear`**: Removes ALL data (use with caution)
- 🔍 **`csv-summary`**: Shows only CSV data counts
- 📊 **`summary`**: Shows all data counts

## Conclusion

The CSV data loading system provides a powerful and flexible way to manage test data in the Church Course Tracker application. It supports development, testing, and demonstration scenarios while maintaining data integrity and providing comprehensive error handling.

**NEW:** The enhanced system now includes source tracking, allowing you to safely remove only CSV-loaded test data while preserving user-entered data. This makes it perfect for development environments where you need to reset test data without losing important user data.

For more information, see the [CSV Data Loading Guide](../backend/CSV_DATA_LOADING_GUIDE.md) and the [API Documentation](./API_DOCUMENTATION.md).
