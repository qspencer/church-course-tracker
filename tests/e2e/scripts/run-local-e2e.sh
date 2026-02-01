#!/bin/bash
# Run E2E tests against local development environment
# This script starts the backend and frontend if needed, then runs tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$E2E_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Local E2E Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env.e2e exists
if [ ! -f "$E2E_DIR/.env.e2e" ]; then
    echo -e "${YELLOW}Setting up test users...${NC}"
    python3 "$SCRIPT_DIR/setup-test-users.py"
fi

# Load .env.e2e
source "$E2E_DIR/.env.e2e" 2>/dev/null || true

# Check if backend is running
BACKEND_RUNNING=false
if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}⚠ Backend is not running${NC}"
fi

# Check if frontend is running
FRONTEND_RUNNING=false
if curl -s "http://localhost:4200" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
    FRONTEND_RUNNING=true
else
    echo -e "${YELLOW}⚠ Frontend is not running${NC}"
fi

# Start services if not running
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

if [ "$BACKEND_RUNNING" = false ]; then
    echo -e "${GREEN}Starting backend...${NC}"
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate 2>/dev/null || true

    # Copy dev environment if .env doesn't exist
    if [ ! -f .env ]; then
        cp .env.development .env 2>/dev/null || true
    fi

    uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    # Wait for backend to be ready
    echo -n "  Waiting for backend"
    for i in {1..30}; do
        if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
            echo -e " ${GREEN}ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e " ${RED}failed${NC}"
        echo "Backend failed to start. Check logs above."
        exit 1
    fi
fi

if [ "$FRONTEND_RUNNING" = false ]; then
    echo -e "${GREEN}Starting frontend...${NC}"
    cd "$PROJECT_ROOT/frontend/church-course-tracker"
    ng serve --host 0.0.0.0 &
    FRONTEND_PID=$!

    # Wait for frontend to be ready
    echo -n "  Waiting for frontend"
    for i in {1..60}; do
        if curl -s "http://localhost:4200" > /dev/null 2>&1; then
            echo -e " ${GREEN}ready${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done

    if ! curl -s "http://localhost:4200" > /dev/null 2>&1; then
        echo -e " ${RED}failed${NC}"
        echo "Frontend failed to start. Check logs above."
        exit 1
    fi
fi

# Run e2e tests
echo ""
echo -e "${GREEN}Running E2E tests...${NC}"
echo ""

cd "$E2E_DIR"

# Set environment for local testing
export APP_BASE_URL="http://localhost:4200"
export API_BASE_URL="http://localhost:8000"
export E2E_SKIP_DATA_LOAD=true
export E2E_SKIP_DATA_CLEANUP=true

# Run tests
npx playwright test "$@"

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
    echo -e "${RED}========================================${NC}"
fi

exit $TEST_EXIT_CODE
