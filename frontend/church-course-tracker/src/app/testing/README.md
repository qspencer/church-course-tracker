# Testing Guide for Church Course Tracker

This document outlines the testing strategy and structure for the Church Course Tracker Angular application.

## Test Structure

### Unit Tests
All components, services, guards, and interceptors have comprehensive unit tests:

#### Components
- `auth.component.spec.ts` - Authentication component tests
- `dashboard.component.spec.ts` - Dashboard with chart integration tests
- `courses.component.spec.ts` - Course management component tests
- `course-dialog.component.spec.ts` - Course dialog tests
- `members.component.spec.ts` - Member management component tests
- `member-dialog.component.spec.ts` - Member dialog tests

#### Services
- `auth.service.spec.ts` - Authentication service tests
- `course.service.spec.ts` - Course API service tests
- `enrollment.service.spec.ts` - Enrollment API service tests
- `progress.service.spec.ts` - Progress tracking service tests
- `member.service.spec.ts` - Member API service tests
- `report.service.spec.ts` - Reporting service tests

#### Guards & Interceptors
- `auth.guard.spec.ts` - Route protection tests
- `auth.interceptor.spec.ts` - JWT token handling tests
- `error.interceptor.spec.ts` - Error handling and user feedback tests

## Test Coverage Goals

- **Statements**: 80%+
- **Branches**: 70%+
- **Functions**: 80%+
- **Lines**: 80%+

## Running Tests

### Development Testing
```bash
npm run test
```
Runs tests in watch mode with Chrome browser for development.

### Headless Testing (CI/CD)
```bash
npm run test:headless
```
Runs tests once in headless Chrome with coverage report.

### Coverage Report
```bash
npm run test:coverage
```
Generates detailed coverage report in `coverage/` directory.

## Test Patterns

### Component Testing
```typescript
describe('ComponentName', () => {
  let component: ComponentName;
  let fixture: ComponentFixture<ComponentName>;
  let serviceSpy: jasmine.SpyObj<ServiceName>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('ServiceName', ['method1', 'method2']);
    
    await TestBed.configureTestingModule({
      declarations: [ComponentName],
      imports: [RequiredModules],
      providers: [{ provide: ServiceName, useValue: spy }]
    }).compileComponents();
  });

  it('should test behavior', () => {
    // Arrange, Act, Assert
  });
});
```

### Service Testing
```typescript
describe('ServiceName', () => {
  let service: ServiceName;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ServiceName]
    });
  });

  it('should make HTTP request', () => {
    service.getData().subscribe(data => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne('/api/data');
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });
});
```

## Mock Strategies

### HTTP Mocking
Uses `HttpClientTestingModule` and `HttpTestingController` for API testing.

### Component Dependencies
Uses Jasmine spies for service dependencies:
```typescript
const serviceSpy = jasmine.createSpyObj('ServiceName', ['method']);
serviceSpy.method.and.returnValue(of(mockData));
```

### Angular Material
Includes proper imports for Material components in test modules.

### Chart.js
Mocks Chart.js in test setup to avoid rendering issues.

## Test Data

Mock data is defined inline in test files for:
- User objects
- Course objects  
- Enrollment objects
- Progress objects
- Report data

## Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **One Assertion Per Test**: Each test should verify one behavior
3. **Descriptive Names**: Test names should clearly describe what is being tested
4. **Mock External Dependencies**: Use spies and mocks for all external dependencies
5. **Test Error Cases**: Include tests for error scenarios
6. **Clean Setup/Teardown**: Use `beforeEach` and `afterEach` appropriately

## Continuous Integration

Tests run automatically on:
- Pull requests
- Main branch commits
- Release builds

The CI pipeline fails if:
- Any test fails
- Coverage drops below thresholds
- Linting errors exist

## Debugging Tests

### Common Issues
1. **Material Module Imports**: Ensure all required Material modules are imported
2. **Async Operations**: Use `fakeAsync` and `tick()` for timing-dependent tests
3. **DOM Testing**: Use `fixture.detectChanges()` after component changes
4. **HTTP Mocking**: Always call `httpMock.verify()` in `afterEach`

### Debug Commands
```bash
# Run specific test file
ng test --include="**/auth.service.spec.ts"

# Run tests with debugging
ng test --source-map --watch
```

This comprehensive test suite ensures the reliability and maintainability of the Church Course Tracker application.
