# API Gateway Custom Domain Cache Invalidation Instructions

## Problem

Custom domain `https://api.quentinspencer.com` returns 503 due to cached "no healthy instances" state, even though:
- Service Discovery instance is HEALTHY
- Direct API Gateway endpoint works (200 OK)
- Fix is correctly implemented

## Solution: Force Cache Invalidation

### Method 1: Re-create API Base Path Mapping (Most Recommended) ⭐

**Steps (via AWS Console):**

1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway)
2. Navigate to **Custom domain names** in left menu
3. Click on domain: `api.quentinspencer.com`
4. Go to **API mappings** tab
5. Select the API mapping (should show API `tinev5iszf`, Stage `$default`)
6. Click **Delete**
7. **Wait 60 seconds**
8. Click **Create API mapping**
9. Add mapping back with:
   - API: `church-course-tracker-api` (or `tinev5iszf`)
   - Stage: `$default`
   - Path: (leave empty for root path)
10. **Wait 2-5 minutes**
11. Test: `curl https://api.quentinspencer.com/api/v1/health`

**Steps (via Terraform):**

```bash
cd infrastructure

# Get mapping ID
aws apigatewayv2 get-api-mappings \
  --domain-name api.quentinspencer.com \
  --region us-east-1

# Delete mapping (requires IAM permissions)
aws apigatewayv2 delete-api-mapping \
  --domain-name api.quentinspencer.com \
  --api-mapping-id <MAPPING_ID> \
  --region us-east-1

# Wait 60 seconds
sleep 60

# Recreate via Terraform (if mapping is managed by Terraform)
terraform apply -target=aws_apigatewayv2_api_mapping.<resource_name>
```

### Method 2: Redeploy API Stage

**Steps (via AWS Console):**

1. Go to API Gateway Console
2. Select your API: `church-course-tracker-api`
3. Click **Deploy API**
4. Select Stage: `$default`
5. Deployment description: "Force cache invalidation"
6. Click **Deploy**
7. **Wait 2-5 minutes**
8. Test: `curl https://api.quentinspencer.com/api/v1/health`

**Steps (via CLI):**

```bash
API_ID="tinev5iszf"

aws apigatewayv2 create-deployment \
  --api-id "$API_ID" \
  --stage-name "\$default" \
  --description "Force cache invalidation - $(date -u +%Y-%m-%d-%H%M%S)" \
  --region us-east-1
```

### Method 3: Toggle Integration (The "Jiggle")

**Steps (via AWS Console):**

1. Go to API Gateway Console
2. Select your API: `church-course-tracker-api`
3. Go to **Routes**
4. Select a route (e.g., `GET /health`)
5. Change integration to **Mock** integration
6. Click **Save**
7. **Deploy API** to `$default` stage
8. Test custom domain (should return mock 200 OK)
9. Change integration **back** to VPC Link / Service Discovery
10. Click **Save**
11. **Deploy API** again
12. **Wait 2-5 minutes**
13. Test: `curl https://api.quentinspencer.com/api/v1/health`

**Why This Works**: Forces API Gateway to tear down old integration path and build new one, discovering HEALTHY instance in process.

## Current Status

✅ **Fix Implemented**: 
- ECS no longer manages Service Discovery
- Register Lambda sets `AWS_INIT_HEALTH_STATUS='HEALTHY'` at registration
- Instance is HEALTHY

⏳ **Cache Invalidation**: 
- Method 2 (stage redeployment) attempted via CLI
- If still 503, use Method 1 (console) or Method 3 (toggle integration)

## Verification After Cache Invalidation

```bash
# Test custom domain
curl https://api.quentinspencer.com/api/v1/health

# Should return 200 OK with JSON response
# If still 503, try next method
```

## Notes

- Cache invalidation can take 2-5 minutes to propagate
- Instance must remain HEALTHY during this process
- Direct endpoint will continue working regardless
- If all methods fail, may indicate deeper AWS issue - contact support


