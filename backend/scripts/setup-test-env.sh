#!/bin/bash
# Setup script for testing environment

set -e

echo "🧪 Setting up Testing Environment"
echo "================================"

cd "$(dirname "$0")/.."

# Determine which virtual environment to use
if [ -d "venv_new" ]; then
    VENV_PATH="venv_new"
    echo "📦 Using existing venv_new..."
elif [ -d "venv" ]; then
    VENV_PATH="venv"
    echo "📦 Using existing venv..."
else
    VENV_PATH="venv_test"
    echo "📦 Creating new virtual environment: venv_test..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Set up database
echo "🗄️  Setting up test database..."
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
mkdir -p data

# Run migrations
echo "🔄 Running migrations..."
if python -m alembic upgrade head 2>/dev/null; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️  Migrations failed, creating tables directly..."
    python -c "
import sys
sys.path.insert(0, '.')
from app.core.database import Base, engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Tables created directly')
" || echo "⚠️  Table creation also failed - tests will handle this"
fi

# Verify installation
echo ""
echo "✅ Verifying installation..."
echo "   pytest: $(pytest --version 2>/dev/null | head -n1 || echo 'NOT FOUND')"
echo "   alembic: $(python -m alembic --version 2>/dev/null | head -n1 || echo 'NOT FOUND')"
echo "   python: $(python --version)"

# Test simple import
echo ""
echo "✅ Testing imports..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.models.course_instance import CourseInstance, CourseInstanceTeacher
    from app.services.course_instance_service import CourseInstanceService
    from app.api.v1.endpoints.course_instances import router
    print('✅ All imports successful')
except Exception as e:
    print(f'⚠️  Import error: {e}')
    sys.exit(1)
" || exit 1

echo ""
echo "========================================"
echo "✅ Testing environment setup complete!"
echo "========================================"
echo ""
echo "Run tests with:"
echo "  pytest tests/test_course_instances.py -v"
echo ""
echo "Or run all tests:"
echo "  pytest tests/ -v"
echo ""

