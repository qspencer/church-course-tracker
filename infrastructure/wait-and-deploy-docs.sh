#!/bin/bash
# wait-and-deploy-docs.sh
# Waits for ACM certificate validation to complete, then deploys CloudFront and Route 53

set -e

CERT_ARN="arn:aws:acm:us-east-1:334581603621:certificate/f4429c94-2aa0-48de-aa09-c5ae560d6a99"
REGION="us-east-1"
CHECK_INTERVAL=30  # Check every 30 seconds
MAX_WAIT_MINUTES=180  # Maximum wait time in minutes (3 hours - ACM can take up to 72 hours)
MAX_CHECKS=$((MAX_WAIT_MINUTES * 60 / CHECK_INTERVAL))

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/wait-and-deploy-docs.log"

# Redirect all output to log file and stdout
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🔍 Monitoring ACM Certificate Validation"
echo "   Log file: $LOG_FILE"
echo "   Certificate ARN: $CERT_ARN"
echo "   Check interval: ${CHECK_INTERVAL} seconds"
echo "   Max wait time: ${MAX_WAIT_MINUTES} minutes"
echo ""

check_count=0
while [ $check_count -lt $MAX_CHECKS ]; do
    check_count=$((check_count + 1))
    
    # Get certificate status
    STATUS=$(aws acm describe-certificate \
        --certificate-arn "$CERT_ARN" \
        --region "$REGION" \
        --query 'Certificate.Status' \
        --output text 2>&1)
    
    # Check if command succeeded
    if [ $? -ne 0 ]; then
        echo "❌ Error checking certificate status: $STATUS"
        exit 1
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Check #${check_count}: Status = $STATUS"
    
    # Check if certificate is issued
    if [ "$STATUS" = "ISSUED" ]; then
        echo ""
        echo "✅ Certificate validated! Status: $STATUS"
        echo ""
        echo "🚀 Proceeding with Terraform deployment..."
        echo ""
        
        # Run terraform apply
        terraform apply -auto-approve
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 Deployment complete!"
            echo ""
            echo "📋 Summary:"
            terraform output -json | jq -r '
                if .docs_s3_bucket then "   S3 Bucket: \(.docs_s3_bucket.value)" else "" end,
                if .docs_cloudfront_distribution_id then "   CloudFront Distribution ID: \(.docs_cloudfront_distribution_id.value)" else "" end,
                if .docs_cloudfront_domain then "   CloudFront Domain: \(.docs_cloudfront_domain.value)" else "" end,
                if .docs_url then "   Documentation URL: \(.docs_url.value)" else "" end
            ' 2>/dev/null || echo "   Run 'terraform output' to see deployment details"
            echo ""
            echo "⏱️  Note: CloudFront distribution may take 10-15 minutes to fully deploy"
            echo "   DNS propagation may take 5-60 minutes"
            echo ""
            exit 0
        else
            echo ""
            echo "❌ Terraform apply failed. Please check the errors above."
            exit 1
        fi
    elif [ "$STATUS" = "FAILED" ] || [ "$STATUS" = "VALIDATION_TIMED_OUT" ]; then
        echo ""
        echo "❌ Certificate validation failed or timed out. Status: $STATUS"
        echo "   Please check the certificate in AWS Console and try again."
        exit 1
    fi
    
    # Wait before next check
    if [ $check_count -lt $MAX_CHECKS ]; then
        sleep $CHECK_INTERVAL
    fi
done

echo ""
echo "⏱️  Maximum wait time (${MAX_WAIT_MINUTES} minutes) exceeded"
echo "   Certificate is still in status: $STATUS"
echo ""
echo "💡 You can:"
echo "   1. Continue waiting manually and run: terraform apply"
echo "   2. Check certificate status:"
echo "      aws acm describe-certificate --certificate-arn $CERT_ARN --region $REGION --query 'Certificate.Status' --output text"
echo ""
exit 1

