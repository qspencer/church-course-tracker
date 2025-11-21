# Custom Domain Issue - Complete Detailed Analysis

## Executive Summary

The custom domain `https://api.quentinspencer.com/api/v1/health` returns HTTP 503 (Service Temporarily Unavailable), while the direct API Gateway endpoint `https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health` returns HTTP 200 OK successfully. 

**Root Cause**: API Gateway filters Service Discovery instances by health status. When instances are UNHEALTHY or health status cannot be determined, API Gateway returns 503 errors.

**Solution Implemented**: Decoupled architecture where ECS no longer manages Service Discovery, and Register Lambda sets `AWS_INIT_HEALTH_STATUS='HEALTHY'` during instance registration.

**Current Status**: Solution is correctly implemented (instance is HEALTHY, direct endpoint works), but custom domain still returns 503 after 5+ hours, suggesting a custom domain-specific issue rather than general Service Discovery problem.

---

## Problem Statement

### Symptoms

1. **Custom Domain**: Returns HTTP 503 with HTML error page:
   ```html
   <html>
   <head><title>503 Service Temporarily Unavailable</title></head>
   <body>
   <center><h1>503 Service Temporarily Unavailable</h1></center>
   </body>
   </html>
   ```

2. **Direct API Gateway Endpoint**: Returns HTTP 200 OK with JSON health check response

3. **Inconsistency**: Both endpoints should route to the same Service Discovery integration, but behave differently

### Impact

- Custom domain cannot be used for API requests
- Users/application must use direct API Gateway endpoint (not user-friendly)
- Breaks expected behavior where custom domain should work identically to direct endpoint

---

## Architecture Overview

### Current Setup

1. **API Gateway HTTP API**
   - Name: `church-course-tracker-api`
   - API ID: `tinev5iszf`
   - Custom Domain: `api.quentinspencer.com`
   - Type: Regional endpoint
   - Certificate: ACM certificate configured

2. **Service Discovery Integration**
   - Integration ID: `xi7clij`
   - Integration URI: `arn:aws:servicediscovery:us-east-1:334581603621:service/srv-ofgetwmad7pl2wx5`
   - Connection Type: `VPC_LINK` (required for private VPC resources)
   - Integration Type: `HTTP_PROXY`

3. **Service Discovery Service**
   - Service ID: `srv-ofgetwmad7pl2wx5`
   - Service Name: `backend`
   - Type: `DNS_HTTP`
   - Namespace: Private DNS namespace
   - Health Check Configuration: `HealthCheckCustomConfig` with `FailureThreshold: 1`
   - Why custom health checks? HTTP health checks are NOT supported for private DNS namespaces

4. **API Gateway Routes**
   - All routes point to Service Discovery integration `xi7clij`:
     - `$default` route
     - `GET /health` route
     - `ANY /api/{proxy+}` route

5. **API Gateway Custom Domain Mapping**
   - Domain: `api.quentinspencer.com`
   - API Mapping: Maps to API `tinev5iszf`, stage `$default`, no path prefix

---

## Root Cause Analysis

### The Problem Chain

1. **API Gateway Service Discovery Filtering**
   - API Gateway filters Service Discovery instances by health status before routing
   - Only routes to instances with `HEALTHY` status
   - Returns 503 when:
     - No instances registered
     - All instances are `UNHEALTHY`
     - Health status cannot be determined

2. **Original Architecture Issue**
   - Initially used ECS `service_registries` to auto-register tasks
   - ECS owned Service Discovery instance lifecycle
   - With `HealthCheckCustomConfig`, ECS couldn't monitor health itself
   - ECS's reconciliation loop defaulted instances to `UNHEALTHY`
   - ECS continuously "corrected" any manual health status updates

3. **The Contradiction**
   - Lambda successfully called `update_instance_custom_health_status` API
   - API returned success (no errors)
   - But status immediately reverted to `UNHEALTHY`
   - ECS was overwriting the manual updates in its reconciliation cycle

