# Manual Cache Invalidation - Step by Step

## Current Situation

✅ **Fix is correctly implemented**:
- Service Discovery instance is HEALTHY
- Direct API Gateway endpoint works (200 OK)
- All architecture changes are correct

❌ **Custom domain still returns 503**:
- Cache persists after 5+ hours
- CLI/Terraform methods haven't cleared it
- Manual console action required

## Recommended Fix: Delete and Recreate API Mapping

### Step-by-Step Instructions

1. **Open AWS Console**
   - Go to: https://console.aws.amazon.com/apigateway/home?region=us-east-1
   - Sign in if needed

2. **Navigate to Custom Domain Names**
   - In left sidebar, click: **Custom domain names**

3. **Select Your Domain**
   - Click on: **api.quentinspencer.com**

4. **Go to API Mappings Tab**
   - Click the **API mappings** tab

5. **Delete the Mapping**
   - You should see one mapping:
     - API: `church-course-tracker-api` (or `tinev5iszf`)
     - Stage: `$default`
     - Path: (empty)
   - Click the checkbox next to the mapping
   - Click **Delete**
   - Confirm deletion

6. **Wait 60 Seconds**
   - Important: Wait a full 60 seconds
   - This allows the deletion to propagate

7. **Recreate the Mapping**
   - Click **Create API mapping**
   - Configure:
     - **API**: Select `church-course-tracker-api`
     - **Stage**: Select `$default`
     - **Path**: Leave empty (for root path)
   - Click **Save**

8. **Wait for Propagation**
   - Wait **2-5 minutes** for changes to propagate

9. **Test**
   ```bash
   curl https://api.quentinspencer.com/api/v1/health
   ```
   - Should return 200 OK with JSON response

## Alternative: Toggle Integration Method

If mapping deletion/recreation doesn't work:

1. **Go to Routes**
   - API Gateway → Your API → Routes

2. **Select Health Route**
   - Click on: `GET /health`

3. **Change to Mock Integration**
   - Edit integration
   - Change to **Mock** integration
   - Save and **Deploy** API

4. **Test**
   ```bash
   curl https://api.quentinspencer.com/api/v1/health
   ```
   - Should return mock 200 OK

5. **Change Back to Service Discovery**
   - Edit integration again
   - Change back to **VPC Link** / **Service Discovery**
   - Save and **Deploy** API

6. **Wait and Test**
   - Wait 2-5 minutes
   - Test again - should now return actual health check

## Why This Works

Deleting and recreating the API mapping forces API Gateway to:
1. Tear down the old integration cache
2. Rebuild the Service Discovery resolution
3. Discover the HEALTHY instance
4. Establish new routing path

## Verification After Fix

Once cache is cleared, verify:

```bash
# Should return 200 OK
curl https://api.quentinspencer.com/api/v1/health

# Should match direct endpoint
curl https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health
```

Both should return identical 200 OK responses with health check JSON.

## Expected Timeline

- Mapping deletion: Immediate
- Propagation wait: 60 seconds
- Mapping recreation: Immediate  
- Full propagation: 2-5 minutes
- **Total**: ~5-7 minutes

## Notes

- Instance must remain HEALTHY during this process
- Direct endpoint will continue working
- No downtime expected
- If still 503 after this, contact AWS Support


