# CloudFront Cache Configuration Fix

## Problem

Users had to clear browser cache every time frontend code was updated, which is not normal behavior for frontend development.

## Root Cause

CloudFront was using default cache settings:
- **No TTL specified** → Default 24-hour cache
- **No cache-control headers** from S3 → CloudFront couldn't differentiate file types
- **index.html cached** → Old HTML served cached JavaScript files
- **No distinction** between index.html and hashed assets

## Solution

### 1. CloudFront Cache Behaviors

Configured three cache behaviors:

1. **index.html**: No cache (always fetch fresh)
   - `min_ttl = 0`, `default_ttl = 0`, `max_ttl = 0`
   - Ensures users always get the latest HTML with updated script references

2. **Hashed JavaScript files (*.js)**: Long-term cache (1 year)
   - `min_ttl = 31536000`, `default_ttl = 31536000`, `max_ttl = 31536000`
   - Safe because hash changes when content changes (Angular content-based hashing)

3. **Hashed CSS files (*.css)**: Long-term cache (1 year)
   - Same as JavaScript files
   - Hash changes when content changes

4. **Default behavior**: 1 day default, 1 year max
   - For other files (images, fonts, etc.)

### 2. S3 Cache-Control Headers

Deployment script now sets proper headers:

- **index.html**: `Cache-Control: no-cache, no-store, must-revalidate`
- **Hashed assets**: `Cache-Control: public, max-age=31536000, immutable`

### 3. How It Works

1. **index.html** is never cached
   - User visits site → CloudFront fetches fresh index.html
   - index.html contains references to hashed JS/CSS files
   - Example: `<script src="main.abc123.js"></script>`

2. **Hashed files** are cached long-term
   - When content changes → Angular generates new hash
   - Example: `main.abc123.js` → `main.xyz789.js`
   - Browser requests `main.xyz789.js` (new file, not in cache)
   - Old `main.abc123.js` can remain cached (no longer referenced)

3. **No browser cache clear needed**
   - Fresh index.html always references latest hashed files
   - Browser automatically fetches new files when hash changes

## Changes Made

### Infrastructure (`infrastructure/main.tf`)

1. **Added S3 bucket versioning and public access block**
2. **Configured CloudFront cache behaviors**:
   - Default: 1 day default, 1 year max
   - index.html: No cache
   - *.js: 1 year cache
   - *.css: 1 year cache

### Deployment Script (`scripts/deploy-frontend.sh`)

New script that:
- Sets `no-cache` on index.html
- Sets `max-age=31536000, immutable` on hashed assets
- Automatically invalidates CloudFront after deployment

## Usage

### Deploy Frontend

```bash
./scripts/deploy-frontend.sh
```

This script:
1. Builds frontend (if needed)
2. Deploys index.html with no-cache
3. Deploys assets with long-term cache
4. Invalidates CloudFront

### Manual Deployment

```bash
# Deploy index.html (no cache)
aws s3 cp dist/index.html s3://bucket/ \
    --cache-control "no-cache, no-store, must-revalidate"

# Deploy assets (long cache)
aws s3 sync dist/ s3://bucket/ \
    --exclude "index.html" \
    --cache-control "public, max-age=31536000, immutable"
```

## Benefits

✅ **No browser cache clear needed**
- Users always get fresh index.html
- New hashed files automatically fetched

✅ **Optimal caching**
- Hashed files cached long-term (better performance)
- index.html never cached (always fresh)

✅ **Standard practice**
- Follows Angular best practices
- Matches industry-standard SPA deployment patterns

## Testing

After deployment:

1. **Visit site** → Should work immediately
2. **Check Network tab** → index.html should have `no-cache` header
3. **Check JS files** → Should have `max-age=31536000` header
4. **Deploy new code** → Should work without browser cache clear

## Troubleshooting

### Still seeing old code?

1. **Check CloudFront invalidation status**:
   ```bash
   aws cloudfront get-invalidation \
       --distribution-id <ID> \
       --id <INVALIDATION_ID>
   ```

2. **Check S3 cache headers**:
   ```bash
   aws s3api head-object \
       --bucket <BUCKET> \
       --key index.html
   ```

3. **Verify CloudFront cache behavior**:
   - Check that index.html has `min_ttl = 0`
   - Check that *.js has `min_ttl = 31536000`

### Browser still caching?

- This should not happen with proper configuration
- If it does, check:
  1. CloudFront distribution is updated
  2. S3 objects have correct headers
  3. Browser is not using service worker

## Next Steps

1. **Apply Terraform changes**:
   ```bash
   cd infrastructure
   terraform plan
   terraform apply
   ```

2. **Redeploy frontend**:
   ```bash
   ./scripts/deploy-frontend.sh
   ```

3. **Test**:
   - Visit site
   - Deploy a small change
   - Verify it works without cache clear

## Notes

- **Angular hash-based filenames** are critical for this to work
- **index.html must never be cached** for this pattern to work
- **CloudFront invalidation** is still run after deployment (for immediate effect)
- **Long-term** invalidation won't be needed once this is fully deployed


