"""
Lambda function to register ECS tasks with Service Discovery.

Triggered by EventBridge when an ECS task enters RUNNING state.
Registers the task's private IP with Service Discovery.
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
ecs = boto3.client('ecs', region_name=AWS_REGION)
ec2 = boto3.client('ec2', region_name=AWS_REGION)
servicediscovery = boto3.client('servicediscovery', region_name=AWS_REGION)

# Environment variables
SERVICE_DISCOVERY_SERVICE_ID = os.environ['SERVICE_DISCOVERY_SERVICE_ID']
SERVICE_DISCOVERY_PORT = os.environ.get('SERVICE_DISCOVERY_PORT', '8000')


def get_task_private_ip(task_arn, cluster_name):
    """
    Get the private IP address of an ECS task.
    
    Args:
        task_arn: ECS task ARN
        cluster_name: ECS cluster name
    
    Returns:
        Private IP address string
    """
    try:
        # Describe the task to get network interface details
        response = ecs.describe_tasks(
            cluster=cluster_name,
            tasks=[task_arn]
        )
        
        if not response.get('tasks'):
            raise ValueError(f"Task {task_arn} not found")
        
        task = response['tasks'][0]
        
        # Get network interface ID from task attachments
        network_interface_id = None
        for attachment in task.get('attachments', []):
            for detail in attachment.get('details', []):
                if detail.get('name') == 'networkInterfaceId':
                    network_interface_id = detail.get('value')
                    break
            if network_interface_id:
                break
        
        if not network_interface_id:
            raise ValueError(f"No network interface found for task {task_arn}")
        
        # Get private IP from network interface
        ni_response = ec2.describe_network_interfaces(
            NetworkInterfaceIds=[network_interface_id]
        )
        
        if not ni_response.get('NetworkInterfaces'):
            raise ValueError(f"Network interface {network_interface_id} not found")
        
        private_ip = ni_response['NetworkInterfaces'][0].get('PrivateIpAddress')
        
        if not private_ip:
            raise ValueError(f"No private IP found for network interface {network_interface_id}")
        
        return private_ip
        
    except Exception as e:
        logger.error(f"Error getting task private IP: {str(e)}")
        raise


def extract_task_id(task_arn):
    """
    Extract task ID from task ARN.
    
    Format: arn:aws:ecs:region:account:task/cluster/task-id
    Returns: task-id
    """
    return task_arn.split('/')[-1]


def handler(event, context):
    """
    Main Lambda handler - registers ECS task with Service Discovery.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse EventBridge event
        detail = event.get('detail', {})
        task_arn = detail.get('taskArn')
        cluster_arn = detail.get('clusterArn')
        cluster_name = cluster_arn.split('/')[-1] if cluster_arn else None
        
        if not task_arn:
            logger.error("No taskArn in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No taskArn in event'})
            }
        
        if not cluster_name:
            logger.error("No clusterArn in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No clusterArn in event'})
            }
        
        logger.info(f"Registering task {task_arn} with Service Discovery")
        
        # Extract task ID (used as instance ID)
        task_id = extract_task_id(task_arn)
        
        # Check if instance already exists
        try:
            existing = servicediscovery.get_instance(
                ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
                InstanceId=task_id
            )
            logger.info(f"Instance {task_id} already exists, skipping registration")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Instance already registered', 'instance_id': task_id})
            }
        except servicediscovery.exceptions.InstanceNotFound:
            # Instance doesn't exist, proceed with registration
            pass
        
        # Get task's private IP address
        private_ip = get_task_private_ip(task_arn, cluster_name)
        logger.info(f"Task {task_id} has private IP: {private_ip}")
        
        # Register instance with Service Discovery
        # CRITICAL: Set AWS_INIT_HEALTH_STATUS to HEALTHY during registration
        # This tells Service Discovery to treat the instance as HEALTHY immediately,
        # which allows API Gateway to route to it right away
        response = servicediscovery.register_instance(
            ServiceId=SERVICE_DISCOVERY_SERVICE_ID,
            InstanceId=task_id,
            Attributes={
                'AWS_INSTANCE_IPV4': private_ip,
                'AWS_INSTANCE_PORT': SERVICE_DISCOVERY_PORT,
                'AWS_INIT_HEALTH_STATUS': 'HEALTHY',  # CRITICAL: Set health status at registration
                'ECS_CLUSTER_NAME': cluster_name,
                'ECS_TASK_ARN': task_arn
            }
        )
        
        operation_id = response.get('OperationId')
        logger.info(f"Successfully registered instance {task_id} with Service Discovery (Operation ID: {operation_id})")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Instance registered successfully',
                'instance_id': task_id,
                'private_ip': private_ip,
                'operation_id': operation_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error registering instance: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

