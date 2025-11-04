# Recommended Next Steps

## Current Status

✅ **Completed:**
- Decoupled architecture implemented (ECS no longer manages Service Discovery)
- Register Lambda created and invoked by EventBridge
- Deregister Lambda created and working
- Health-sync Lambda ready to work (no longer fighting with ECS)
- All infrastructure deployed successfully

⚠️ **Issue:**
- RegisterInstance API calls succeed but instances don't appear immediately
- Need to verify operation completion and timing

## Next Steps

### 1. Debug Registration Timing (High Priority)

**Problem**: RegisterInstance operations are asynchronous. Instances may take 30-60 seconds to appear after registration.

**Actions**:
- Check operation status using `servicediscovery.get_operation(OperationId)`
- Verify if operations are completing successfully
- Add polling logic to Register Lambda to wait for completion
- Check CloudWatch logs for any error messages

**Command to test**:
```bash
# Get operation ID from Register Lambda logs
OPERATION_ID="your-operation-id-here"
aws servicediscovery get-operation \
  --operation-id "$OPERATION_ID" \
  --region us-east-1
```

### 2. Verify Instance Appearance

**Actions**:
- Wait 60-90 seconds after task start and check again
- Monitor Service Discovery instances list continuously
- Verify instance ID matches ECS task ID

**Command to monitor**:
```bash
# Watch Service Discovery instances
watch -n 5 'aws servicediscovery list-instances \
  --service-id $(aws servicediscovery list-services \
    --query "Services[?Name=='\''backend'\''].Id" \
    --output text) \
  --region us-east-1 \
  --output json | python3 -m json.tool'
```

### 3. Test Health Sync Lambda

**Once instances appear:**
- Verify health-sync Lambda finds the instances
- Check if it successfully updates health status to HEALTHY
- Verify status persists (doesn't revert to UNHEALTHY)

**Expected behavior**:
- Health-sync Lambda runs every 2 minutes
- Finds registered instances
- Updates status from UNHEALTHY to HEALTHY
- Status should persist (no ECS override anymore)

### 4. Test Custom Domain

**Once Service Discovery instance is HEALTHY:**
- Test custom domain: `https://api.quentinspencer.com/api/v1/health`
- Should return 200 OK (not 503)
- Verify API Gateway routing works

**Test command**:
```bash
curl -v https://api.quentinspencer.com/api/v1/health | jq
```

### 5. Monitor Complete Flow

**Test end-to-end:**
1. Restart ECS service → Register Lambda should register new task
2. Health-sync Lambda should update health to HEALTHY
3. Custom domain should work
4. Stop task → Deregister Lambda should remove instance

**Monitoring commands**:
```bash
# Monitor Register Lambda
aws logs tail /aws/lambda/church-course-tracker-service-discovery-register --follow

# Monitor Health-sync Lambda
aws logs tail /aws/lambda/church-course-tracker-health-sync --follow

# Monitor Service Discovery
watch -n 10 'aws servicediscovery list-instances \
  --service-id srv-ofgetwmad7pl2wx5 \
  --region us-east-1'
```

### 6. Improve Register Lambda (Optional Enhancement)

**Current issue**: Register Lambda doesn't wait for operation completion.

**Enhancement**:
- Add `get_operation` polling after `register_instance`
- Wait up to 30 seconds for operation to complete
- Log success/failure of operation
- Retry if operation fails

**Code addition** (already attempted, needs to be applied):
```python
# After register_instance call, poll for completion
if operation_id:
    import time
    for _ in range(15):  # 30 seconds max
        op_response = servicediscovery.get_operation(OperationId=operation_id)
        status = op_response.get('Operation', {}).get('Status')
        if status == 'SUCCESS':
            logger.info("Registration completed successfully")
            break
        elif status == 'FAIL':
            raise Exception("Registration failed")
        time.sleep(2)
```

## Immediate Action Items

1. **Wait and check**: Give Service Discovery 60-90 seconds after registration, then check instances again
2. **Check operation status**: Use the operation ID from Register Lambda logs to verify completion
3. **Monitor logs**: Watch all three Lambda functions for any errors
4. **Test health sync**: Once instance appears, verify health-sync Lambda updates it to HEALTHY

## Success Criteria

✅ Service Discovery instance appears after task starts  
✅ Instance health status can be updated to HEALTHY  
✅ Status persists (doesn't revert to UNHEALTHY)  
✅ Custom domain returns 200 OK  
✅ Full lifecycle works (register → healthy → deregister)

## Troubleshooting

If instances still don't appear:
1. Check Service Discovery service configuration (HealthCheckCustomConfig must be present)
2. Verify IAM permissions for Register Lambda
3. Check if there are any Service Discovery limits/quota issues
4. Verify the Service ID is correct in environment variables

If health status doesn't persist:
1. Verify ECS service_registries is completely removed
2. Check health-sync Lambda logs for errors
3. Verify Service Discovery instance has correct attributes


