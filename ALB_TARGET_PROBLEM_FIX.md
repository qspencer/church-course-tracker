# ALB Target Problem - Root Cause & Fix

## Problem
ALB target group had stale unhealthy targets that needed manual registration.

## Root Cause
The ECS service was NOT configured to automatically register tasks with the ALB.
- The ALB was created manually (not in Terraform)
- The ECS service was only using Service Discovery, not load balancer integration
- Tasks had to be manually registered with the ALB target group

## Fix Applied

### 1. Added ALB Configuration to Terraform
Created `infrastructure/alb.tf` with:
- ALB security group
- Internal ALB resource
- Target group configuration
- ALB listener

### 2. Updated ECS Service Configuration
Modified `infrastructure/ecs.tf` to add `load_balancer` block to the ECS service:
```hcl
load_balancer {
  target_group_arn = aws_lb_target_group.backend.arn
  container_name   = "backend"
  container_port   = 8000
}
```

### 3. Imported Existing Resources
Imported the manually-created ALB resources into Terraform state:
- ALB
- Target group
- Listener
- Security groups

### 4. Applied Changes
Ran `terraform apply` to update the ECS service configuration.

## Status
- ✅ ECS service now has load balancer configuration
- ✅ Configuration shows correct target group ARN
- ⏳ Waiting for new task deployment to test automatic registration
- ⚠️ Old unhealthy targets need to be manually deregistered (or will timeout)

## Next Steps
1. Force a new deployment of the ECS service
2. Verify automatic task registration with ALB
3. Monitor target health
4. Test API endpoints

## Expected Result
- New ECS tasks will automatically register with the ALB target group
- No more manual target registration needed
- Targets will be healthy and API will work consistently
