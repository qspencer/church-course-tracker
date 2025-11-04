"""
Lambda function to deregister ECS tasks from Service Discovery.

Triggered by EventBridge when an ECS task stops.
Removes the task from Service Discovery.
"""

import json
import os
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients with explicit region
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
servicediscovery = boto3.client('servicediscovery', region_name=AWS_REGION)

# Environment variables
SERVICE_DISCOVERY_SERVICE_ID = os.environ['SERVICE_DISCOVERY_SERVICE_ID']


def extract_task_id(task_arn):
    """
    Extract task ID from task ARN.
    
    Format: arn:aws:ecs:region:account:task/cluster/task-id
    Returns: task-id
    """
    return task_arn.split('/')[-1]


def handler(event, context):
    """
    Main Lambda handler - deregisters ECS task from Service Discovery.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse EventBridge event
        detail = event.get('detail', {})
        task_arn = detail.get('taskArn')
        
        if not task_arn:
            logger.error("No taskArn in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No taskArn in event'})
            }
        
        # Extract task ID (used as instance ID)
        task_id = extract_task_id(task_arn)
        
        logger.info(f"Deregistering task {task_id} from Service Discovery")
        
        # Check if instance exists
        try:
            instance = servicediscovery.get_instance(
                ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
                InstanceId=task_id
            )
            logger.info(f"Found instance {task_id}, proceeding with deregistration")
        except servicediscovery.exceptions.InstanceNotFound:
            logger.warning(f"Instance {task_id} not found in Service Discovery, may already be deregistered")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Instance not found, may already be deregistered', 'instance_id': task_id})
            }
        
        # Deregister instance from Service Discovery
        response = servicediscovery.deregister_instance(
            ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
            InstanceId=task_id
        )
        
        operation_id = response.get('OperationId')
        logger.info(f"Successfully deregistered instance {task_id} from Service Discovery (Operation ID: {operation_id})")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Instance deregistered successfully',
                'instance_id': task_id,
                'operation_id': operation_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error deregistering instance: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


