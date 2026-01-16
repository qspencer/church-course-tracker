#!/bin/bash
# Script to identify and clean up old VPC and associated resources
# This helps remove orphaned AWS resources that are no longer needed

set -e

OLD_VPC_ID="vpc-038a7f2f2b7445645"

echo "=== Old VPC Cleanup Script ==="
echo ""
echo "Target VPC: $OLD_VPC_ID"
echo ""

# Function to check if NAT Gateways are deleted
check_nat_gateways() {
    echo "=== Checking NAT Gateway Status ==="
    NAT_GATEWAYS=$(aws ec2 describe-nat-gateways --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'NatGateways[*].NatGatewayId' --output text 2>/dev/null || echo "")
    
    if [ -n "$NAT_GATEWAYS" ] && [ "$NAT_GATEWAYS" != "None" ]; then
        echo "⚠️  NAT Gateways still exist in this VPC:"
        for nat_id in $NAT_GATEWAYS; do
            STATE=$(aws ec2 describe-nat-gateways --nat-gateway-ids "$nat_id" --query 'NatGateways[0].State' --output text)
            echo "  - $nat_id (State: $STATE)"
        done
        echo ""
        echo "Please wait for NAT Gateways to be fully deleted before cleaning up the VPC."
        return 1
    else
        echo "✅ No NAT Gateways found (or all deleted)"
        return 0
    fi
}

# Function to check for Load Balancers
check_load_balancers() {
    echo "=== Checking Load Balancers ==="
    ALBS=$(aws elbv2 describe-load-balancers --query "LoadBalancers[?VpcId=='$OLD_VPC_ID'].[LoadBalancerName,LoadBalancerArn,State.Code]" --output text 2>/dev/null || echo "")
    
    if [ -n "$ALBS" ] && [ "$ALBS" != "None" ]; then
        echo "⚠️  Load Balancers found in this VPC:"
        echo "$ALBS" | while read -r name arn state; do
            echo "  - $name (State: $state)"
        done
        echo ""
        echo "Load Balancers must be deleted before VPC can be deleted."
        return 1
    else
        echo "✅ No Load Balancers found"
        return 0
    fi
}

# Function to list all resources in the VPC
list_resources() {
    echo "=== Identifying Resources in VPC ==="
    echo ""
    
    # Load Balancers
    echo "Load Balancers:"
    ALBS=$(aws elbv2 describe-load-balancers --query "LoadBalancers[?VpcId=='$OLD_VPC_ID'].[LoadBalancerName,State.Code]" --output table 2>/dev/null || echo "")
    if [ -n "$ALBS" ] && [ "$ALBS" != "None" ]; then
        echo "$ALBS"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # EC2 Instances
    echo "EC2 Instances:"
    EC2_INSTANCES=$(aws ec2 describe-instances --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table)
    if [ -n "$EC2_INSTANCES" ] && [ "$EC2_INSTANCES" != "None" ]; then
        echo "$EC2_INSTANCES"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # RDS Instances
    echo "RDS Instances:"
    RDS_INSTANCES=$(aws rds describe-db-instances --query "DBInstances[?DBSubnetGroup.VpcId=='$OLD_VPC_ID'].[DBInstanceIdentifier,DBInstanceStatus]" --output table 2>/dev/null || echo "")
    if [ -n "$RDS_INSTANCES" ] && [ "$RDS_INSTANCES" != "None" ]; then
        echo "$RDS_INSTANCES"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # Elastic IPs (often associated with NAT Gateways)
    echo "Elastic IPs:"
    EIPS=$(aws ec2 describe-addresses --filters "Name=domain,Values=vpc" --query "Addresses[?NetworkInterfaceId==\`$(aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'NetworkInterfaces[0].NetworkInterfaceId' --output text 2>/dev/null || echo 'none')\`].[PublicIp,AllocationId]" --output table 2>/dev/null || echo "")
    if [ -n "$EIPS" ] && [ "$EIPS" != "None" ]; then
        echo "$EIPS"
    else
        echo "  ✅ None found (or not associated with VPC interfaces)"
    fi
    echo ""
    
    # Network Interfaces
    echo "Network Interfaces:"
    ENIS=$(aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'NetworkInterfaces[*].[NetworkInterfaceId,Status,Description]' --output table)
    if [ -n "$ENIS" ] && [ "$ENIS" != "None" ]; then
        echo "$ENIS"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # Security Groups (excluding default)
    echo "Security Groups:"
    SGS=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'SecurityGroups[?GroupName!=`default`].[GroupId,GroupName,Description]' --output table)
    if [ -n "$SGS" ] && [ "$SGS" != "None" ]; then
        echo "$SGS"
    else
        echo "  ✅ None found (excluding default)"
    fi
    echo ""
    
    # Subnets
    echo "Subnets:"
    SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone]' --output table)
    if [ -n "$SUBNETS" ] && [ "$SUBNETS" != "None" ]; then
        echo "$SUBNETS"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # Route Tables (excluding main)
    echo "Route Tables:"
    RTS=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'RouteTables[?Associations[0].Main!=`true`].[RouteTableId]' --output table)
    if [ -n "$RTS" ] && [ "$RTS" != "None" ]; then
        echo "$RTS"
    else
        echo "  ✅ None found (excluding main route table)"
    fi
    echo ""
    
    # Internet Gateways
    echo "Internet Gateways:"
    IGWS=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$OLD_VPC_ID" --query 'InternetGateways[*].[InternetGatewayId]' --output table)
    if [ -n "$IGWS" ] && [ "$IGWS" != "None" ]; then
        echo "$IGWS"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # VPC Endpoints
    echo "VPC Endpoints:"
    VPC_ENDPOINTS=$(aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'VpcEndpoints[*].[VpcEndpointId,VpcEndpointType,State]' --output table 2>/dev/null || echo "")
    if [ -n "$VPC_ENDPOINTS" ] && [ "$VPC_ENDPOINTS" != "None" ]; then
        echo "$VPC_ENDPOINTS"
    else
        echo "  ✅ None found"
    fi
    echo ""
    
    # VPC Peering Connections
    echo "VPC Peering Connections:"
    PEERING=$(aws ec2 describe-vpc-peering-connections --filters "Name=requester-vpc-info.vpc-id,Values=$OLD_VPC_ID" "Name=accepter-vpc-info.vpc-id,Values=$OLD_VPC_ID" --query 'VpcPeeringConnections[*].[VpcPeeringConnectionId,Status.Code]' --output table 2>/dev/null || echo "")
    if [ -n "$PEERING" ] && [ "$PEERING" != "None" ]; then
        echo "$PEERING"
    else
        echo "  ✅ None found"
    fi
    echo ""
}

