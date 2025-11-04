# Custom Domain Issue - Detailed Analysis

## Overview

The custom domain `https://api.quentinspencer.com/api/v1/health` returns HTTP 503 (Service Temporarily Unavailable), while the direct API Gateway endpoint `https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health` returns HTTP 200 OK successfully.

## Infrastructure Architecture

### Current Setup

1. **API Gateway HTTP API** (`church-course-tracker-api`)
   - Custom Domain: `api.quentinspencer.com`
   - API Mappings: Maps custom domain to `$default` stage
   - Routes: All routes (`$default`, `GET /health`, `ANY /api/{proxy+}`) point to Service Discovery integration

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
   - Health Check Configuration: `HealthCheckCustomConfig` (required for private DNS namespaces with VPC Link)
     - `FailureThreshold: 1`

4. **ECS Task**
   - Task ID: `da09289b58a84d81847995f8ade49ecd`
   - Health Status: `HEALTHY` (verified via `ecs describe-tasks`)
   - Container Health Check: Configured and passing
   - Private IP: `10.0.1.164`

## The Problem

### Symptom
- **Custom Domain**: Returns HTTP 503
- **Direct API Gateway**: Returns HTTP 200 OK
- **Health Endpoint Response**: `<html><head><title>503 Service Temporarily Unavailable</title></head><body>`

### Root Cause Analysis

#### API Gateway Service Discovery Health Filtering

API Gateway filters Service Discovery instances by health status when using Service Discovery as the integration target. When all instances for a service are `UNHEALTHY` or there are no healthy instances, API Gateway returns a 503 error.

**Expected Behavior:**
- API Gateway should route to instances with `HEALTHY` status
- API Gateway should return 503 if no healthy instances are available

**Actual Behavior:**
- Custom domain returns 503 despite health-sync Lambda reporting successful status updates
- Health status updates are not being recognized by API Gateway

## Health Status Update Mechanism

### Implementation

1. **Health-Sync Lambda Function**
   - Runs every 2 minutes via EventBridge schedule
   - Finds ECS tasks that are `HEALTHY` and `RUNNING`
   - Finds corresponding Service Discovery instances (matched by Task ID = Instance ID)
   - Calls `servicediscovery.update_instance_custom_health_status` API
   - Reports: "Successfully updated instance {id} from UNKNOWN to HEALTHY"

2. **Lambda Execution Logs**
   ```
   2025-11-02T20:39:29 [INFO] Successfully updated instance da09289b58a84d81847995f8ade49ecd 
   from UNKNOWN to HEALTHY (task health: HEALTHY, status: RUNNING)
   ```
   - Lambda consistently reports successful updates
   - Updates occur every 2 minutes
   - No errors in Lambda execution

### Verification Attempts

#### 1. Checking Instance Attributes

**Command:**
```bash
aws servicediscovery get-instance \
  --service-id srv-ofgetwmad7pl2wx5 \
  --instance-id da09289b58a84d81847995f8ade49ecd \
  --region us-east-1
```

**Result:**
```json
{
  "Instance": {
    "Id": "da09289b58a84d81847995f8ade49ecd",
    "Attributes": {
      "AWS_INSTANCE_IPV4": "10.0.1.164",
      "AWS_INSTANCE_PORT": "8000",
      "ECS_CLUSTER_NAME": "church-course-tracker-cluster",
      "ECS_TASK_ARN": "arn:aws:ecs:us-east-1:334581603621:task/church-course-tracker-cluster/da09289b58a84d81847995f8ade49ecd"
    }
  }
}
```

**Observation:** The `AWS_INIT_HEALTH_STATUS` attribute is **NOT present** in the instance attributes, despite health-sync Lambda reporting successful updates.

#### 2. Attempted Health Status Query

**Command:**
```bash
aws servicediscovery get-instances-health-status \
  --service-id srv-ofgetwmad7pl2wx5 \
  --instance-ids da09289b58a84d81847995f8ade49ecd \
  --region us-east-1
```

**Result:** API returns error or invalid response format

**Observation:** `GetInstancesHealthStatus` API may not be available or may work differently for custom health checks.

## Technical Details

### Custom Health Check Configuration

With `HealthCheckCustomConfig` in a private DNS namespace:

1. **No Automatic Health Checks**: Service Discovery does not perform HTTP/HTTPS health checks
2. **Manual Status Management**: Application must manually update health status via `update_instance_custom_health_status` API
3. **Status Storage**: Health status is stored internally by Service Discovery, not necessarily in instance attributes

### API Gateway Service Discovery Integration Behavior

When API Gateway uses Service Discovery as an integration:

1. **Health Status Filtering**: API Gateway filters instances by health status
2. **Resolution Process**:
   - API Gateway queries Service Discovery for instances
   - Filters to only `HEALTHY` instances
   - Selects an instance from the healthy set
   - Routes request to that instance

3. **503 Error Conditions**:
   - No instances registered
   - All instances are `UNHEALTHY`
   - Health status cannot be determined
   - Service Discovery query fails

### Why Direct API Gateway Works But Custom Domain Doesn't

This is actually a **misconception** - both endpoints use the same integration. However:

1. **Custom Domain**: Goes through additional DNS resolution and may have different caching behavior
2. **API Gateway Caching**: Custom domains may have different cache TTLs for Service Discovery resolution
3. **DNS Propagation**: Custom domain DNS may resolve differently
4. **Time-Based**: Different endpoints tested at different times may show different results

