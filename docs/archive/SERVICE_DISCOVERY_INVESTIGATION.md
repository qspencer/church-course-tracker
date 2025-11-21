# Service Discovery Health Status Investigation

## Current Situation

### Working Components
- ✅ ECS Task: HEALTHY
- ✅ Direct API Gateway: Returns 200 OK
- ✅ Lambda Function: Executing successfully every 2 minutes
- ✅ Lambda API Calls: `update_instance_custom_health_status` returns success (no errors)

### Issue
- ⚠️ Service Discovery Instance: Remains UNHEALTHY despite successful API updates
- ⚠️ Custom Domain: Returns 503 (blocked by UNHEALTHY Service Discovery instance)

## Investigation Results

### API Call Verification
- ✅ Service ID is correct: `srv-ofgetwmad7pl2wx5`
- ✅ Instance ID is correct: Matches ECS task ID
- ✅ Region is correct: `us-east-1` (explicitly set in Lambda)
- ✅ API calls return success: No errors in responses or logs
- ✅ `health_check_custom_config` is configured: Required for update API

### Status Update Behavior
1. Lambda successfully calls `update_instance_custom_health_status` API
2. API returns success (no errors)
3. Status immediately checked after update: Still shows UNHEALTHY
4. Status remains UNHEALTHY even after waiting 5-10 minutes

### Key Observation
Instance has ECS attributes:
- `ECS_CLUSTER_NAME`: church-course-tracker-cluster
- `ECS_SERVICE_NAME`: church-course-tracker-service
- `ECS_TASK_DEFINITION_FAMILY`: church-course-tracker-backend

This indicates ECS registered the instance with Service Discovery.

## Hypothesis

**ECS Service Discovery Integration Behavior:**
When ECS registers instances with Service Discovery using `service_registries`, ECS may:
1. Set initial health status when registering the instance
2. Periodically update health status based on ECS's internal health check logic
3. Override manual status updates made via `update_instance_custom_health_status` API

This would explain why:
- Manual API updates succeed (no errors)
- Status doesn't change (ECS overrides it)
- Lambda keeps updating every 2 minutes (but status doesn't persist)

## AWS Documentation Notes

According to AWS documentation:
- `UpdateInstanceCustomHealthStatus` is only valid for services with `HealthCheckCustomConfig`
- With custom health checks, the application/service owner is responsible for updating health status
- However, when ECS manages Service Discovery registration, ECS may also manage health status

## Possible Solutions

### Option 1: Wait for ECS Health Sync
ECS may eventually sync container health to Service Discovery. Monitor for 15-30 minutes to see if status changes naturally.

### Option 2: Check ECS Service Discovery Configuration
Verify if there's a configuration option to have ECS sync container health to Service Discovery health status automatically.

### Option 3: Alternative Routing Approach
If API Gateway respects Service Discovery health filtering, we may need to:
- Find a way to bypass health filtering, OR
- Use a different routing mechanism that doesn't depend on Service Discovery health status

### Option 4: Accept Limitation
Use direct API Gateway endpoint instead of custom domain, or document the limitation.

## Next Steps

1. **Extended Monitoring**: Wait 15-30 minutes and monitor if status ever changes to HEALTHY
2. **AWS Support**: If status doesn't change, contact AWS support or check AWS forums for ECS Service Discovery health sync behavior
3. **Alternative Configuration**: Research if there's a way to configure ECS to sync container health to Service Discovery automatically
4. **Workaround**: Document current working state (direct gateway works) and consider using that as primary endpoint

## Current Working State

- Direct API Gateway endpoint: ✅ Working (200 OK)
- Backend is healthy: ✅ ECS tasks are HEALTHY
- Lambda solution: ✅ Implemented and functioning correctly
- Custom domain: ⚠️ Blocked by Service Discovery UNHEALTHY status

The infrastructure is correctly configured; the issue appears to be AWS Service Discovery behavior when ECS manages instance registration.


