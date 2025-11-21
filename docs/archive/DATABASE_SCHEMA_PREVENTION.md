# Database Schema Prevention Strategy

This document outlines the comprehensive strategy to prevent database schema mismatches before they cause runtime errors.

## Problem

Previously, we encountered multiple database schema issues:
- Missing tables (`content_audit_logs`, `content_access_logs`)
- Missing columns (`changed_at`, `ip_address`, `user_agent` in `audit_log`)
- Wrong constraints (`module_name` NOT NULL when it should be nullable)
- Alembic migration failures (multiple heads)

## Prevention Strategy

### 1. Dynamic Schema Validation

**Location**: `backend/scripts/schema_validator.py`

This script:
- Reads SQLAlchemy models directly (no hardcoding)
- Compares models to actual database schema
- Identifies missing tables, columns, and constraint mismatches
- Provides detailed error reports

**Usage**:
```bash
python3 backend/scripts/schema_validator.py
```

**Integration**: Runs automatically in `start.sh` after migrations

### 2. Alembic Head Fixing

**Location**: `backend/scripts/fix_alembic_heads.py`

This script:
- Detects multiple Alembic head revisions
- Automatically creates merge migrations
- Prevents migration failures

**Usage**:
```bash
python3 backend/scripts/fix_alembic_heads.py
```

**Integration**: Runs automatically in `start.sh` before migrations

### 3. Pre-Deployment Checks

**Location**: `backend/scripts/pre_deployment_check.py`

This script:
- Runs schema validation before deployment
- Fails CI/CD if schema issues are found
- Provides actionable error messages

**Usage**:
```bash
python3 backend/scripts/pre_deployment_check.py
```

**Integration**: Should be added to CI/CD pipeline

### 4. Enhanced Startup Script

**Location**: `backend/start.sh`

The startup script now:
1. Fixes Alembic multiple heads (if any)
2. Runs migrations
3. Validates schema against models
4. Runs comprehensive schema fixes (creates missing tables/columns)
5. Provides detailed logging

### 5. Comprehensive Schema Fixes

**Location**: `backend/start.sh` (Python section)

The schema fix script:
- Creates missing tables (`content_audit_logs`, `content_access_logs`)
- Adds missing columns to existing tables
- Fixes constraint issues (NOT NULL → nullable)
- Tracks all changes with summary reports

## Best Practices

### When Adding New Models

1. **Create an Alembic migration**:
   ```bash
   alembic revision --autogenerate -m "add_new_model"
   ```

2. **Test the migration locally**:
   ```bash
   alembic upgrade head
   ```

3. **Run schema validator**:
   ```bash
   python3 backend/scripts/schema_validator.py
   ```

4. **Fix any issues** before committing

### When Modifying Existing Models

1. **Create an Alembic migration** for the change
2. **Test locally** before pushing
3. **Run pre-deployment check**:
   ```bash
   python3 backend/scripts/pre_deployment_check.py
   ```

### When Adding New Columns

1. **Add to SQLAlchemy model** first
2. **Create Alembic migration**:
   ```bash
   alembic revision --autogenerate -m "add_column_name"
   ```
3. **Verify schema** matches model

## CI/CD Integration

### Recommended GitHub Actions Step

Add this to your workflow before deployment:

```yaml
- name: Check database schema
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
  run: |
    python3 backend/scripts/pre_deployment_check.py
```

### Manual Pre-Deployment Check

Before deploying, run:
```bash
export DATABASE_URL="your_database_url"
python3 backend/scripts/pre_deployment_check.py
```

## Monitoring

The `start.sh` script logs:
- Schema validation results
- Missing tables/columns found
- Schema fixes applied
- Summary of all changes

Check CloudWatch logs for:
- `Schema Validation Report`
- `COLUMN CHECK SUMMARY`
- Any schema validation errors

## Troubleshooting

### Multiple Alembic Heads

**Symptom**: `Multiple head revisions are present`

**Solution**: Run `fix_alembic_heads.py` or manually:
```bash
alembic merge heads -m "merge_heads"
alembic upgrade head
```

### Missing Tables

**Symptom**: `relation "table_name" does not exist`

**Solution**: 
1. Check if table is in SQLAlchemy models
2. Run schema validator to confirm
3. Create Alembic migration or let `start.sh` auto-create

### Missing Columns

**Symptom**: `column "column_name" does not exist`

**Solution**:
1. Verify column exists in SQLAlchemy model
2. Run schema validator
3. Create migration or let `start.sh` auto-add

## Future Improvements

1. **Automated Migration Generation**: Create migrations automatically on model changes
2. **Schema Versioning**: Track schema versions in database
3. **Rollback Support**: Ability to rollback schema changes
4. **Testing**: Integration tests that verify schema matches models
5. **Documentation**: Auto-generate schema documentation from models