# Function to delete resources
delete_resources() {
    echo "=== Deleting Resources ==="
    echo ""
    
    # Delete Load Balancers first (they block VPC deletion)
    echo "Deleting Load Balancers..."
    ALB_ARNS=$(aws elbv2 describe-load-balancers --query "LoadBalancers[?VpcId=='$OLD_VPC_ID'].LoadBalancerArn" --output text 2>/dev/null || echo "")
    if [ -n "$ALB_ARNS" ] && [ "$ALB_ARNS" != "None" ]; then
        for alb_arn in $ALB_ARNS; do
            echo "  Deleting Load Balancer: $alb_arn"
            
            # Delete listeners first
            LISTENER_ARNS=$(aws elbv2 describe-listeners --load-balancer-arn "$alb_arn" --query 'Listeners[*].ListenerArn' --output text 2>/dev/null || echo "")
            if [ -n "$LISTENER_ARNS" ] && [ "$LISTENER_ARNS" != "None" ]; then
                for listener_arn in $LISTENER_ARNS; do
                    echo "    Deleting listener: $listener_arn"
                    aws elbv2 delete-listener --listener-arn "$listener_arn" 2>/dev/null || echo "      ⚠️  Could not delete listener"
                done
            fi
            
            # Delete target groups
            TG_ARNS=$(aws elbv2 describe-target-groups --load-balancer-arn "$alb_arn" --query 'TargetGroups[*].TargetGroupArn' --output text 2>/dev/null || echo "")
            if [ -n "$TG_ARNS" ] && [ "$TG_ARNS" != "None" ]; then
                for tg_arn in $TG_ARNS; do
                    echo "    Deleting target group: $tg_arn"
                    aws elbv2 delete-target-group --target-group-arn "$tg_arn" 2>/dev/null || echo "      ⚠️  Could not delete target group"
                done
            fi
            
            # Delete the load balancer
            aws elbv2 delete-load-balancer --load-balancer-arn "$alb_arn" 2>/dev/null && echo "    ✅ Load balancer deletion initiated" || echo "    ⚠️  Could not delete load balancer"
            echo "    (Note: Load balancer deletion may take a few minutes)"
        done
        echo ""
        echo "⚠️  Waiting 30 seconds for load balancer deletion to propagate..."
        sleep 30
        echo ""
    fi
    
    # Get resource IDs
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'Subnets[*].SubnetId' --output text)
    RT_IDS=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'RouteTables[?Associations[0].Main!=`true`].RouteTableId' --output text)
    IGW_IDS=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$OLD_VPC_ID" --query 'InternetGateways[*].InternetGatewayId' --output text)
    SG_IDS=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text)
    ENI_IDS=$(aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'NetworkInterfaces[*].NetworkInterfaceId' --output text)
    
    # Delete Network Interfaces first (if any)
    if [ -n "$ENI_IDS" ] && [ "$ENI_IDS" != "None" ]; then
        echo "Deleting Network Interfaces..."
        for eni_id in $ENI_IDS; do
            echo "  Deleting $eni_id..."
            aws ec2 delete-network-interface --network-interface-id "$eni_id" 2>/dev/null || echo "    ⚠️  Could not delete (may be in use)"
        done
        echo ""
    fi
    
    # Detach and delete Internet Gateways
    if [ -n "$IGW_IDS" ] && [ "$IGW_IDS" != "None" ]; then
        echo "Detaching and deleting Internet Gateways..."
        for igw_id in $IGW_IDS; do
            echo "  Detaching $igw_id from VPC..."
            aws ec2 detach-internet-gateway --internet-gateway-id "$igw_id" --vpc-id "$OLD_VPC_ID" 2>/dev/null || echo "    ⚠️  Could not detach"
            echo "  Deleting $igw_id..."
            aws ec2 delete-internet-gateway --internet-gateway-id "$igw_id" 2>/dev/null || echo "    ⚠️  Could not delete"
        done
        echo ""
    fi
    
    # Delete Route Tables (non-main)
    if [ -n "$RT_IDS" ] && [ "$RT_IDS" != "None" ]; then
        echo "Deleting Route Tables..."
        for rt_id in $RT_IDS; do
            echo "  Deleting $rt_id..."
            aws ec2 delete-route-table --route-table-id "$rt_id" 2>/dev/null || echo "    ⚠️  Could not delete (may have associations)"
        done
        echo ""
    fi
    
    # Delete Subnets
    if [ -n "$SUBNET_IDS" ] && [ "$SUBNET_IDS" != "None" ]; then
        echo "Deleting Subnets..."
        for subnet_id in $SUBNET_IDS; do
            echo "  Deleting $subnet_id..."
            aws ec2 delete-subnet --subnet-id "$subnet_id" 2>/dev/null || echo "    ⚠️  Could not delete (may have resources)"
        done
        echo ""
    fi
    
    # Delete Security Groups (non-default)
    if [ -n "$SG_IDS" ] && [ "$SG_IDS" != "None" ]; then
        echo "Deleting Security Groups..."
        for sg_id in $SG_IDS; do
            echo "  Deleting $sg_id..."
            aws ec2 delete-security-group --group-id "$sg_id" 2>/dev/null || echo "    ⚠️  Could not delete (may have dependencies)"
        done
        echo ""
    fi
    
    # Finally, delete the VPC
    echo "Deleting VPC: $OLD_VPC_ID"
    aws ec2 delete-vpc --vpc-id "$OLD_VPC_ID" 2>/dev/null && echo "✅ VPC deleted successfully" || echo "❌ Could not delete VPC (may still have resources)"
    echo ""
}

# Main execution
echo "This script will help you clean up the old VPC and its resources."
echo ""

# Check NAT Gateways first
if ! check_nat_gateways; then
    echo ""
    echo "Please wait for NAT Gateways to be deleted first, then run this script again."
    exit 1
fi

echo ""

# Check Load Balancers
if ! check_load_balancers; then
    echo ""
    echo "Load Balancers will be deleted as part of the cleanup process."
fi

echo ""

# List all resources
list_resources

echo ""
echo "=== Summary ==="
echo "The above shows all resources in the VPC."
echo "If you see any resources listed above (other than 'None found'),"
echo "please verify they are not needed before proceeding with deletion."
echo ""

read -p "Do you want to proceed with deletion? (type 'yes' to confirm): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo "Deletion cancelled."
    exit 0
fi

echo ""
delete_resources

echo "=== Cleanup Complete ==="
echo ""
echo "If some resources could not be deleted, they may have dependencies."
echo "Check the error messages above and manually resolve any issues."
echo ""
echo "You can verify the VPC is deleted with:"
echo "  aws ec2 describe-vpcs --vpc-ids $OLD_VPC_ID"
