#!/bin/bash
# Deployment script for documentation site
# Deploys to S3 with churchcoursetracker/ path prefix

set -e

# Configuration - these should be set as environment variables or in CI/CD
S3_BUCKET="${DOCS_S3_BUCKET:-docs.quentinspencer.com}"
CLOUDFRONT_DIST_ID="${DOCS_CLOUDFRONT_DIST_ID}"
DOCS_PATH="churchcoursetracker"

# Validate required environment variables
if [ -z "$CLOUDFRONT_DIST_ID" ]; then
    echo "⚠️  WARNING: CLOUDFRONT_DIST_ID not set. CloudFront cache invalidation will be skipped."
    echo "   Set DOCS_CLOUDFRONT_DIST_ID environment variable to enable cache invalidation."
fi

echo "🚀 Deploying Church Course Tracker documentation..."
echo "   S3 Bucket: $S3_BUCKET"
echo "   Path: /$DOCS_PATH/"
echo ""

# Navigate to docs-site directory
cd "$(dirname "$0")/.."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Build the site
echo "📦 Building documentation site..."
mkdocs build

if [ ! -d "site" ]; then
    echo "❌ Build failed - site directory not found"
    exit 1
fi

echo "✅ Build complete"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI to deploy."
    exit 1
fi

# Deploy to S3
echo "📤 Uploading to S3..."
aws s3 sync site/ s3://$S3_BUCKET/$DOCS_PATH/ \
    --delete \
    --exclude "*.pyc" \
    --exclude ".git/*" \
    --exclude "venv/*" \
    --cache-control "public, max-age=3600"

if [ $? -ne 0 ]; then
    echo "❌ S3 upload failed"
    exit 1
fi

echo "✅ Upload complete"
echo ""

# Invalidate CloudFront cache if distribution ID is provided
if [ -n "$CLOUDFRONT_DIST_ID" ]; then
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DIST_ID \
        --paths "/$DOCS_PATH/*"
    
    if [ $? -eq 0 ]; then
        echo "✅ CloudFront invalidation initiated"
    else
        echo "⚠️  CloudFront invalidation failed (non-critical)"
    fi
else
    echo "⚠️  CLOUDFRONT_DIST_ID not set - skipping cache invalidation"
fi

echo ""
echo "🎉 Deployment complete!"
echo "   Documentation available at: https://docs.quentinspencer.com/$DOCS_PATH/"