**Actual Testing:**
- Both endpoints should behave the same if they use the same integration
- If direct endpoint works, custom domain should also work
- The discrepancy suggests timing or caching differences

## Current State

### Working Components ✅

1. **ECS Task**: HEALTHY and running correctly
2. **Service Discovery Instance**: Registered with correct IP and port
3. **Register Lambda**: Successfully registers instances on task start
4. **Health-Sync Lambda**: Executes successfully, reports status updates
5. **API Gateway Integration**: Correctly configured to use Service Discovery
6. **Routes**: All routes correctly point to Service Discovery integration
7. **EventBridge Rules**: Triggering correctly for task lifecycle events

### Issue Components ⚠️

1. **Health Status Visibility**: 
   - Health status updates reported by Lambda but not visible in instance attributes
   - API Gateway may not see the health status even though Lambda reports updates

2. **Custom Domain Response**: 
   - Consistently returns 503
   - Suggests API Gateway cannot find healthy instances

3. **Status Propagation**: 
   - Updates may take time to propagate through Service Discovery to API Gateway
   - Custom health check status may have different propagation characteristics

## Possible Root Causes

### Hypothesis 1: Health Status Not Actually Being Set

**Evidence Against:**
- Lambda reports successful API calls
- No errors in Lambda execution logs
- `update_instance_custom_health_status` API returns success

**Evidence For:**
- `AWS_INIT_HEALTH_STATUS` attribute not present in instance attributes
- Custom domain still returns 503

**Verdict**: Likely - Status may not be persisting or may not be visible to API Gateway

### Hypothesis 2: Propagation Delay

**Evidence For:**
- Service Discovery operations are asynchronous
- API Gateway may cache Service Discovery resolution
- Custom domain may have different cache behavior

**Verdict**: Possible - But we've waited 10+ minutes, which should be sufficient

### Hypothesis 3: Custom Health Check Status Not Visible to API Gateway

**Evidence For:**
- Status attribute doesn't appear in `get-instance` response
- API Gateway may require different health check configuration
- Private DNS namespace + custom health checks may have limitations

**Verdict**: Likely - This seems to be the core issue

### Hypothesis 4: API Gateway Service Discovery Resolution Issue

**Evidence For:**
- Direct endpoint works (at different times)
- Custom domain consistently returns 503
- Both should use same integration but may have different resolution paths

**Verdict**: Possible - May be related to DNS/caching differences

## Investigation Attempts

### Attempt 1: Verify Integration Configuration
**Result**: ✅ Confirmed integration correctly uses Service Discovery ARN

### Attempt 2: Check Instance Registration
**Result**: ✅ Instance is registered correctly with correct IP/port

### Attempt 3: Verify Health Status Updates
**Result**: ⚠️ Lambda reports success, but status not visible in attributes

### Attempt 4: Wait for Propagation
**Result**: ⚠️ Waited 10+ minutes, status still not visible, custom domain still 503

### Attempt 5: Check for Multiple Integrations
**Result**: ✅ Found ALB integration exists but is not used; Service Discovery integration is active

### Attempt 6: Verify Routes Point to Correct Integration
**Result**: ✅ All routes correctly point to Service Discovery integration

## AWS Service Discovery Behavior with Custom Health Checks

### Known Behaviors

1. **Custom Health Check Status**:
   - Status is managed separately from instance attributes
   - `AWS_INIT_HEALTH_STATUS` attribute may not appear in `get-instance` response
   - Status may be stored internally and not exposed via attributes API

2. **API Gateway Integration**:
   - API Gateway queries Service Discovery for healthy instances
   - For custom health checks, API Gateway must query internal health status
   - Status may not be immediately visible but should be used for routing

3. **Private DNS Namespaces**:
   - HTTP health checks are NOT supported (only public namespaces)
   - Must use `HealthCheckCustomConfig`
   - Manual status management required

## Next Steps for Resolution

### Immediate Actions

1. **Verify Health Status is Actually Being Set**:
   - Manually call `update_instance_custom_health_status` API
   - Immediately test custom domain
   - Check if status change is reflected

2. **Check API Gateway Logs**:
   - Enable API Gateway access logging
   - Check CloudWatch logs for Service Discovery resolution errors
   - Look for health status filtering messages

3. **Test Direct Instance Access**:
   - Verify instance is accessible via VPC Link
   - Test health endpoint directly
   - Confirm networking is correct

### Long-Term Solutions

1. **Alternative Architecture**:
   - Consider using Application Load Balancer instead of Service Discovery
   - Use Network Load Balancer with Service Discovery
   - Use ALB with target groups and health checks

2. **AWS Support**:
   - Escalate to AWS Support about custom health check visibility
   - Request clarification on API Gateway + Service Discovery + custom health checks
   - Ask about known limitations or required configurations

3. **Alternative Health Check**:
   - If possible, use public DNS namespace with HTTP health checks
   - This may not be feasible for private VPC resources

## Conclusion

The custom domain issue is caused by API Gateway not recognizing Service Discovery instances as healthy, despite:

1. ✅ ECS tasks being healthy
2. ✅ Instances being registered correctly
3. ✅ Health-sync Lambda reporting successful status updates
4. ✅ Integration being correctly configured

The core issue appears to be that **custom health check status updates may not be visible or properly recognized by API Gateway** when using:
- Private DNS namespace
- `HealthCheckCustomConfig`
- VPC Link integration

This may be a limitation or configuration requirement that needs AWS Support clarification.


