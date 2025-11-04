# Service Discovery Health Status Problem Summary

## What We're Trying To Do

We're implementing a serverless architecture for a church course tracking application where the backend API runs on AWS ECS Fargate containers in private subnets, accessible via API Gateway HTTP API with a custom domain (`api.quentinspencer.com`). To enable API Gateway to route requests to ECS tasks without a load balancer (to save costs), we're using AWS Service Discovery with a private DNS namespace. ECS automatically registers each running task as a Service Discovery instance, and API Gateway uses the Service Discovery service ARN as its integration endpoint. This allows API Gateway to dynamically discover and route to healthy backend instances via a VPC Link, creating a cost-effective alternative to an Application Load Balancer (~$15/month savings).

## The Problem

The Service Discovery instance remains in an `UNHEALTHY` status despite the ECS task being `HEALTHY`, causing API Gateway to return 503 errors when accessed via the custom domain. This occurs because API Gateway respects Service Discovery health filtering and only routes to `HEALTHY` instances. Here are the key technical details:

**Infrastructure Configuration:**
- ECS tasks use `awsvpc` network mode with container health checks configured (`curl -f http://localhost:8000/health`)
- Service Discovery service uses `HealthCheckCustomConfig` (required for private DNS namespaces - HTTP health checks are not supported)
- ECS service has `service_registries` configured to auto-register tasks with Service Discovery
- API Gateway integration uses Service Discovery service ARN (`arn:aws:servicediscovery:...`)
- Custom domain maps to API Gateway with routes pointing to the Service Discovery integration

**Observed Behavior:**
- ECS task health status: `HEALTHY` (confirmed via `ecs describe-tasks`, running for 4+ hours)
- Service Discovery instance health status: `UNHEALTHY` (persists despite multiple update attempts)
- Direct API Gateway endpoint: Returns 200 OK (works correctly)
- Custom domain endpoint: Returns 503 (blocked by UNHEALTHY Service Discovery filtering)

**Attempted Solutions:**
1. Created Lambda function to sync ECS task health to Service Discovery every 2 minutes using `update_instance_custom_health_status` API
2. Lambda successfully calls the API (no errors, returns success)
3. However, status immediately reverts to `UNHEALTHY` after update
4. Verified API calls use correct Service ID, Instance ID, and region (`us-east-1`)
5. Forced ECS service update to trigger re-registration - new instance also starts as `UNHEALTHY`
6. Waited 4+ hours for ECS to naturally sync health - no change observed

**Root Cause Hypothesis:**
AWS documentation states that ECS automatically syncs container health status to Service Discovery when using `HealthCheckCustomConfig`, but this is not occurring. Additionally, manual updates via `update_instance_custom_health_status` API succeed but don't persist - they're immediately overridden, likely by ECS's own health management cycle. This suggests that when ECS manages Service Discovery registration via `service_registries`, ECS may be continuously resetting the health status based on its own internal logic, which may not be correctly syncing the container health check status to the Service Discovery instance health attribute. The `update_instance_custom_health_status` API appears to be designed for application-managed health checks, not ECS-managed instances, leading to a conflict where ECS overwrites manual updates.

**Impact:**
The custom domain (`api.quentinspencer.com`) cannot route requests to the backend, though the direct API Gateway endpoint works perfectly. This creates a user experience issue and prevents the use of the clean custom domain URL.