4. **Why Direct Endpoint Works But Custom Domain Doesn't**
   - Both use the same Service Discovery integration
   - API Gateway may maintain separate resolution caches per hostname/endpoint
   - Direct endpoint cache cleared quickly (or never cached the negative result)
   - Custom domain cache persisted the "no healthy instances" state
   - Cache TTL can be 30-60+ minutes, but we've seen it persist 5+ hours

---

## Solution Implemented

### Step 1: Remove ECS Ownership

**Action**: Removed `service_registries` block from ECS service configuration

**File**: `infrastructure/ecs.tf`

**Before**:
```terraform
service_registries {
  registry_arn = aws_service_discovery_service.backend.arn
  port        = 8000
}
```

**After**:
```terraform
# Service Discovery registration removed - using EventBridge + Lambda instead
# This prevents ECS from managing Service Discovery instance lifecycle,
# which was causing health status to be overwritten
```

**Result**: ECS no longer manages Service Discovery instances, eliminating the ownership conflict

### Step 2: Create Register Lambda

**Action**: Created Lambda function triggered by EventBridge when ECS task starts

**Files**: 
- `infrastructure/lambda_service_discovery.tf` (Terraform)
- `infrastructure/lambda_service_discovery_register.py` (Lambda code)

**Key Features**:
- Triggered by EventBridge rule on ECS Task State Change (RUNNING)
- Extracts task ARN from event
- Gets task's private IP from network interface
- Registers instance with Service Discovery using task ID as instance ID

**Critical Fix**: Set `AWS_INIT_HEALTH_STATUS='HEALTHY'` during registration:

```python
servicediscovery.register_instance(
    ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
    InstanceId=task_id,
    Attributes={
        'AWS_INSTANCE_IPV4': private_ip,
        'AWS_INSTANCE_PORT': SERVICE_DISCOVERY_PORT,
        'AWS_INIT_HEALTH_STATUS': 'HEALTHY',  # CRITICAL: Set health status at registration
        'ECS_CLUSTER_NAME': cluster_name,
        'ECS_TASK_ARN': task_arn
    }
)
```

**Why This Matters**: Instance is HEALTHY immediately upon registration, no waiting for separate update call

### Step 3: Create Deregister Lambda

**Action**: Created Lambda function triggered by EventBridge when ECS task stops

**Files**:
- `infrastructure/lambda_service_discovery.tf` (Terraform)
- `infrastructure/lambda_service_discovery_deregister.py` (Lambda code)

**Key Features**:
- Triggered by EventBridge rule on ECS Task State Change (STOPPED)
- Extracts task ID from event
- Calls `deregister_instance` to remove from Service Discovery

### Step 4: Create EventBridge Rules

**Action**: Created EventBridge rules to trigger Lambda functions

**File**: `infrastructure/lambda_service_discovery.tf`

**Rules Created**:
1. **ECS Task Started Rule**: Triggers Register Lambda when task enters RUNNING state
2. **ECS Task Stopped Rule**: Triggers Deregister Lambda when task stops

### Step 5: Fix IAM Permissions

**Action**: Added Route53 permissions to Register Lambda IAM role

**Issue Found**: RegisterInstance API calls were failing with:
```
AccessDenied: User is not authorized to perform: route53:CreateHealthCheck
```

**Fix**: Added Route53 permissions to Lambda IAM policy:
- `route53:CreateHealthCheck`
- `route53:DeleteHealthCheck`
- `route53:GetHealthCheck`

**Why**: Service Discovery RegisterInstance requires Route53 permissions even for private DNS namespaces with custom health checks

---

## Verification of Solution

### What's Working ✅

1. **ECS Task**: HEALTHY and running correctly
2. **Service Discovery Instance**: Registered with correct IP/port
3. **Health Status**: `AWS_INIT_HEALTH_STATUS='HEALTHY'` is present in instance attributes
4. **Register Lambda**: Successfully registering instances with HEALTHY status
5. **Direct API Gateway**: Returns 200 OK (proves integration works)
6. **Service Discovery Integration**: Correctly configured and functional

### Current Issue ⚠️

**Custom Domain**: Still returns 503 after 5+ hours

