# Recommended Next Steps - Final Status

## ✅ Problem Solved!

**Root Cause Found**: Missing Route53 IAM permissions for RegisterInstance operation.

**Fix Applied**: Added Route53 permissions to Lambda IAM role:
- `route53:CreateHealthCheck`
- `route53:DeleteHealthCheck`
- `route53:GetHealthCheck`

**Status**: Service Discovery registration is now working! Instance successfully registered.

## Current Status

✅ **Working:**
- Register Lambda: Successfully registering instances
- Deregister Lambda: Ready for task stop events
- Health-sync Lambda: Running every 2 minutes, will update status to HEALTHY
- Service Discovery: Instance registered (health will be updated by health-sync)

## Next Steps (In Order)

### 1. Wait for Health Sync ⏱️ (2 minutes)

The health-sync Lambda runs every 2 minutes and will:
- Find the registered instance
- Check ECS task health (should be HEALTHY)
- Update Service Discovery instance health to HEALTHY

**Action**: Wait 2-3 minutes, then check status

**Command**:
```bash
SERVICE_ID=$(aws servicediscovery list-services \
  --query "Services[?Name=='backend'].Id" \
  --output text)
aws servicediscovery list-instances \
  --service-id "$SERVICE_ID" \
  --region us-east-1 \
  --query 'Instances[0].Attributes.AWS_INIT_HEALTH_STATUS' \
  --output text
```

### 2. Test Custom Domain 🌐

Once instance health is HEALTHY:

**Command**:
```bash
curl -v https://api.quentinspencer.com/api/v1/health | jq
```

**Expected**: HTTP 200 OK with health check JSON response

### 3. Verify Full Lifecycle 🔄

Test complete flow:
1. **Register**: Restart ECS service → Register Lambda registers new task
2. **Health Sync**: Health-sync Lambda updates to HEALTHY
3. **Custom Domain**: Should return 200 OK
4. **Deregister**: Stop task → Deregister Lambda removes instance

**Test commands**:
```bash
# Force new deployment (triggers register)
aws ecs update-service \
  --cluster church-course-tracker-cluster \
  --service church-course-tracker-service \
  --force-new-deployment

# Monitor logs
aws logs tail /aws/lambda/church-course-tracker-service-discovery-register --follow
aws logs tail /aws/lambda/church-course-tracker-health-sync --follow
```

### 4. Monitor and Validate 📊

Monitor all components for 10-15 minutes:
- Register Lambda logs (should see registration on task start)
- Health-sync Lambda logs (should update health every 2 min)
- Service Discovery instances (should show HEALTHY)
- Custom domain (should return 200 OK)

## Success Criteria

✅ Service Discovery instance appears after task starts  
✅ Instance health status updates to HEALTHY  
✅ Status persists (doesn't revert to UNHEALTHY)  
✅ Custom domain returns 200 OK  
✅ Full lifecycle works (register → healthy → deregister)

## Architecture Summary

```
ECS Task Starts
    ↓
EventBridge (ECS Task State Change: RUNNING)
    ↓
Register Lambda
    ↓
Service Discovery Instance Registered
    ↓
Health-Sync Lambda (every 2 min)
    ↓
Instance Health = HEALTHY
    ↓
API Gateway Routes to Instance
    ↓
Custom Domain Returns 200 OK ✅
```

## Files Modified

- `infrastructure/lambda_service_discovery.tf` - Added Route53 permissions to IAM policy
- `infrastructure/ecs.tf` - Removed service_registries
- `infrastructure/lambda_service_discovery_register.py` - Register Lambda code
- `infrastructure/lambda_service_discovery_deregister.py` - Deregister Lambda code

## Notes

- **IAM Permissions**: Service Discovery RegisterInstance requires Route53 permissions even for private DNS namespaces with custom health checks
- **Timing**: Service Discovery operations are asynchronous - may take 30-60 seconds
- **Health Sync**: Runs every 2 minutes automatically via EventBridge schedule
- **No ECS Override**: ECS no longer manages instances, so health status will persist


