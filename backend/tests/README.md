# Church Course Tracker - Backend Tests

This directory contains comprehensive tests for the Church Course Tracker backend application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_models.py              # SQLAlchemy model tests
├── test_schemas.py             # Pydantic schema tests
├── test_services.py            # Service layer tests
├── test_endpoints.py           # API endpoint tests
└── README.md                   # This file
```

## Test Categories

### 1. Model Tests (`test_models.py`)
Tests for all SQLAlchemy models including:
- **People Model**: Church member data and relationships
- **Campus Model**: Church campus information
- **Role Model**: User roles and permissions
- **Course Model**: Course/event data and Planning Center integration
- **Content Model**: Course content and materials
- **ContentType Model**: Extensible content type definitions
- **Certification Model**: Certification requirements and tracking
- **CourseEnrollment Model**: Enrollment data and progress tracking
- **Planning Center Models**: Integration and caching models
- **AuditLog Model**: Change tracking and audit trails

### 2. Schema Tests (`test_schemas.py`)
Tests for all Pydantic schemas including:
- **Validation**: Field validation and data types
- **Required Fields**: Enforcement of required fields
- **Optional Fields**: Proper handling of optional data
- **Default Values**: Correct default value assignment
- **Email Validation**: Email format validation
- **Date/Time Handling**: Proper datetime and date handling
- **Enum Validation**: Status and type enum validation
- **Nested Objects**: Complex object validation

### 3. Service Tests (`test_services.py`)
Tests for all service layer classes including:
- **PeopleService**: Member management operations
- **CourseService**: Course management and Planning Center sync
- **CourseEnrollmentService**: Enrollment and progress tracking
- **PlanningCenterSyncService**: Async sync operations and task management

### 4. Endpoint Tests (`test_endpoints.py`)
Tests for all API endpoints including:
- **People Endpoints**: CRUD operations for church members
- **Course Endpoints**: Course management and Planning Center integration
- **Enrollment Endpoints**: Enrollment management and progress tracking
- **Planning Center Sync Endpoints**: Async sync operations and webhooks

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
# Using pytest directly
pytest tests/ -v

# Using the test runner script
python run_tests.py

# With coverage reporting
pytest tests/ -v --cov=app --cov-report=html
```

### Run Specific Test Categories
```bash
# Model tests only
pytest tests/test_models.py -v

# Schema tests only
pytest tests/test_schemas.py -v

# Service tests only
pytest tests/test_services.py -v

# Endpoint tests only
pytest tests/test_endpoints.py -v
```

### Run Specific Test Files
```bash
# Run a specific test file
python run_tests.py test_models

# Or using pytest directly
pytest tests/test_models.py -v
```

### Run Tests with Markers
```bash
# Run only unit tests
pytest -m unit -v

# Run only integration tests
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v
```

## Test Configuration

### Fixtures (`conftest.py`)
The test configuration provides several useful fixtures:

- **`db_session`**: Fresh database session for each test
- **`client`**: FastAPI test client with database override
- **`sample_*_data`**: Pre-configured sample data for testing

### Database
Tests use an in-memory SQLite database for fast execution:
- Each test gets a fresh database session
- Tables are created and dropped for each test
- No data persistence between tests

### Mocking
Tests use mocking for external dependencies:
- Planning Center API calls are mocked
- HTTP requests are intercepted
- Async operations are properly handled

## Test Coverage

The test suite aims for comprehensive coverage of:
- ✅ **Models**: All SQLAlchemy models and relationships
- ✅ **Schemas**: All Pydantic schemas and validation
- ✅ **Services**: All service layer methods and business logic
- ✅ **Endpoints**: All API endpoints and error handling
- ✅ **Integration**: End-to-end API workflows
- ✅ **Async Operations**: Planning Center sync operations
- ✅ **Error Handling**: Exception handling and edge cases

## Test Data

### Sample Data Fixtures
Tests use consistent sample data through fixtures:
- **People**: Church member data with Planning Center IDs
- **Courses**: Course/event data with Planning Center integration
- **Campus**: Church campus information
- **Roles**: User roles and permissions
- **Content**: Course content and materials
- **Enrollments**: Enrollment and progress data

### Test Scenarios
Tests cover various scenarios:
- **Happy Path**: Normal operation flows
- **Edge Cases**: Boundary conditions and limits
- **Error Cases**: Invalid data and error handling
- **Relationships**: Model relationships and constraints
- **Async Operations**: Background task management

## Best Practices

### Test Organization
- Each test class focuses on a specific component
- Test methods are descriptive and focused
- Tests are independent and can run in any order
- Setup and teardown are handled by fixtures

### Assertions
- Tests use specific assertions for better error messages
- Both positive and negative test cases are included
- Edge cases and error conditions are tested
- Data validation is thoroughly tested

### Performance
- Tests use in-memory database for speed
- Mocking reduces external dependencies
- Parallel test execution where possible
- Minimal test data for efficiency

## Continuous Integration

### GitHub Actions
Tests are configured to run in CI/CD:
- All tests must pass before deployment
- Coverage reports are generated
- Test results are published
- Failed tests block deployment

### Quality Gates
- Minimum 80% code coverage required
- All tests must pass
- No critical security vulnerabilities
- Code quality checks (linting, formatting)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure test database is properly configured
   - Check that all models are imported
   - Verify database migrations are up to date

2. **Import Errors**
   - Check that all dependencies are installed
   - Verify Python path includes the app directory
   - Ensure all modules are properly imported

3. **Async Test Issues**
   - Use `pytest-asyncio` for async tests
   - Properly handle async fixtures
   - Mock async operations correctly

4. **Mock Issues**
   - Ensure mocks are properly configured
   - Check mock return values
   - Verify mock call expectations

### Debug Mode
Run tests with debug output:
```bash
pytest tests/ -v -s --tb=long
```

### Coverage Reports
View detailed coverage reports:
```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Use descriptive test names
3. Include both positive and negative cases
4. Add appropriate fixtures for test data
5. Update this documentation if needed
6. Ensure tests pass in CI/CD

## Test Metrics

Current test coverage targets:
- **Models**: 100% coverage
- **Schemas**: 100% coverage  
- **Services**: 95% coverage
- **Endpoints**: 90% coverage
- **Overall**: 90% coverage

Run coverage report to see current metrics:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```
