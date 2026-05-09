#!/bin/bash

# Increment the application version.
#
# Canonical source: frontend/church-course-tracker/version.txt
# Mirrors that value into:
#   - frontend/church-course-tracker/src/environments/environment.ts
#   - frontend/church-course-tracker/src/environments/environment.prod.ts
#
# Status messages go to stderr; the new version (and only the new version)
# goes to stdout so callers can capture it (e.g. GitHub Actions outputs).

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/frontend/church-course-tracker/version.txt"
ENV_BASE_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.ts"
ENV_PROD_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.prod.ts"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📌 Incrementing application version...${NC}" >&2

# 1. Read current version from version.txt (canonical). Fall back to 0.00.
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(tr -d '[:space:]' < "$VERSION_FILE")
else
    CURRENT_VERSION="0.00"
fi

if [ -z "$CURRENT_VERSION" ]; then
    CURRENT_VERSION="0.00"
fi

echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}" >&2

# 2. Increment by 0.01. Use awk so we don't need bc.
NEW_VERSION=$(awk "BEGIN { printf \"%.2f\", $CURRENT_VERSION + 0.01 }")
echo -e "${GREEN}New version: $NEW_VERSION${NC}" >&2

# 3. Write to all three sources atomically.
echo "$NEW_VERSION" > "$VERSION_FILE"

if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE=(-i '')
else
    SED_INPLACE=(-i)
fi

for f in "$ENV_BASE_FILE" "$ENV_PROD_FILE"; do
    if [ -f "$f" ]; then
        # Replace either an existing version literal or the VERSION_PLACEHOLDER
        # token used by deploy-frontend.sh.
        sed "${SED_INPLACE[@]}" -E "s/version: *['\"][^'\"]*['\"]/version: '$NEW_VERSION'/g" "$f"
        sed "${SED_INPLACE[@]}" "s/VERSION_PLACEHOLDER/$NEW_VERSION/g" "$f"
    fi
done

echo -e "${GREEN}✅ Version $NEW_VERSION written to version.txt, environment.ts, environment.prod.ts${NC}" >&2

# 4. Emit ONLY the version number to stdout for capture by callers.
echo "$NEW_VERSION"
