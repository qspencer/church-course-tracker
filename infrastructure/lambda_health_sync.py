"""
Lambda function to sync ECS task health status to Service Discovery instances.

This function:
1. Lists all running ECS tasks for the service
2. Checks their health status
3. Finds corresponding Service Discovery instances
4. Updates Service Discovery instance health status to match ECS task health
"""

import json
import os
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients with explicit region
# Use Lambda's execution region (us-east-1)
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
ecs = boto3.client('ecs', region_name=AWS_REGION)
servicediscovery = boto3.client('servicediscovery', region_name=AWS_REGION)

# Get environment variables
SERVICE_DISCOVERY_SERVICE_ID = os.environ['SERVICE_DISCOVERY_SERVICE_ID']
ECS_CLUSTER = os.environ['ECS_CLUSTER']
ECS_SERVICE = os.environ['ECS_SERVICE']


def handler(event, context):
    """
    Main Lambda handler
    """
    try:
        logger.info(f"Starting health sync for ECS service: {ECS_SERVICE}")
        
        # Get all running tasks for the ECS service
        tasks_response = ecs.list_tasks(
            cluster=ECS_CLUSTER,
            serviceName=ECS_SERVICE,
            desiredStatus='RUNNING'
        )
        
        task_arns = tasks_response.get('taskArns', [])
        
        if not task_arns:
            logger.warning("No running tasks found")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No running tasks'})
            }
        
        logger.info(f"Found {len(task_arns)} running task(s)")
        
        # Describe tasks to get health status
        tasks_details = ecs.describe_tasks(
            cluster=ECS_CLUSTER,
            tasks=task_arns
        )
        
        # Get Service Discovery instances
        instances_response = servicediscovery.list_instances(
            ServiceId=SERVICE_DISCOVERY_SERVICE_ID
        )
        
        instances = instances_response.get('Instances', [])
        logger.info(f"Found {len(instances)} Service Discovery instance(s)")
        
        # Create mapping of task ARN to task details
        task_map = {}
        for task in tasks_details.get('tasks', []):
            task_arn = task.get('taskArn', '')
            # Extract task ID from ARN (last segment after /)
            task_id = task_arn.split('/')[-1] if task_arn else ''
            task_map[task_id] = {
                'arn': task_arn,
                'health': task.get('healthStatus', 'UNKNOWN'),
                'status': task.get('lastStatus', 'UNKNOWN')
            }
        
        # Update Service Discovery instance health based on ECS task health
        updated_count = 0
        for instance in instances:
            instance_id = instance.get('Id', '')
            current_health = instance.get('Attributes', {}).get('AWS_INIT_HEALTH_STATUS', 'UNKNOWN')
            
            # Find matching ECS task by instance ID (instance ID = task ID)
            if instance_id in task_map:
                task_info = task_map[instance_id]
                task_health = task_info['health']
                task_status = task_info['status']
                
                # Map ECS health to Service Discovery health
                if task_health == 'HEALTHY' and task_status == 'RUNNING':
                    target_health = 'HEALTHY'
                elif task_health == 'UNHEALTHY' or task_status != 'RUNNING':
                    target_health = 'UNHEALTHY'
                else:
                    target_health = 'UNHEALTHY'  # Default to UNHEALTHY for UNKNOWN
            
                # Only update if health status needs to change
                if current_health != target_health:
                    try:
                        logger.info(f"Attempting to update instance {instance_id} from {current_health} to {target_health}")
                        logger.info(f"Using Service ID: {SERVICE_DISCOVERY_SERVICE_ID}, Region: {AWS_REGION}")
                        
                        response = servicediscovery.update_instance_custom_health_status(
                            ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
                            InstanceId=instance_id,
                            Status=target_health
                        )
                        logger.info(f"Successfully updated instance {instance_id} from {current_health} to {target_health} (task health: {task_health}, status: {task_status})")
                        logger.info(f"API Response: {json.dumps(response)}")
                        updated_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update instance {instance_id}: {str(e)}")
                        logger.error(f"Service ID used: {SERVICE_DISCOVERY_SERVICE_ID}")
                        logger.error(f"Instance ID used: {instance_id}")
                        logger.error(f"Region: {AWS_REGION}")
                        logger.error(f"Exception type: {type(e).__name__}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                else:
                    logger.debug(f"Instance {instance_id} health already correct: {current_health}")
            else:
                logger.warning(f"No matching ECS task found for instance {instance_id}")
        
        result = {
            'statusCode': 200,
            'message': f'Health sync completed. Updated {updated_count} instance(s)',
            'tasks_checked': len(task_arns),
            'instances_checked': len(instances),
            'instances_updated': updated_count
        }
        
        logger.info(json.dumps(result))
        return result
        
    except Exception as e:
        logger.error(f"Error in health sync: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

