# Service Discovery Health Sync Solution

## Problem Statement

Service Discovery instances were showing as UNHEALTHY even when ECS tasks were HEALTHY, causing API Gateway custom domain to return 503 errors.

### Root Causes Identified

1. **HTTP health checks not supported**: For private DNS namespaces, AWS Service Discovery does NOT support `health_check_config` (HTTP health checks)
2. **Custom health checks don't auto-sync**: When using `health_check_custom_config`, Service Discovery doesn't automatically sync with ECS task health status
3. **Manual updates unreliable**: Manual health status updates via `update_instance_custom_health_status` API don't persist or work reliably

## Solution Implemented

### 1. Security Group Configuration

Added VPC CIDR (10.0.0.0/16) ingress rule to ECS security group to allow Service Discovery health checks:

```terraform
ingress {
  from_port   = 8000
  to_port     = 8000
  protocol    = "tcp"
  cidr_blocks = [module.vpc.vpc_cidr_block]
  description = "Allow Service Discovery health checks from within VPC"
}
```

### 2. Removed Health Check Configuration

Removed health check configuration from Service Discovery service:

```terraform
resource "aws_service_discovery_service" "backend" {
  name = "backend"
  
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 10
      type = "SRV"
    }
    routing_policy = "MULTIVALUE"
  }
  
  # No health check configuration - allows all instances to be registered
}
```

### 3. Lambda Health Sync Function

Created an automated Lambda function that syncs ECS task health to Service Discovery instance health status every 2 minutes.

**Location**: `infrastructure/lambda_health_sync.tf` and `infrastructure/lambda_health_sync.py`

**How it works**:
1. EventBridge triggers Lambda every 2 minutes
2. Lambda lists all running ECS tasks for the service
3. Gets task health status (HEALTHY/UNHEALTHY/UNKNOWN)
4. Finds corresponding Service Discovery instances (instance ID = task ID)
5. Updates Service Discovery instance health status to match ECS task health

**Lambda Permissions**:
- ECS: `ListTasks`, `DescribeTasks`
- Service Discovery: `ListInstances`, `GetInstance`, `UpdateInstanceCustomHealthStatus`
- CloudWatch Logs: Full access for logging

## Files Created/Modified

### New Files
- `infrastructure/lambda_health_sync.tf` - Terraform configuration for Lambda function
- `infrastructure/lambda_health_sync.py` - Lambda function code
- `infrastructure/health_sync_lambda.zip` - Generated Lambda package (git-ignored)

### Modified Files
- `infrastructure/main.tf` - Added `archive` provider for Lambda packaging
- `infrastructure/api_gateway.tf` - Removed health check configuration from Service Discovery service
- `infrastructure/main.tf` (security groups) - Added VPC CIDR ingress rule

## Testing

### Verify Lambda Function
```bash
# Check Lambda function exists
aws lambda get-function --function-name church-course-tracker-health-sync --region us-east-1

# Manually invoke Lambda
aws lambda invoke --function-name church-course-tracker-health-sync --region us-east-1 --payload '{}' response.json

# Check Lambda logs
aws logs tail /aws/lambda/church-course-tracker-health-sync --region us-east-1 --follow
```

### Verify Service Discovery Health Status
```bash
# Get Service Discovery service ID
SERVICE_ID=$(aws servicediscovery list-services --query "Services[?Name=='backend'].Id" --output text --region us-east-1)

# List instances and check health status
aws servicediscovery list-instances --service-id "$SERVICE_ID" --region us-east-1
```

### Test Custom Domain
```bash
# Test health endpoint
curl https://api.quentinspencer.com/api/v1/health

# Should return 200 OK with JSON health status
```

## Monitoring

### CloudWatch Metrics
- Lambda invocations: `/aws/lambda/church-course-tracker-health-sync`
- Lambda errors: Check CloudWatch Logs for any execution errors
- EventBridge rule: Monitor rule execution in EventBridge console

### Key Metrics to Watch
1. Lambda execution success rate
2. Service Discovery instance health status transitions
3. API Gateway 503 error rate (should decrease after Lambda syncs)

## Troubleshooting

### Issue: Lambda not updating health status

**Check**:
1. Lambda logs for errors: `aws logs tail /aws/lambda/church-course-tracker-health-sync --region us-east-1`
2. Lambda IAM permissions - ensure it can access ECS and Service Discovery
3. Service Discovery service ID is correct in Lambda environment variables
4. **CRITICAL**: Ensure boto3 clients explicitly specify the region (e.g., `boto3.client('servicediscovery', region_name='us-east-1')`)

**Fix**: 
- Verify environment variables in Lambda configuration
- Check IAM role has correct permissions
- **Ensure boto3 clients have explicit region set** - without this, API calls may fail with ServiceNotFound errors
- Manually invoke Lambda and check response

### Issue: ServiceNotFound Error

If Lambda logs show `ServiceNotFound` errors:

1. **Verify Service ID**: The Service ID in Lambda environment variables must match the actual Service Discovery service ID (format: `srv-xxxxxxxxxxxxxxxxx`)
2. **Explicit Region Required**: The boto3 client must explicitly set the region:
   ```python
   servicediscovery = boto3.client('servicediscovery', region_name='us-east-1')
   ```
3. **Region Mismatch**: Ensure Lambda function region matches Service Discovery service region

### Issue: Instance health still UNHEALTHY after Lambda runs

**Check**:
1. ECS task health status: Ensure tasks are actually HEALTHY
2. Instance ID matches task ID (last segment of task ARN)
3. Lambda execution logs to see what happened

**Fix**:
- Wait for next Lambda execution (2 minutes)
- Manually invoke Lambda and check response
- Verify ECS tasks are running and healthy

### Issue: Custom domain still returns 503

**Check**:
1. Service Discovery instance health status (should be HEALTHY)
2. API Gateway integration points to Service Discovery ARN
3. Wait 30-60 seconds for changes to propagate

**Fix**:
- Manually invoke Lambda to force immediate sync
- Wait for Service Discovery DNS to update (TTL is 10 seconds)
- Verify API Gateway routes are using correct integration

## Cost Considerations

### Lambda Costs
- **Executions**: ~720 executions/month (every 2 minutes) = $0.00 (within free tier)
- **Duration**: ~1-2 seconds per execution = ~$0.00/month
- **Total**: Negligible cost

### EventBridge Costs
- **Rules**: 1 rule = $1.00/month (within free tier)
- **Total**: $1.00/month (if exceeding free tier)

## Alternative Solutions Considered

1. **Manual health updates**: Not reliable, doesn't persist
2. **HTTP health checks**: Not supported for private DNS namespaces
3. **Public DNS namespace**: Would work but exposes internal DNS, not recommended
4. **Remove Service Discovery**: Would require using ALB, increasing costs

## Current Status

✅ **Solution Deployed**: Lambda function is running and syncing health status every 2 minutes

✅ **Expected Behavior**: 
- ECS tasks that are HEALTHY → Service Discovery instances marked HEALTHY
- ECS tasks that are UNHEALTHY → Service Discovery instances marked UNHEALTHY
- Custom domain should route correctly once instance is HEALTHY

✅ **Monitoring**: Lambda logs available in CloudWatch for troubleshooting

## Next Steps

1. Monitor Lambda function for 24 hours to ensure stable operation
2. Verify custom domain returns 200 consistently
3. Consider adjusting sync frequency if needed (currently 2 minutes)
4. Document any edge cases discovered in production

