#!/bin/bash
# Setup script for running E2E tests locally
# This creates test users and generates the .env.e2e file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
E2E_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$E2E_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  E2E Test Local Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for Python virtual environment
if [ ! -f "$BACKEND_DIR/venv/bin/python" ]; then
    echo -e "${YELLOW}Creating backend virtual environment...${NC}"
    python3 -m venv "$BACKEND_DIR/venv"
fi

# Activate virtual environment and install dependencies
echo -e "${GREEN}Installing backend dependencies...${NC}"
source "$BACKEND_DIR/venv/bin/activate"
pip install -q -r "$BACKEND_DIR/requirements.txt"

# Run the Python setup script
echo -e "${GREEN}Creating test users...${NC}"
python3 "$SCRIPT_DIR/setup-test-users.py"

# Check if .env.e2e was created
if [ -f "$E2E_DIR/.env.e2e" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Test credentials saved to: ${BLUE}$E2E_DIR/.env.e2e${NC}"
    echo ""
    echo -e "${YELLOW}To run E2E tests locally:${NC}"
    echo "  1. Start the backend:  cd backend && ./venv/bin/uvicorn app.main:app --reload"
    echo "  2. Start the frontend: cd frontend/church-course-tracker && ng serve"
    echo "  3. Run tests:          cd tests/e2e && npm test"
    echo ""
    echo -e "${YELLOW}Or run against production:${NC}"
    echo "  cd tests/e2e && npm test"
    echo ""
else
    echo -e "${RED}Error: .env.e2e was not created${NC}"
    exit 1
fi
