#!/bin/bash

# Script to increment application version
# This script reads the current version from environment.prod.ts, increments it, and updates the file

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_PROD_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.prod.ts"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Send status messages to stderr so they don't interfere with version capture
echo -e "${GREEN}📌 Incrementing application version...${NC}" >&2

# Extract current version from environment.prod.ts
if [ -f "$ENV_PROD_FILE" ]; then
    # Extract version using grep and sed
    CURRENT_VERSION=$(grep -oP "version:\s*['\"]\K[^'\"]*" "$ENV_PROD_FILE" || echo "0.00")
    
    if [ -z "$CURRENT_VERSION" ] || [ "$CURRENT_VERSION" = "0.00" ]; then
        CURRENT_VERSION="0.02"
    fi
    
    echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}" >&2
    
    # Increment version (0.02 -> 0.03, etc.)
    # Convert to integer (multiply by 100), increment, then divide by 100
    VERSION_INT=$(echo "$CURRENT_VERSION * 100" | bc | cut -d. -f1)
    NEW_VERSION_INT=$((VERSION_INT + 1))
    NEW_VERSION=$(printf "%.2f" $(echo "scale=2; $NEW_VERSION_INT / 100" | bc))
    
    # Format to 2 decimal places (0.03 instead of 0.3)
    NEW_VERSION=$(printf "%.2f" "$NEW_VERSION")
    
    echo -e "${GREEN}New version: $NEW_VERSION${NC}" >&2
    
    # Update environment.prod.ts
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version: '.*'/version: '$NEW_VERSION'/g" "$ENV_PROD_FILE"
    else
        # Linux
        sed -i "s/version: '.*'/version: '$NEW_VERSION'/g" "$ENV_PROD_FILE"
    fi
    
    echo -e "${GREEN}✅ Version updated to $NEW_VERSION in environment.prod.ts${NC}" >&2
    
    # Return ONLY the version number to stdout (for capture by calling scripts)
    echo "$NEW_VERSION"
else
    echo -e "${YELLOW}⚠️  environment.prod.ts not found, using default version 0.03${NC}" >&2
    echo "0.03"
fi