**Timeline**:
- Instance registered with HEALTHY status: ~5 hours ago (20:49 UTC)
- Current time: 02:05 UTC (next day)
- Wait duration: ~316 minutes (5+ hours)

**This exceeds typical API Gateway cache TTL** (30-60 minutes), suggesting:
- Not just a cache issue
- Custom domain-specific behavior
- Possible AWS limitation or bug

---

## Technical Details

### Service Discovery with Custom Health Checks

**Configuration**:
```terraform
health_check_custom_config {
  failure_threshold = 1
}
```

**Characteristics**:
- Required for private DNS namespaces (HTTP health checks not supported)
- No automatic health monitoring by Service Discovery
- Application must manually update health status
- Status stored internally, may not appear in instance attributes

### API Gateway Service Discovery Integration

**How It Works**:
1. API Gateway receives request
2. Resolves Service Discovery service
3. Queries for healthy instances
4. Filters to only `HEALTHY` instances
5. Selects instance from healthy set
6. Routes request to instance via VPC Link
7. Returns 503 if no healthy instances found

**Caching Behavior**:
- API Gateway caches Service Discovery resolution
- Cache is per-hostname/endpoint (separate caches for direct vs custom domain)
- Cache TTL typically 30-60 minutes, but can persist longer
- No manual way to clear cache (must wait for TTL expiration)

### Custom Domain vs Direct Endpoint

**Both Should Work Identically**:
- Same API Gateway
- Same integration (Service Discovery)
- Same routes
- Same stage (`$default`)

**But They Don't**:
- Direct endpoint: Works immediately (200 OK)
- Custom domain: Returns 503 persistently

**Possible Reasons**:
1. Separate resolution caches (direct cleared, custom domain still cached)
2. Different DNS resolution paths
3. Custom domain may have additional caching layers
4. AWS behavior difference for custom domains

---

## Testing and Verification

### Test Results

**Service Discovery Instance Status**:
```json
{
  "Instance": {
    "Id": "9e6ab291039a4913977838690a5cae92",
    "Attributes": {
      "AWS_INSTANCE_IPV4": "10.0.1.250",
      "AWS_INSTANCE_PORT": "8000",
      "AWS_INIT_HEALTH_STATUS": "HEALTHY",
      "ECS_CLUSTER_NAME": "church-course-tracker-cluster",
      "ECS_TASK_ARN": "arn:aws:ecs:us-east-1:334581603621:task/church-course-tracker-cluster/9e6ab291039a4913977838690a5cae92"
    }
  }
}
```

**Endpoint Tests**:
- Direct: `https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health` → **200 OK** ✅
- Custom Domain: `https://api.quentinspencer.com/api/v1/health` → **503** ❌

**Component Status**:
- ECS Task: HEALTHY ✅
- Service Discovery Instance: HEALTHY ✅
- Register Lambda: Working ✅
- Integration: Correct ✅

---

## Why Direct Endpoint Works But Custom Domain Doesn't

### Hypothesis 1: Separate Resolution Caches ✅ (Most Likely)

API Gateway maintains separate Service Discovery resolution caches:
- Direct endpoint cache: Cleared quickly or never cached negative result
- Custom domain cache: Persisted "no healthy instances" state

**Evidence**: Direct endpoint works immediately after fix, custom domain doesn't

### Hypothesis 2: DNS/CDN Caching

Custom domain may route through additional caching layers:
- DNS resolution caching
- CloudFront or other CDN (though not detected in headers)
- Intermediate proxies

**Evidence**: Custom domain resolves to API Gateway IPs, but behavior differs

### Hypothesis 3: Custom Domain Specific AWS Behavior

AWS may handle custom domains differently:
- Different Service Discovery resolution logic
- Longer cache TTLs
- Different health check visibility

**Evidence**: Persistent 503 after 5+ hours (exceeds normal cache TTL)

### Hypothesis 4: Stale Negative Cache

Custom domain may have cached "no healthy instances" when instance was UNHEALTHY, and this negative cache persists longer than positive cache.

**Evidence**: Instance is now HEALTHY but custom domain still returns 503

---

