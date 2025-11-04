# Urgent: Manual Cache Fix Required

## Status After 1+ Hour Wait

After waiting 1+ hour and attempting Terraform mapping recreation:
- ❌ Custom domain: Still returns 503
- ✅ Direct endpoint: Works (200 OK)
- ✅ Service Discovery: Instance is HEALTHY
- ✅ Integration: Correctly configured

## The Problem

The API Gateway custom domain cache is **extremely persistent**. Even after:
- Terraform mapping recreation
- 1+ hour wait time
- Multiple attempts

The cache still shows "no healthy instances" despite the instance being HEALTHY.

## Why Manual Console Fix is Required

Terraform recreation may not trigger the same cache invalidation path as manual console deletion. AWS may treat console deletions differently, triggering a more aggressive cache clear.

## Step-by-Step Console Fix

### Critical Steps - Follow Exactly

1. **Open AWS Console**
   ```
   https://console.aws.amazon.com/apigateway/home?region=us-east-1
   ```

2. **Navigate to Custom Domain Names**
   - Left sidebar → **Custom domain names**

3. **Select Domain**
   - Click: **api.quentinspencer.com**

4. **Go to API Mappings Tab**
   - Click: **API mappings** tab

5. **DELETE the Mapping**
   - Checkbox: Select the mapping
   - Click: **Delete** button
   - **CRITICAL**: Confirm deletion

6. **WAIT 60 FULL SECONDS**
   - ⏰ Use a timer
   - Don't skip this wait!
   - This allows AWS to fully process the deletion

7. **CREATE New Mapping**
   - Click: **Create API mapping**
   - **API**: `church-course-tracker-api` (or select from dropdown)
   - **Stage**: `$default`
   - **Path**: Leave EMPTY (for root path)
   - Click: **Save**

8. **WAIT 2-5 MINUTES**
   - Allow propagation time
   - Don't test immediately

9. **TEST**
   ```bash
   curl https://api.quentinspencer.com/api/v1/health
   ```
   - Expected: 200 OK with JSON response

## Why This Should Work

Manual console deletion:
- Triggers AWS internal cache invalidation
- Forces API Gateway to rebuild resolution cache
- Discovers HEALTHY instance on rebuild
- Different code path than Terraform recreation

## If Still 503 After Manual Fix

If manual console fix still doesn't work after 5+ minutes:

1. **Check API Gateway Logs**
   - Enable detailed logging
   - Check CloudWatch logs for Service Discovery errors

2. **Verify VPC Link Status**
   - API Gateway → VPC Links
   - Ensure link is ACTIVE

3. **Check Service Discovery Service**
   - Verify service is active
   - Confirm instance appears in console

4. **Contact AWS Support**
   - This may be a bug/limitation
   - Provide evidence:
     - Instance is HEALTHY
     - Direct endpoint works
     - Cache persists despite manual invalidation

## Expected Timeline

- Manual deletion: Immediate
- 60-second wait: Critical
- Mapping recreation: Immediate
- Propagation: 2-5 minutes
- **Total**: ~7-10 minutes

## Verification Checklist

After manual fix, verify:

- [ ] Mapping deleted successfully
- [ ] Waited full 60 seconds
- [ ] Mapping recreated successfully  
- [ ] Waited 2-5 minutes
- [ ] Custom domain returns 200 OK
- [ ] Response matches direct endpoint

## Current Configuration (For Reference)

- **Domain**: api.quentinspencer.com
- **API**: tinev5iszf (church-course-tracker-api)
- **Stage**: $default
- **Path**: (empty - root path)
- **Integration**: Service Discovery (xi7clij)
- **Service Discovery Service**: srv-ofgetwmad7pl2wx5
- **Instance Health**: HEALTHY ✅


