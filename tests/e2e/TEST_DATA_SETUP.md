# E2E Test Data Setup

This document describes how test data is automatically loaded and cleaned up for E2E tests.

## Overview

The E2E test suite automatically loads CSV test data before tests run and cleans it up after tests complete. This ensures tests have consistent, predictable data to work with.

## How It Works

### Global Setup (`global-setup.ts`)

Before all tests run:
1. Calls `setup-test-data.py` to load CSV data into the database
2. Uses `EnhancedCSVDataLoader` which tracks data source as "csv"
3. Only loads data if it doesn't already exist (unless `--force` is used)

### Global Teardown (`global-teardown.ts`)

After all tests complete:
1. Calls `teardown-test-data.py` to remove CSV-loaded data
2. Uses `EnhancedCSVDataLoader.clear_csv_data_only()` method
3. Only removes data that was loaded from CSV, preserving user-entered data

## Configuration

### Environment Variables

- **`E2E_SKIP_DATA_LOAD`**: Set to `true` to skip data loading (useful when testing against production)
- **`E2E_SKIP_DATA_CLEANUP`**: Set to `true` to skip data cleanup (useful when testing against production)

### CSV Data Location

The scripts use the `CSV_DATA_DIR` setting from the backend config, which defaults to `data/csv` relative to the backend directory.

## Usage

### Normal Operation (with database access)

```bash
# Run tests - data will be loaded automatically
npx playwright test
```

### Production Testing (without database access)

```bash
# Skip data loading/cleanup when testing against production
E2E_SKIP_DATA_LOAD=true E2E_SKIP_DATA_CLEANUP=true npx playwright test
```

### Manual Data Management

```bash
# Load test data manually
python3 tests/e2e/setup-test-data.py --force

# Clear test data manually
python3 tests/e2e/teardown-test-data.py
```

## What Data Is Loaded

The CSV loader loads the following data types (in dependency order):

1. **Campuses** - Church campus locations
2. **Roles** - User roles (admin, staff, viewer)
3. **Users** - Test user accounts
4. **People** - Member/people records
5. **Courses** - Course definitions
6. **Modules** - Course modules
7. **Content** - Course content items
8. **Enrollments** - Course enrollments

## Data Source Tracking

The `EnhancedCSVDataLoader` tracks which data was loaded from CSV by:
- Setting `data_source = "csv"` on all loaded records
- Setting `csv_loaded_at` timestamp

This allows selective cleanup - only CSV-loaded data is removed, preserving any data that was manually entered or loaded from other sources.

## Troubleshooting

### "ModuleNotFoundError: No module named 'sqlalchemy'"

This means the backend Python dependencies aren't installed. Options:
1. Install backend dependencies: `cd backend && pip install -r requirements.txt`
2. Or set `E2E_SKIP_DATA_LOAD=true` if testing against production

### "Could not import backend modules"

This is expected when testing against production without database access. Set `E2E_SKIP_DATA_LOAD=true` to skip data loading.

### Data not loading

Check:
1. CSV files exist in `backend/data/csv/` directory
2. Database connection is configured correctly
3. User has permissions to insert data
4. Check logs for specific error messages

### Data not cleaning up

The cleanup only removes data with `data_source = "csv"`. If data was loaded with the old `CSVDataLoader` (without source tracking), it won't be cleaned up automatically. You may need to manually clean it up or reload it with the enhanced loader.

## Best Practices

1. **Use EnhancedCSVDataLoader** - Always use the enhanced loader for test data to enable selective cleanup
2. **Skip in Production** - Always set skip flags when testing against production
3. **Force Reload** - Use `--force` flag to reload data if schema changes
4. **Verify Cleanup** - Check that cleanup worked by verifying CSV data counts are zero after teardown

