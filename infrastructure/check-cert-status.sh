#!/bin/bash
# Quick script to check certificate status
# Usage: ./check-cert-status.sh

CERT_ARN="arn:aws:acm:us-east-1:334581603621:certificate/78e18b2c-69c8-4e4a-b8c6-e35e5d865b70"
REGION="us-east-1"

echo "Checking certificate status..."
STATUS=$(aws acm describe-certificate \
    --certificate-arn "$CERT_ARN" \
    --region "$REGION" \
    --query 'Certificate.Status' \
    --output text 2>&1)

echo ""
echo "Certificate Status: $STATUS"
echo ""

if [ "$STATUS" = "ISSUED" ]; then
    echo "✅ Certificate is validated! You can now run:"
    echo "   cd infrastructure && terraform apply -auto-approve"
elif [ "$STATUS" = "PENDING_VALIDATION" ]; then
    echo "⏳ Certificate is still validating..."
    echo "   The wait-and-deploy-docs.sh script is monitoring this."
    echo "   Or check again in a few minutes."
else
    echo "⚠️  Certificate status: $STATUS"
fi

