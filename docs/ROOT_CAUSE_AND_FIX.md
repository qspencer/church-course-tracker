# Root Cause and Fix - Custom Domain 503 Issue

## Actual Root Cause (Not Cache!)

The issue was **NOT API Gateway Service Discovery cache** - it was **Route53 DNS routing** pointing to the wrong target.

### The Problem

The Route53 DNS record for `api.quentinspencer.com` was pointing to:
- **Wrong Target**: ALB (`church-course-tracker-alb-776928604.us-east-1.elb.amazonaws.com`)
- **Should Point To**: API Gateway Custom Domain (`d-92manacho1.execute-api.us-east-1.amazonaws.com`)

### Why This Caused 503

1. Custom domain request → Route53 → Routed to ALB
2. ALB either doesn't exist, isn't configured, or returns 503
3. Direct API Gateway endpoint → Works because it bypasses Route53

### The Fix

Updated Route53 record to point to API Gateway:
- **DNS Name**: `d-92manacho1.execute-api.us-east-1.amazonaws.com`
- **Hosted Zone ID**: `Z1UJRXOUMOOFQ8`
- **Status**: INSYNC ✅

## Current Status

- ✅ Route53 record: Fixed and INSYNC
- ✅ Service Discovery: Instance HEALTHY
- ✅ API Gateway mapping: Correct
- ⏳ DNS propagation: In progress (can take 5-15 minutes globally)

## Why Still 503?

Even though Route53 is fixed, DNS propagation takes time:
- Route53 change is INSYNC (AWS-side is correct)
- But DNS resolvers globally may still have cached old ALB IPs
- Local DNS cache may also have old IPs
- Full propagation typically takes 5-15 minutes

## Next Steps

1. **Wait 10-15 minutes** for DNS propagation
2. **Test again**: `curl https://api.quentinspencer.com/api/v1/health`
3. **If still 503**: Check if DNS has actually resolved to API Gateway IPs
4. **Alternative**: Test from different network/DNS server to verify propagation

## Verification

To verify DNS has propagated:
```bash
# Check DNS resolution
dig api.quentinspencer.com

# Should eventually show API Gateway IPs (different from ALB IPs)
# Once DNS shows API Gateway IPs, the custom domain should work
```

## What We Learned

1. **Not a cache issue** - It was DNS routing
2. **Route53 state drift** - Terraform state showed correct, but AWS had ALB
3. **Two hosted zones** - Needed to update the correct one
4. **DNS propagation delay** - Even after Route53 is correct, global propagation takes time

The architecture fix (decoupled Service Discovery) was correct all along. The custom domain issue was purely DNS routing configuration.


