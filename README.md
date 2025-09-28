# Church Course Tracker

A comprehensive learning management system designed specifically for churches to track course enrollments, monitor member progress, and generate detailed reports on educational content.

## 🎯 Overview

The Church Course Tracker is a web-based application that enables church staff to efficiently manage educational courses, track member progress, and generate insights about church educational programs. The system integrates with Planning Center's church management platform to provide seamless data synchronization.

## ✨ Features

### Core Functionality
- **Course Management**: Create, edit, and manage church courses
- **Enrollment Tracking**: Enroll members in courses and track enrollment status
- **Progress Monitoring**: Track individual member progress through course modules
- **Reporting & Analytics**: Generate comprehensive reports on enrollment and completion rates
- **Planning Center Integration**: Sync member data with Planning Center
- **User Management**: Role-based access control for church staff

### Key Benefits
- Streamlined course enrollment and progress tracking
- Real-time reporting and analytics
- Integration with existing church management systems
- User-friendly interface for church staff
- Simplified learning management tailored for church environments

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Angular 17+ with TypeScript
- **Backend**: Python FastAPI
- **Database**: H2 Database (in-memory with file persistence)
- **Integration**: REST API with Planning Center
- **Deployment**: Docker containers

### Project Structure
```
church-course-tracker/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic services
│   ├── migrations/         # Database migrations
│   └── tests/             # Backend tests
├── frontend/               # Angular frontend
│   └── church-course-tracker/
│       ├── src/
│       │   ├── app/
│       │   │   ├── components/  # Angular components
│       │   │   ├── services/    # Angular services
│       │   │   └── models/      # TypeScript interfaces
│       │   └── environments/    # Environment configurations
│       └── dist/               # Built application
├── docker/                 # Docker configuration
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose (optional)

### Installation

#### Option 1: Docker (Recommended)
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd church-course-tracker
   ```

2. Start the development environment:
   ```bash
   docker-compose -f docker/docker-compose.dev.yml up --build
   ```

3. Access the application:
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. Log in with default admin credentials:
   - Username: `Admin`
   - Email: `course.tracker.admin@eastgate.church`
   - Password: `Matthew778*`

#### Option 2: Local Development

**Backend Setup:**
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Create the default admin user:
   ```bash
   python create_default_admin.py
   ```

7. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

**Frontend Setup:**
1. Navigate to the frontend directory:
   ```bash
   cd frontend/church-course-tracker
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- Development: http://localhost:8000/docs
- Production: https://your-domain.com/docs

### Key Endpoints
- `GET /api/v1/courses` - List all courses
- `POST /api/v1/courses` - Create a new course
- `GET /api/v1/enrollments` - List enrollments
- `POST /api/v1/enrollments` - Enroll member in course
- `GET /api/v1/progress/{member_id}` - Get member progress
- `GET /api/v1/reports/enrollment` - Generate enrollment report

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
APP_NAME="Church Course Tracker"
ENVIRONMENT="development"
SECRET_KEY="your-secret-key"
DATABASE_URL="h2://./data/church_course_tracker.db"
PLANNING_CENTER_API_URL="https://api.planningcenteronline.com"
PLANNING_CENTER_APP_ID="your-app-id"
PLANNING_CENTER_SECRET="your-secret"
```

**Frontend (environment.ts):**
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Church Course Tracker'
};
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend/church-course-tracker
npm test
```

### End-to-End Tests
```bash
cd frontend/church-course-tracker
npm run e2e
```

## 📦 Deployment

### Production Deployment
1. Build the production images:
   ```bash
   docker-compose -f docker/docker-compose.yml --profile production build
   ```

2. Deploy with production profile:
   ```bash
   docker-compose -f docker/docker-compose.yml --profile production up -d
   ```

### Environment-Specific Configurations
- Update `environment.prod.ts` with production API URL
- Configure SSL certificates in `docker/ssl/`
- Set production environment variables

## 🔐 Security

- JWT-based authentication
- Role-based access control (Admin, Staff, Viewer)
- HTTPS enforcement in production
- Input validation and sanitization
- SQL injection prevention through ORM

## 📊 Planning Center Integration

The system integrates with Planning Center to:
- Sync member data automatically
- Retrieve church member information
- Maintain data consistency between systems

### Setup
1. Create a Planning Center application
2. Configure OAuth credentials
3. Set up webhook endpoints (optional)
4. Configure sync frequency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📝 Development Guidelines

### Code Style
- **Backend**: Follow PEP 8, use Black for formatting
- **Frontend**: Follow Angular style guide, use Prettier for formatting
- **Commits**: Use conventional commit messages

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.11+ required)
- Verify all dependencies are installed
- Check database connection settings

**Frontend build fails:**
- Ensure Node.js 18+ is installed
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall

**Database connection issues:**
- Verify H2 database file permissions
- Check database URL configuration
- Ensure data directory exists

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API documentation at `/docs` endpoint

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Project structure setup
- [x] Basic authentication
- [x] Core database models
- [x] Planning Center integration setup

### Phase 2: Core Features (In Progress)
- [ ] Course management interface
- [ ] Enrollment system
- [ ] Progress tracking
- [ ] Basic reporting

### Phase 3: Enhanced Features
- [ ] Advanced reporting and analytics
- [ ] Bulk operations
- [ ] Email notifications
- [ ] Mobile responsiveness improvements

### Phase 4: Advanced Features
- [ ] Real-time updates
- [ ] Advanced user permissions
- [ ] API rate limiting
- [ ] Performance optimizations

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Next Review**: February 2024
