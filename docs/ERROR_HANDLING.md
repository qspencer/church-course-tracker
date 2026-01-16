# Error Handling Guide

This document describes the error handling patterns and best practices used in the Church Course Tracker application.

## Table of Contents

- [Custom Exception Classes](#custom-exception-classes)
- [Backend Error Handling Patterns](#backend-error-handling-patterns)
- [Frontend Error Handling](#frontend-error-handling)
- [Transaction Management](#transaction-management)
- [Testing Error Handling](#testing-error-handling)

---

## Custom Exception Classes

Located in `backend/app/core/exceptions.py`, we have defined application-specific exceptions for better error context and handling.

### Exception Hierarchy

```python
# Planning Center API Errors
PlanningCenterAPIError (base)
├── PlanningCenterAuthenticationError (401)
├── PlanningCenterRateLimitError (429)
└── PlanningCenterNotFoundError (404)

# Application Errors
DatabaseTransactionError
AuditLogError
ValidationError
```

### Usage Examples

#### Planning Center API Errors

```python
from app.core.exceptions import (
    PlanningCenterAPIError,
    PlanningCenterAuthenticationError,
    PlanningCenterRateLimitError
)

try:
    response = await client.get(url, headers=headers)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise PlanningCenterAuthenticationError(
            "Authentication failed",
            status_code=401
        )
    elif e.response.status_code == 429:
        raise PlanningCenterRateLimitError(
            "Rate limit exceeded",
            status_code=429
        )
```

#### Validation Errors

```python
from app.core.exceptions import ValidationError

def search_people(search_term: str):
    if not search_term or len(search_term) < 2:
        raise ValidationError("Search term must be at least 2 characters")

    if len(search_term) > 100:
        raise ValidationError("Search term is too long (max 100 characters)")
```

---

## Backend Error Handling Patterns

### HTTP/API Operations

Always use specific exception types for HTTP operations:

```python
import httpx
from app.core.exceptions import PlanningCenterAPIError

try:
    response = await client.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    return response.json()

except httpx.TimeoutException:
    logger.warning(f"Request timed out: {url}")
    raise PlanningCenterAPIError("Request timed out", status_code=504)

except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        raise PlanningCenterAuthenticationError("Auth failed", status_code=401)
    elif e.response.status_code == 429:
        raise PlanningCenterRateLimitError("Rate limit", status_code=429)
    elif e.response.status_code == 404:
        raise PlanningCenterNotFoundError("Not found", status_code=404)
    else:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
        raise PlanningCenterAPIError(f"HTTP {e.response.status_code}")

except httpx.ConnectError as e:
    logger.error(f"Connection error: {e}")
    raise PlanningCenterAPIError("Cannot connect to Planning Center")

except httpx.RequestError as e:
    logger.error(f"Request error: {e}")
    raise PlanningCenterAPIError(f"Request failed: {str(e)}")

except ValueError as e:  # JSON decode errors
    logger.error(f"Invalid JSON response: {e}")
    raise PlanningCenterAPIError("Invalid response format")

except Exception as e:
    # Only truly unexpected errors
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### When to Keep Broad Exception Handlers

Broad `except Exception` handlers are appropriate for:

1. **Top-level background task handlers**
   ```python
   def run_sync():
       try:
           asyncio.run(self._sync_background(task_id))
           logger.info(f"Sync {task_id} completed")
       except Exception as e:
           logger.error(f"Sync {task_id} failed: {e}", exc_info=True)
           self._update_task_status(task_id, 'failed', str(e))
   ```

2. **Batch processing loops** (continue on individual failures)
   ```python
   for item in items:
       try:
           process_item(item)
       except Exception as e:
           errors.append(f"Item {item.id}: {str(e)}")
           continue  # Process remaining items
   ```

3. **Final defensive wrappers** (after specific handlers)

### Exception Handler Decorators

Use the provided decorators for consistent error handling in endpoints:

```python
from app.core.exceptions import planning_center_exception_handler

@router.get("/sync")
@planning_center_exception_handler
async def sync_people():
    # Planning Center API calls
    # Exceptions automatically converted to HTTP responses
    pass
```

The decorator handles:
- `PlanningCenterAuthenticationError` → 401 Unauthorized
- `PlanningCenterRateLimitError` → 429 Too Many Requests
- `PlanningCenterNotFoundError` → 404 Not Found
- `PlanningCenterAPIError` → 502 Bad Gateway
- `ValidationError` → 400 Bad Request
- `DatabaseTransactionError` → 500 Internal Server Error

---

## Frontend Error Handling

### LoggerService Integration

All frontend errors should use LoggerService for consistent handling:

```typescript
import { LoggerService } from './services/logger.service';

constructor(private logger: LoggerService) {}

performAction(): void {
  this.service.doSomething().subscribe({
    next: (result) => this.handleSuccess(result),
    error: (error) => {
      this.logger.error('Action failed', error, {
        component: 'ComponentName',
        action: 'performAction',
        userId: this.currentUserId
      });
      this.snackBar.open('Action failed', 'Close', { duration: 5000 });
    }
  });
}
```

### Loading State Management

Always use RxJS `finalize()` operator for loading states:

```typescript
import { finalize } from 'rxjs/operators';

save(): void {
  if (this.isSaving) return;  // Prevent double-submission

  this.isSaving = true;
  this.service.save(data)
    .pipe(finalize(() => this.isSaving = false))  // Always resets
    .subscribe({
      next: (result) => this.dialogRef.close(result),
      error: (error) => {
        this.logger.error('Save failed', error, {
          component: 'DialogName',
          action: 'save'
        });
        this.snackBar.open('Failed to save', 'Close', { duration: 5000 });
      }
    });
}
```

**Benefits:**
- Loading state always resets (success or error)
- No UI stuck in loading state
- Prevents double-submission
- Cleaner code (no duplication)

---

## Transaction Management

### Atomic Operations with Audit Logs

Use `flush()` instead of `commit()` to ensure audit logs and data changes are atomic:

**❌ Wrong Pattern:**
```python
def create_record(data):
    record = Model(**data)
    db.add(record)
    db.commit()  # ❌ If audit fails, record already saved!
    db.refresh(record)

    AuditService(db).log_change(...)  # Not in same transaction
```

**✅ Correct Pattern:**
```python
def create_record(data):
    try:
        record = Model(**data)
        db.add(record)
        db.flush()  # Get ID without committing

        AuditService(db).log_change(...)  # In same transaction

        db.commit()  # Commit both together
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()  # Rollback both if either fails
        logger.error(f"Transaction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Operation failed")
```

### Transaction Consistency Checklist

- [ ] Use `db.flush()` before audit logging
- [ ] Place audit log in same transaction
- [ ] Single `db.commit()` after all operations
- [ ] `db.rollback()` in exception handler
- [ ] Proper logging with `exc_info=True`

---

## Testing Error Handling

### Unit Tests for Specific Exceptions

```python
import pytest
from unittest.mock import Mock, patch
import httpx
from app.core.exceptions import PlanningCenterAPIError

def test_timeout_error():
    with patch('httpx.AsyncClient.get', side_effect=httpx.TimeoutException()):
        with pytest.raises(PlanningCenterAPIError) as exc:
            await sync_service.fetch_data(url)
        assert exc.value.status_code == 504

def test_authentication_error():
    mock_response = Mock(status_code=401)
    with patch('httpx.AsyncClient.get', side_effect=httpx.HTTPStatusError(
        "Unauthorized", request=Mock(), response=mock_response
    )):
        with pytest.raises(PlanningCenterAuthenticationError):
            await sync_service.fetch_data(url)
```

### Integration Tests for Transactions

```python
def test_audit_failure_rolls_back_creation(db_session):
    """Verify rollback when audit fails"""
    with patch.object(AuditService, 'log_change',
                     side_effect=Exception("Audit failed")):
        with pytest.raises(HTTPException):
            course_service.create_course(course_data, created_by=1)

        # Verify course NOT created
        assert db_session.query(Course).count() == 0

def test_successful_creation_with_audit(db_session):
    """Verify both record and audit log created"""
    course = course_service.create_course(course_data, created_by=1)
    assert course.id is not None

    audit = db_session.query(AuditLog).filter_by(
        table_name='courses',
        record_id=course.id
    ).first()
    assert audit is not None
```

### Frontend Error Testing

```typescript
describe('ComponentName', () => {
  let logger: jasmine.SpyObj<LoggerService>;

  beforeEach(() => {
    const loggerSpy = jasmine.createSpyObj('LoggerService', ['error']);
    TestBed.configureTestingModule({
      providers: [{ provide: LoggerService, useValue: loggerSpy }]
    });
    logger = TestBed.inject(LoggerService) as jasmine.SpyObj<LoggerService>;
  });

  it('should log errors with context', () => {
    component.performAction();

    expect(logger.error).toHaveBeenCalledWith(
      'Action failed',
      jasmine.any(Error),
      jasmine.objectContaining({
        component: 'ComponentName',
        action: 'performAction'
      })
    );
  });

  it('should reset loading state on error', fakeAsync(() => {
    component.isSaving = true;

    // Trigger error
    tick();

    expect(component.isSaving).toBe(false);
  }));
});
```

---

## Best Practices Summary

### Backend

✅ **Do:**
- Use specific exception types for HTTP/API operations
- Keep broad handlers for top-level/batch processing
- Use `flush()` before audit logging
- Log with context and `exc_info=True`
- Use exception handler decorators

❌ **Don't:**
- Use bare `except:` clauses
- Commit before audit logging
- Swallow exceptions silently
- Use generic error messages
- Mix transaction boundaries

### Frontend

✅ **Do:**
- Use LoggerService for all error logging
- Use `finalize()` for loading states
- Add double-submission guards
- Include component context in logs
- Show user-friendly error messages

❌ **Don't:**
- Use console.log/console.error directly
- Manually reset loading states in next/error
- Let UI stuck in loading state
- Show technical errors to users
- Forget to log errors

---

## Additional Resources

- [Backend Custom Exceptions](../backend/app/core/exceptions.py)
- [Frontend LoggerService](../frontend/church-course-tracker/src/app/services/logger.service.ts)
- [Logging Guide](./LOGGING.md)
- [Sentry Documentation](https://docs.sentry.io/)
