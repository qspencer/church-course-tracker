# Development Guide

This document provides detailed information for developers working on the Church Course Tracker project.

## 🏗️ Development Environment Setup

### Prerequisites
- **Node.js**: Version 18 or higher
- **Python**: Version 3.11 or higher
- **Docker**: Latest version (optional but recommended)
- **Git**: Latest version

### IDE Recommendations
- **VS Code** with extensions:
  - Python
  - Angular Language Service
  - Docker
  - GitLens
  - Prettier
  - ESLint

## 🔧 Backend Development

### Project Structure
```
backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Core configuration
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   └── services/             # Business logic
├── migrations/               # Database migrations
├── tests/                    # Test files
└── requirements.txt          # Python dependencies
```

### Key Components

#### Models (SQLAlchemy)
- `User`: Church staff members
- `Member`: Church members from Planning Center
- `Course`: Course definitions
- `Enrollment`: Member-course relationships
- `Progress`: Course completion tracking

#### Services
- `CourseService`: Course management logic
- `EnrollmentService`: Enrollment operations
- `ProgressService`: Progress tracking
- `ReportService`: Report generation
- `SyncService`: Planning Center integration

#### API Endpoints
- RESTful API design
- Versioned endpoints (`/api/v1/`)
- Comprehensive error handling
- Request/response validation

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/
isort app/

# Lint code
flake8 app/

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Database Development

#### H2 Database Setup
The project uses H2 database for development and testing:

```python
# Database URL format
DATABASE_URL = "h2://./data/church_course_tracker.db"
```

#### Migration Workflow
1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration in `migrations/versions/`
4. Apply migration: `alembic upgrade head`

### Testing Strategy

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Use pytest fixtures for test data

#### Integration Tests
- Test API endpoints
- Test database operations
- Test service layer interactions

#### Test Structure
```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── fixtures/                # Test data fixtures
└── conftest.py             # Pytest configuration
```

## 🎨 Frontend Development

### Project Structure
```
frontend/church-course-tracker/
├── src/
│   ├── app/
│   │   ├── components/      # Feature components
│   │   ├── services/        # Angular services
│   │   ├── models/          # TypeScript interfaces
│   │   ├── guards/          # Route guards
│   │   └── interceptors/    # HTTP interceptors
│   ├── assets/              # Static assets
│   └── environments/        # Environment configs
├── e2e/                     # End-to-end tests
└── docs/                    # Frontend documentation
```

### Key Components

#### Services
- `AuthService`: Authentication and user management
- `CourseService`: Course operations
- `EnrollmentService`: Enrollment management
- `ProgressService`: Progress tracking
- `ReportService`: Report generation

#### Components
- `DashboardComponent`: Main dashboard
- `CoursesComponent`: Course management
- `EnrollmentsComponent`: Enrollment interface
- `ProgressComponent`: Progress tracking
- `ReportsComponent`: Report generation

### Development Commands

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run e2e tests
npm run e2e

# Lint code
npm run lint

# Format code
npm run format
```

### Angular Best Practices

#### Component Design
- Use OnPush change detection strategy
- Implement proper lifecycle hooks
- Use reactive forms for user input
- Implement proper error handling

#### Service Design
- Use dependency injection
- Implement proper error handling
- Use observables for async operations
- Cache data when appropriate

#### State Management
- Use Angular services for simple state
- Consider NgRx for complex state management
- Implement proper loading states

## 🔄 API Integration

### HTTP Client Configuration
```typescript
// Base API configuration
const API_BASE_URL = environment.apiUrl;

// HTTP interceptors for:
// - Authentication headers
// - Error handling
// - Loading indicators
```

### Error Handling
```typescript
// Global error handling
@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle different error types
        return throwError(error);
      })
    );
  }
}
```

## 🧪 Testing

### Backend Testing

#### Test Configuration
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --disable-warnings
```

#### Test Examples
```python
def test_create_course(client, db_session):
    """Test course creation"""
    course_data = {
        "name": "Test Course",
        "description": "Test Description"
    }
    response = client.post("/api/v1/courses/", json=course_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Course"
```

### Frontend Testing

#### Unit Tests
```typescript
describe('CourseService', () => {
  let service: CourseService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [CourseService]
    });
    service = TestBed.inject(CourseService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should get courses', () => {
    const mockCourses = [{ id: 1, name: 'Test Course' }];
    
    service.getCourses().subscribe(courses => {
      expect(courses).toEqual(mockCourses);
    });

    const req = httpMock.expectOne('/api/v1/courses');
    expect(req.request.method).toBe('GET');
    req.flush(mockCourses);
  });
});
```

## 🐳 Docker Development

### Development Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.dev
    volumes:
      - ../backend:/app
    command: uvicorn main:app --reload
```

### Useful Docker Commands
```bash
# Build and start development environment
docker-compose -f docker/docker-compose.dev.yml up --build

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f

# Execute commands in container
docker-compose -f docker/docker-compose.dev.yml exec backend bash

# Stop services
docker-compose -f docker/docker-compose.dev.yml down
```

## 🔍 Debugging

### Backend Debugging
```python
# Use Python debugger
import pdb; pdb.set_trace()

# Use logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging
```typescript
// Use browser dev tools
console.log('Debug message');

// Use Angular DevTools
// Install: npm install -g @angular/devkit

// Use VS Code debugger
// Configure launch.json for debugging
```

## 📊 Performance Optimization

### Backend Optimization
- Use database indexes for frequently queried fields
- Implement pagination for large datasets
- Use connection pooling
- Cache frequently accessed data

### Frontend Optimization
- Use OnPush change detection
- Implement lazy loading for routes
- Use trackBy functions in *ngFor
- Optimize bundle size with tree shaking

## 🔐 Security Considerations

### Backend Security
- Validate all input data
- Use parameterized queries
- Implement proper authentication
- Use HTTPS in production
- Sanitize user input

### Frontend Security
- Validate forms on both client and server
- Use HTTPS for all API calls
- Implement proper error handling
- Sanitize user input before display

## 📝 Code Review Guidelines

### Backend Code Review
- [ ] Code follows PEP 8 style guide
- [ ] Functions have proper docstrings
- [ ] Error handling is implemented
- [ ] Tests are included
- [ ] Database queries are optimized
- [ ] Security considerations are addressed

### Frontend Code Review
- [ ] Code follows Angular style guide
- [ ] Components are properly structured
- [ ] Error handling is implemented
- [ ] Tests are included
- [ ] Performance considerations are addressed
- [ ] Accessibility is considered

## 🚀 Deployment

### Development Deployment
```bash
# Build and deploy to development environment
docker-compose -f docker/docker-compose.dev.yml up --build
```

### Production Deployment
```bash
# Build production images
docker-compose -f docker/docker-compose.yml --profile production build

# Deploy to production
docker-compose -f docker/docker-compose.yml --profile production up -d
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Angular Documentation](https://angular.io/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Angular Material Documentation](https://material.angular.io/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Angular DevTools](https://angular.io/guide/devtools) - Angular debugging
- [SQLAlchemy Studio](https://github.com/coleifer/sqlalchemy-studio) - Database management

---

**Last Updated**: January 2024  
**Version**: 1.0.0