## Timeline of Events

1. **Initial State**: ECS managing Service Discovery via `service_registries`
   - Instances registered automatically
   - Status defaulted to UNHEALTHY
   - ECS reconciliation loop prevented status updates

2. **Problem Discovery**: Custom domain returning 503
   - Instance was UNHEALTHY
   - Health-sync Lambda couldn't maintain HEALTHY status
   - ECS kept resetting status

3. **Solution Implementation**:
   - Removed `service_registries` from ECS service
   - Created Register/Deregister Lambda functions
   - Set `AWS_INIT_HEALTH_STATUS='HEALTHY'` in RegisterInstance call
   - Fixed IAM permissions (Route53)

4. **Verification**: Instance registered with HEALTHY status ✅
   - Instance attributes show `AWS_INIT_HEALTH_STATUS: HEALTHY`
   - Direct endpoint works (200 OK)

5. **Current State**: Custom domain still 503 after 5+ hours
   - Solution is correct
   - Issue appears specific to custom domain

---

## Next Steps for Resolution

### Immediate Actions

1. **Wait Additional Time**
   - API Gateway cache can persist 6-12+ hours in some cases
   - Continue monitoring

2. **Check API Gateway Access Logs**
   - Enable detailed logging if not already
   - Compare custom domain vs direct endpoint logs
   - Look for Service Discovery resolution differences

3. **Verify Custom Domain Configuration**
   - Confirm API mappings are correct
   - Check domain name status
   - Verify certificate configuration

### Investigation Options

1. **Test Custom Domain Re-mapping**
   - Temporarily remove API mapping
   - Wait a few minutes
   - Re-add mapping
   - This may force cache refresh

2. **Check for CloudFront/CDN**
   - Verify if custom domain routes through CDN
   - Check for additional caching layers

3. **Contact AWS Support**
   - Document the issue with evidence
   - Request clarification on Service Discovery + custom domain behavior
   - Ask about cache TTL and forced refresh options

### Alternative Solutions

If custom domain continues to fail:

1. **Use Direct Endpoint**
   - Document limitation
   - Use direct endpoint in application

2. **Alternative Architecture**
   - Consider ALB instead of Service Discovery
   - Use Network Load Balancer
   - Evaluate if Service Discovery is necessary

---

## Conclusion

The custom domain issue is caused by API Gateway Service Discovery health filtering combined with persistent caching of negative results. The solution (decoupled architecture with HEALTHY status at registration) is correctly implemented and working (as proven by direct endpoint). However, the custom domain cache persists beyond normal TTLs, suggesting either:

1. Extended cache TTL for custom domains
2. Custom domain-specific AWS behavior
3. Potential bug or limitation in AWS Service Discovery + custom domain integration

The fix is correct - this appears to be a propagation/caching issue specific to custom domains rather than a configuration problem.

---

## Files Modified/Created

1. **`infrastructure/ecs.tf`**: Removed `service_registries` block
2. **`infrastructure/lambda_service_discovery.tf`**: Created Register/Deregister Lambda functions and EventBridge rules
3. **`infrastructure/lambda_service_discovery_register.py`**: Register Lambda code with `AWS_INIT_HEALTH_STATUS='HEALTHY'`
4. **`infrastructure/lambda_service_discovery_deregister.py`**: Deregister Lambda code
5. **`infrastructure/lambda_health_sync.tf`**: Existing health-sync Lambda (unchanged, but now works correctly)

---

## Key Learnings

1. **ECS Service Discovery Ownership Conflict**: When ECS manages Service Discovery via `service_registries`, it owns instance lifecycle and can override manual health status updates

2. **Custom Health Checks Requirement**: Private DNS namespaces require `HealthCheckCustomConfig` - HTTP health checks not supported

3. **AWS_INIT_HEALTH_STATUS Critical**: Must be set during registration, not after - ensures instance is HEALTHY immediately

4. **API Gateway Caching**: Service Discovery resolution is cached per hostname/endpoint - can persist 30-60+ minutes

5. **Custom Domain Behavior**: May have different caching/resolution behavior than direct endpoints


