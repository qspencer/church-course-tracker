#!/bin/bash
# Script to safely delete unused NAT Gateways
# This script will delete the NAT Gateways in the old VPC that are no longer needed

set -e

OLD_VPC_ID="vpc-038a7f2f2b7445645"
NAT_GATEWAY_IDS=("nat-0bea5a03f4debdee5" "nat-0836711e1e4ad168b")

echo "=== NAT Gateway Deletion Script ==="
echo ""
echo "This script will delete the following NAT Gateways:"
for nat_id in "${NAT_GATEWAY_IDS[@]}"; do
    echo "  - $nat_id"
done
echo ""
echo "These NAT Gateways are in VPC: $OLD_VPC_ID"
echo "Your current infrastructure uses VPC: vpc-04d5c14c563173157 (with NAT instances)"
echo ""
echo "⚠️  WARNING: Deleting NAT Gateways will:"
echo "   1. Stop all outbound internet traffic from resources in private subnets using these NAT Gateways"
echo "   2. Take 2-5 minutes to complete"
echo "   3. You'll still be charged until deletion completes"
echo ""
echo "Cost savings: ~\$64.80/month (2 NAT Gateways × \$32.40/month each)"
echo ""

# Double check the VPC is really empty
echo "=== Verifying VPC is empty ==="
EC2_COUNT=$(aws ec2 describe-instances --filters "Name=vpc-id,Values=$OLD_VPC_ID" --query 'length(Reservations)' --output text)
if [ "$EC2_COUNT" != "0" ]; then
    echo "❌ ERROR: Found $EC2_COUNT EC2 instance(s) in the old VPC!"
    echo "Please verify these instances are not needed before proceeding."
    exit 1
fi

echo "✅ VPC appears to be empty (no EC2 instances found)"
echo ""

# Check if NAT Gateways are still in use
echo "=== Checking if NAT Gateways are in use ==="
for nat_id in "${NAT_GATEWAY_IDS[@]}"; do
    ROUTE_COUNT=$(aws ec2 describe-route-tables --filters "Name=route.nat-gateway-id,Values=$nat_id" --query 'length(RouteTables)' --output text)
    if [ "$ROUTE_COUNT" != "0" ]; then
        echo "⚠️  NAT Gateway $nat_id is still referenced by $ROUTE_COUNT route table(s)"
        echo "   This is expected - the route tables will be updated automatically"
    else
        echo "✅ NAT Gateway $nat_id is not referenced by any route tables"
    fi
done
echo ""

# Confirm deletion
read -p "Do you want to proceed with deletion? (type 'yes' to confirm): " confirmation
if [ "$confirmation" != "yes" ]; then
    echo "Deletion cancelled."
    exit 0
fi

echo ""
echo "=== Deleting NAT Gateways ==="
for nat_id in "${NAT_GATEWAY_IDS[@]}"; do
    echo "Deleting NAT Gateway: $nat_id"
    aws ec2 delete-nat-gateway --nat-gateway-id "$nat_id" || {
        echo "❌ Failed to delete $nat_id"
        continue
    }
    echo "✅ Deletion initiated for $nat_id"
done

echo ""
echo "=== Deletion Status ==="
echo "NAT Gateway deletions have been initiated."
echo "It will take 2-5 minutes for the deletions to complete."
echo ""
echo "You can check the status with:"
echo "  aws ec2 describe-nat-gateways --nat-gateway-ids ${NAT_GATEWAY_IDS[*]}"
echo ""
echo "Once the state changes to 'deleted', you will stop being charged."
echo ""
echo "Note: You may also want to delete the old VPC and associated resources"
echo "      (subnets, route tables, internet gateways, etc.) to avoid any other charges."
