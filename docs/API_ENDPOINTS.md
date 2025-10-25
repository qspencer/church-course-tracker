# Church Course Tracker API Endpoints

## Working Endpoints

- **Direct API Gateway URL**: https://tinev5iszf.execute-api.us-east-1.amazonaws.com
- **Custom Domain (503 error)**: https://api.quentinspencer.com

## Health Check

```bash
curl https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health
```

## Status

- ✅ Backend is running and healthy
- ✅ ECS health checks passing  
- ✅ ALB targets healthy
- ❌ Custom domain returning 503 errors
- ✅ Direct API Gateway URL working perfectly

## Troubleshooting Completed (October 25, 2025)

1. ✅ Documented execute-api URL
2. ❌ Custom domain API mapping configuration issue
3. ✅ DNS propagating correctly from all locations
4. ⚠️ Terraform state needs manual sync for API mapping

### Root Cause Analysis
- API Gateway direct URL works perfectly
- Custom domain has API mapping but returns 503
- Terraform state has stale API mapping ID reference
- Multiple API mapping deletion/recreation attempts may have caused state drift

### Next Steps
- Use direct execute-api URL for production (works perfectly)
- Investigate API Gateway custom domain caching issues
- Consider disabling AutoDeploy and manually managing deployments
