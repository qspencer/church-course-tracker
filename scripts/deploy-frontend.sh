#!/bin/bash
# Deploy frontend to S3 with proper cache headers
# This ensures CloudFront respects cache settings correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get S3 bucket from Terraform output
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Version file location
VERSION_FILE="$PROJECT_ROOT/frontend/church-course-tracker/version.txt"
ENV_PROD_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.prod.ts"

# Increment version
if [ -f "$VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$VERSION_FILE")
    # Use awk for version increment (works without bc)
    NEW_VERSION=$(awk "BEGIN {printf \"%.2f\", $CURRENT_VERSION + 0.01}")
else
    NEW_VERSION="0.01"
fi

echo -e "${GREEN}📌 Version: ${NEW_VERSION}${NC}"

# Update version file
echo "$NEW_VERSION" > "$VERSION_FILE"

# Replace version placeholder in environment.prod.ts
if [ -f "$ENV_PROD_FILE" ]; then
    # Use sed to replace the placeholder (works on both Linux and macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VERSION_PLACEHOLDER/$NEW_VERSION/g" "$ENV_PROD_FILE"
    else
        # Linux
        sed -i "s/VERSION_PLACEHOLDER/$NEW_VERSION/g" "$ENV_PROD_FILE"
    fi
    echo -e "${GREEN}✅ Updated version in environment.prod.ts${NC}"
fi

cd "$PROJECT_ROOT/infrastructure"

# Get S3 bucket name
S3_BUCKET=$(terraform output -raw s3_static_bucket 2>/dev/null || echo "")
if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}❌ Error: Could not get S3 bucket from Terraform output${NC}"
    echo "Make sure you've run 'terraform apply' in the infrastructure directory"
    exit 1
fi

echo -e "${GREEN}📦 Deploying frontend to S3: ${S3_BUCKET}${NC}"

# Build frontend (always rebuild to ensure version is included)
echo -e "${GREEN}🔨 Building frontend with version ${NEW_VERSION}...${NC}"
cd "$PROJECT_ROOT/frontend/church-course-tracker"
npm run build -- --configuration=production --base-href=/churchcoursetracker/

FRONTEND_DIST="$PROJECT_ROOT/frontend/church-course-tracker/dist/church-course-tracker"

# Deploy index.html with no-cache (always fetch fresh)
echo -e "${GREEN}📄 Deploying index.html (no-cache)...${NC}"
aws s3 cp "$FRONTEND_DIST/index.html" "s3://$S3_BUCKET/churchcoursetracker/index.html" \
    --cache-control "no-cache, no-store, must-revalidate" \
    --content-type "text/html" \
    --metadata-directive REPLACE

# Deploy all other files (hashed JS/CSS) with long-term cache
# Hashed files can be cached indefinitely since the hash changes when content changes
echo -e "${GREEN}📦 Deploying assets (long-term cache)...${NC}"
aws s3 sync "$FRONTEND_DIST/" "s3://$S3_BUCKET/churchcoursetracker/" \
    --exclude "index.html" \
    --cache-control "public, max-age=31536000, immutable" \
    --delete

# Get CloudFront distribution ID
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, '$S3_BUCKET')].Id" \
    --output text 2>/dev/null || echo "")

if [ -n "$CLOUDFRONT_ID" ]; then
    echo -e "${GREEN}🔄 Invalidating CloudFront cache...${NC}"
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_ID" \
        --paths "/churchcoursetracker/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    echo -e "${GREEN}✅ CloudFront invalidation created: ${INVALIDATION_ID}${NC}"
    echo -e "${YELLOW}⏳ Cache invalidation typically takes 5-15 minutes${NC}"
else
    echo -e "${YELLOW}⚠️  Could not find CloudFront distribution. Skipping invalidation.${NC}"
fi

echo -e "${GREEN}✅ Frontend deployment complete!${NC}"
echo ""
echo "Cache configuration:"
echo "  - index.html: no-cache (always fresh)"
echo "  - *.js, *.css: 1 year cache (immutable, hash-based)"
echo ""
echo "Users will get fresh index.html on each visit, which references"
echo "the latest hashed JS/CSS files. No browser cache clear needed!"


