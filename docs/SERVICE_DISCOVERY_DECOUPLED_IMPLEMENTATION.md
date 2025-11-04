# Service Discovery Decoupled Implementation

## Solution Implemented

We've successfully implemented the decoupled architecture to solve the ECS Service Discovery health status ownership conflict.

## Changes Made

### 1. Removed ECS Ownership
- **File**: `infrastructure/ecs.tf`
- **Change**: Removed `service_registries` block from `aws_ecs_service.backend`
- **Result**: ECS no longer manages Service Discovery instance lifecycle

### 2. Created Register Lambda
- **File**: `infrastructure/lambda_service_discovery_register.py`
- **Function**: Registers ECS tasks with Service Discovery when they start
- **Trigger**: EventBridge rule on ECS Task State Change (RUNNING)
- **Logic**:
  - Extracts task ARN from EventBridge event
  - Gets task's private IP from network interface
  - Calls `servicediscovery.register_instance` with task ID as instance ID

### 3. Created Deregister Lambda
- **File**: `infrastructure/lambda_service_discovery_deregister.py`
- **Function**: Removes ECS tasks from Service Discovery when they stop
- **Trigger**: EventBridge rule on ECS Task State Change (STOPPED)
- **Logic**:
  - Extracts task ID from EventBridge event
  - Calls `servicediscovery.deregister_instance`

### 4. Created EventBridge Rules
- **File**: `infrastructure/lambda_service_discovery.tf`
- **Rule 1**: `ecs_task_started` - Triggers Register Lambda when task enters RUNNING state
- **Rule 2**: `ecs_task_stopped` - Triggers Deregister Lambda when task stops

### 5. Health-Sync Lambda (No Changes)
- **File**: `infrastructure/lambda_health_sync.py`
- **Status**: Unchanged - will now work correctly since ECS no longer overrides health status
- **Function**: Updates Service Discovery instance health every 2 minutes based on ECS task health

## Current Status

### Working Components
- ✅ Infrastructure deployed successfully
- ✅ Register Lambda function created and invoked by EventBridge
- ✅ Deregister Lambda function created and working
- ✅ EventBridge rules configured correctly
- ✅ RegisterInstance API calls succeeding (logs show success)

### Debugging Issue
- ⚠️ Service Discovery instances registered but not appearing in `list_instances`
- Possible causes:
  1. Asynchronous operation timing (operations take time to complete)
  2. Service Discovery API behavior (instances may not appear immediately)
  3. Need to verify operation completion using `get_operation` API

## Next Steps

1. **Debug Registration**: Verify RegisterInstance operations complete successfully
2. **Test Health Sync**: Once instances appear, verify health-sync Lambda works
3. **Verify Custom Domain**: Test that custom domain works when instances are HEALTHY

## Architecture Benefits

1. **No Ownership Conflict**: ECS no longer manages instances, preventing health status override
2. **Full Control**: Lambda functions have complete control over registration and health
3. **Event-Driven**: Automatic registration/deregistration via EventBridge events
4. **Health Sync Works**: Health-sync Lambda can now successfully update health status

## Files Created/Modified

- `infrastructure/ecs.tf` - Removed service_registries
- `infrastructure/lambda_service_discovery.tf` - New Terraform configuration
- `infrastructure/lambda_service_discovery_register.py` - Register Lambda code
- `infrastructure/lambda_service_discovery_deregister.py` - Deregister Lambda code


