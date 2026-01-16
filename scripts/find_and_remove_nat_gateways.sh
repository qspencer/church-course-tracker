#!/bin/bash
# Script to find and optionally remove unused NAT Gateways
# This helps identify NAT Gateways that are costing money even when not in use

set -e

echo "=== Finding NAT Gateways in your AWS account ==="
echo ""

# Get all NAT Gateways
NAT_GATEWAYS=$(aws ec2 describe-nat-gateways --query 'NatGateways[*].[NatGatewayId,State,SubnetId,VpcId,Tags[?Key==`Name`].Value|[0],Tags[?Key==`Application`].Value|[0]]' --output table)

if [ -z "$NAT_GATEWAYS" ] || [ "$NAT_GATEWAYS" = "None" ]; then
    echo "No NAT Gateways found in your account."
    exit 0
fi

echo "Found NAT Gateways:"
echo "$NAT_GATEWAYS"
echo ""

# Get detailed information
echo "=== Detailed NAT Gateway Information ==="
aws ec2 describe-nat-gateways --query 'NatGateways[*].{
    ID:NatGatewayId,
    State:State,
    Subnet:SubnetId,
    VPC:VpcId,
    Created:CreateTime,
    Tags:Tags
}' --output json | jq '.'

echo ""
echo "=== Checking Route Tables ==="
echo "Checking which route tables are using these NAT Gateways..."
echo ""

# Get all route tables and check for NAT Gateway routes
NAT_IDS=$(aws ec2 describe-nat-gateways --query 'NatGateways[*].NatGatewayId' --output text)

for NAT_ID in $NAT_IDS; do
    echo "Checking routes for NAT Gateway: $NAT_ID"
    ROUTE_TABLES=$(aws ec2 describe-route-tables --filters "Name=route.nat-gateway-id,Values=$NAT_ID" --query 'RouteTables[*].[RouteTableId,Associations[*].SubnetId]' --output table)
    
    if [ -z "$ROUTE_TABLES" ] || [ "$ROUTE_TABLES" = "None" ]; then
        echo "  ⚠️  WARNING: NAT Gateway $NAT_ID is NOT being used by any route tables!"
        echo "  This NAT Gateway is costing you money but not being used."
    else
        echo "  Route tables using this NAT Gateway:"
        echo "$ROUTE_TABLES"
    fi
    echo ""
done

echo "=== Cost Information ==="
echo "NAT Gateways are charged:"
echo "  - \$0.045 per hour (approximately \$32.40 per month) per NAT Gateway"
echo "  - Plus \$0.045 per GB of data processed"
echo ""
echo "Even if a NAT Gateway processes 0 GB of data, you still pay the hourly charge."
echo ""

# Ask if user wants to delete unused NAT Gateways
echo "=== Next Steps ==="
echo "To delete a NAT Gateway that's not being used:"
echo ""
echo "1. First, verify it's not needed by checking:"
echo "   - Is it associated with any route tables? (shown above)"
echo "   - Are there any resources in private subnets that need internet access?"
echo ""
echo "2. If you're sure it's not needed, delete it with:"
echo "   aws ec2 delete-nat-gateway --nat-gateway-id <NAT_GATEWAY_ID>"
echo ""
echo "3. Note: Deleting a NAT Gateway takes a few minutes. You'll still be charged"
echo "   until the deletion is complete."
echo ""
echo "Would you like to see a command to delete unused NAT Gateways? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "=== Unused NAT Gateways (not in any route tables) ==="
    UNUSED_NATS=$(aws ec2 describe-nat-gateways --query 'NatGateways[*].NatGatewayId' --output text)
    
    for NAT_ID in $UNUSED_NATS; do
        ROUTE_COUNT=$(aws ec2 describe-route-tables --filters "Name=route.nat-gateway-id,Values=$NAT_ID" --query 'length(RouteTables)' --output text)
        if [ "$ROUTE_COUNT" = "0" ]; then
            STATE=$(aws ec2 describe-nat-gateways --nat-gateway-ids "$NAT_ID" --query 'NatGateways[0].State' --output text)
            if [ "$STATE" = "available" ]; then
                echo "aws ec2 delete-nat-gateway --nat-gateway-id $NAT_ID"
            fi
        fi
    done
fi
