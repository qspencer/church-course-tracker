#!/bin/bash

# Angular 18 Upgrade Script
# This script automates the upgrade process from Angular 17 to Angular 18

set -e  # Exit on error

FRONTEND_DIR="frontend/church-course-tracker"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Angular 18 Upgrade Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# Check if we're in the right directory
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# Step 1: Check Node.js version
print_info "Checking Node.js version..."
NODE_VERSION=$(node --version | cut -d'v' -f2)
REQUIRED_NODE="18.20.0"

if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE" ]; then
    print_warning "Node.js version $NODE_VERSION is less than required $REQUIRED_NODE"
    print_info "Please update Node.js to version 18.20.0 or higher"
    print_info "You can use nvm: nvm install 18.20.0 && nvm use 18.20.0"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "Node.js version $NODE_VERSION meets requirements"
fi

# Step 2: Check npm version
print_info "Checking npm version..."
NPM_VERSION=$(npm --version)
REQUIRED_NPM="9.0.0"

if [ "$(printf '%s\n' "$REQUIRED_NPM" "$NPM_VERSION" | sort -V | head -n1)" != "$REQUIRED_NPM" ]; then
    print_warning "npm version $NPM_VERSION is less than required $REQUIRED_NPM"
    print_info "Updating npm..."
    npm install -g npm@latest
    print_success "npm updated"
else
    print_success "npm version $NPM_VERSION meets requirements"
fi

# Step 3: Create backup
print_info "Creating backup..."
cd "$PROJECT_ROOT"
if [ -d ".git" ]; then
    BACKUP_BRANCH="backup-before-angular-18-upgrade-$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$BACKUP_BRANCH" 2>/dev/null || print_warning "Could not create backup branch (may already exist)"
    git checkout - 2>/dev/null || true
    print_success "Backup branch created: $BACKUP_BRANCH"
    git tag "v1.0.0-angular-17-$(date +%Y%m%d)" 2>/dev/null || print_warning "Tag may already exist"
    print_success "Tag created for rollback"
else
    print_warning "Not a git repository, skipping backup"
fi

cd "$FRONTEND_DIR"

# Step 4: Fix security vulnerabilities
print_info "Fixing security vulnerabilities..."
npm audit fix --legacy-peer-deps || print_warning "Some vulnerabilities may remain"
print_success "Security audit completed"

# Step 5: Update Angular CLI globally (optional, but recommended)
print_info "Checking Angular CLI version..."
ANGULAR_CLI_VERSION=$(ng version 2>/dev/null | grep "Angular CLI" | awk '{print $3}' || echo "not installed")

if [ "$ANGULAR_CLI_VERSION" = "not installed" ] || [[ "$ANGULAR_CLI_VERSION" < "18.0.0" ]]; then
    print_info "Updating Angular CLI globally..."
    npm uninstall -g @angular/cli 2>/dev/null || true
    npm cache clean --force
    npm install -g @angular/cli@18
    print_success "Angular CLI updated to version 18"
else
    print_success "Angular CLI version $ANGULAR_CLI_VERSION is up to date"
fi

# Step 6: Update Angular core packages
print_info "Updating Angular core packages to version 18..."
ng update @angular/core@18 @angular/cli@18 --allow-dirty --force || {
    print_error "Failed to update Angular core packages"
    exit 1
}
print_success "Angular core packages updated"

# Step 7: Update Angular Material
print_info "Updating Angular Material to version 18..."
ng update @angular/material@18 --allow-dirty --force || {
    print_warning "Angular Material update may have issues, continuing..."
}
print_success "Angular Material update attempted"

# Step 8: Update TypeScript
print_info "Updating TypeScript..."
ng update typescript@latest --allow-dirty --force || {
    print_warning "TypeScript update may have issues, continuing..."
}
print_success "TypeScript update attempted"

# Step 9: Update remaining Angular packages
print_info "Updating remaining Angular packages..."
ng update @angular/animations@18 --allow-dirty --force || print_warning "Animations update failed"
ng update @angular/cdk@18 --allow-dirty --force || print_warning "CDK update failed"
ng update @angular/platform-browser@18 --allow-dirty --force || print_warning "Platform browser update failed"
ng update @angular/platform-browser-dynamic@18 --allow-dirty --force || print_warning "Platform browser dynamic update failed"
ng update @angular/router@18 --allow-dirty --force || print_warning "Router update failed"
ng update @angular/forms@18 --allow-dirty --force || print_warning "Forms update failed"
ng update @angular/common@18 --allow-dirty --force || print_warning "Common update failed"
print_success "Remaining Angular packages update attempted"

# Step 10: Clean install
print_info "Performing clean install..."
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
print_success "Dependencies reinstalled"

# Step 11: Build check
print_info "Checking if project builds..."
npm run build 2>&1 | tee /tmp/angular-upgrade-build.log || {
    print_error "Build failed! Check /tmp/angular-upgrade-build.log for details"
    print_info "You may need to fix compilation errors manually"
    exit 1
}
print_success "Project builds successfully"

# Step 12: Run tests
print_info "Running unit tests..."
npm run test:headless 2>&1 | tee /tmp/angular-upgrade-tests.log || {
    print_warning "Some tests may have failed. Check /tmp/angular-upgrade-tests.log"
    print_info "You may need to update tests manually"
}

print_success "Upgrade script completed!"
echo ""
print_info "Next steps:"
echo "  1. Review the build output: /tmp/angular-upgrade-build.log"
echo "  2. Review the test output: /tmp/angular-upgrade-tests.log"
echo "  3. Fix any compilation errors"
echo "  4. Update any failing tests"
echo "  5. Test the application manually"
echo ""
print_info "If you need to rollback:"
echo "  git checkout backup-before-angular-18-upgrade-*"
echo "  or"
echo "  git checkout v1.0.0-angular-17-*"


