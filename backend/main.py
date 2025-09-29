"""
Church Course Tracker - Main FastAPI Application
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.csv_loader import load_csv_data_on_startup

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Church Course Tracker API",
    description="A learning management system for church course tracking",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS with comprehensive security headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-API-Key",
        "X-Forwarded-For",
        "X-Real-IP"
    ],
    expose_headers=[
        "X-Total-Count", 
        "X-Page-Count",
        "X-Rate-Limit-Limit",
        "X-Rate-Limit-Remaining",
        "X-Rate-Limit-Reset"
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add comprehensive security headers to all responses"""
    response = await call_next(request)
    
    # Core security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    
    # Content Security Policy
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.planningcenteronline.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    
    # Additional security headers
    response.headers["X-Download-Options"] = "noopen"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    
    # Only add HSTS in production with HTTPS
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    return response

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
    
    return response

# Add rate limiting middleware (enhanced implementation)
if settings.RATE_LIMIT_ENABLED:
    from collections import defaultdict
    import asyncio
    
    # Simple in-memory rate limiter (use Redis in production)
    rate_limit_storage = defaultdict(list)
    
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Enhanced rate limiting middleware with proper headers"""
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        rate_limit_storage[client_ip] = [
            timestamp for timestamp in rate_limit_storage[client_ip]
            if current_time - timestamp < settings.RATE_LIMIT_WINDOW
        ]
        
        # Calculate rate limit info
        remaining_requests = max(0, settings.RATE_LIMIT_REQUESTS - len(rate_limit_storage[client_ip]))
        reset_time = int(current_time + settings.RATE_LIMIT_WINDOW)
        
        # Check rate limit
        if len(rate_limit_storage[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "rate_limit": {
                        "limit": settings.RATE_LIMIT_REQUESTS,
                        "remaining": 0,
                        "reset_time": reset_time,
                        "window": settings.RATE_LIMIT_WINDOW
                    }
                }
            )
            # Add rate limit headers even for blocked requests
            response.headers["X-Rate-Limit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
            response.headers["X-Rate-Limit-Remaining"] = "0"
            response.headers["X-Rate-Limit-Reset"] = str(reset_time)
            response.headers["Retry-After"] = str(settings.RATE_LIMIT_WINDOW)
            return response
        
        # Add current request
        rate_limit_storage[client_ip].append(current_time)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers["X-Rate-Limit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-Rate-Limit-Remaining"] = str(remaining_requests - 1)
        response.headers["X-Rate-Limit-Reset"] = str(reset_time)
        
        return response

# Add trusted host middleware for security (disabled in development)
# Note: Disabled for AWS deployment due to ALB health check issues
# if settings.ENVIRONMENT != "development":
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=settings.ALLOWED_HOSTS
#     )

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    logger.info("Starting Church Course Tracker API...")
    
    # Load CSV data if enabled
    try:
        load_csv_data_on_startup()
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")
    
    logger.info("Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler"""
    logger.info("Shutting down Church Course Tracker API...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Church Course Tracker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from app.core.database import SessionLocal
    from sqlalchemy import text
    import time
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {}
    }
    
    # Database connectivity check
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Application configuration check
    try:
        health_status["checks"]["configuration"] = "healthy"
        health_status["checks"]["cors_origins"] = len(settings.ALLOWED_ORIGINS)
        health_status["checks"]["rate_limiting"] = "enabled" if settings.RATE_LIMIT_ENABLED else "disabled"
    except Exception as e:
        health_status["checks"]["configuration"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Security check
    try:
        health_status["checks"]["security"] = "healthy"
        health_status["checks"]["secret_key_configured"] = bool(settings.SECRET_KEY)
        health_status["checks"]["debug_mode"] = settings.DEBUG
    except Exception as e:
        health_status["checks"]["security"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
