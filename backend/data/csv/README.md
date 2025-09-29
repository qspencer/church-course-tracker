# CSV Data Loading System

This directory contains CSV files with test data for the Church Course Tracker application. The application can automatically load this data on startup to provide a populated database for development, testing, and demos.

## Quick Start

1. **Enable CSV loading** by setting environment variables:
   ```bash
   export LOAD_CSV_DATA=true
   export CSV_DATA_DIR=data/csv
   ```

2. **Create sample data** (if not already present):
   ```bash
   python scripts/csv_data_manager.py create
   ```

3. **Load data into database**:
   ```bash
   python scripts/csv_data_manager.py load
   ```

4. **Start the application** - data will be loaded automatically on startup.

## CSV Files

| File | Description | Records |
|------|-------------|---------|
| `campuses.csv` | Church campuses | 3 campuses |
| `roles.csv` | User roles and permissions | 3 roles |
| `users.csv` | System users | 4 users |
| `people.csv` | Church members | 5 people |
| `courses.csv` | Course offerings | 5 courses |
| `modules.csv` | Course modules | 6 modules |
| `content.csv` | Course content items | 6 content items |
| `enrollments.csv` | Course enrollments | 6 enrollments |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOAD_CSV_DATA` | `false` | Enable CSV data loading on startup |
| `CSV_DATA_DIR` | `data/csv` | Directory containing CSV files |
| `FORCE_RELOAD_CSV` | `false` | Force reload data even if it exists |

## Management Commands

Use the CSV data manager script for common operations:

```bash
# Create sample CSV files
python scripts/csv_data_manager.py create

# Load data into database
python scripts/csv_data_manager.py load

# Force reload data (overwrites existing)
python scripts/csv_data_manager.py load --force

# Show database summary
python scripts/csv_data_manager.py summary

# Clear all database data (WARNING!)
python scripts/csv_data_manager.py clear

# Complete setup (create + load + summary)
python scripts/csv_data_manager.py full-setup
```

## CSV File Format

Each CSV file follows a specific format with required and optional columns:

### campuses.csv
```csv
name,address,city,state,zip_code,phone,email,is_active
Main Campus,123 Church St,Anytown,CA,12345,555-1234,main@church.com,true
```

### users.csv
```csv
username,email,password,full_name,role,is_active
admin,admin@church.com,admin123,Administrator,admin,true
```

### courses.csv
```csv
title,description,duration_weeks,max_capacity,is_active
Introduction to Faith,A foundational course on Christian faith,6,30,true
```

### And so on...

## Data Relationships

The CSV files are loaded in dependency order:
1. **Campuses** → **Roles** → **Users**
2. **People** (linked to campuses)
3. **Courses** → **Modules** → **Content**
4. **Enrollments** (linking people to courses)

## Customization

To customize the test data:

1. **Edit existing CSV files** in this directory
2. **Add new records** following the same format
3. **Create new CSV files** for additional data types
4. **Modify the CSV loader** in `app/core/csv_loader.py` to handle new data types

## Troubleshooting

### Data not loading
- Check that `LOAD_CSV_DATA=true` is set
- Verify CSV files exist in the correct directory
- Check application logs for error messages

### Duplicate data
- Set `FORCE_RELOAD_CSV=true` to overwrite existing data
- Or clear the database first: `python scripts/csv_data_manager.py clear`

### Missing relationships
- Ensure CSV files are loaded in the correct order
- Check that referenced records exist (e.g., course titles in modules.csv must match courses.csv)

## Development Workflow

1. **Start with sample data**: `python scripts/csv_data_manager.py full-setup`
2. **Develop and test** with populated database
3. **Modify CSV files** as needed for testing scenarios
4. **Reload data** when changes are made: `python scripts/csv_data_manager.py load --force`
5. **Clear data** when done: `python scripts/csv_data_manager.py clear`

This system makes it easy to maintain consistent test data across different environments and team members.
