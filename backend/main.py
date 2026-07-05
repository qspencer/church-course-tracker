"""
Church Course Tracker - Main FastAPI Application
Triggering backend tests
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import time
import logging

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.csv_loader import load_csv_data_on_startup
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.exceptions import ValidationError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager (replaces deprecated on_event)"""
    # Startup
    logger.info("Starting Church Course Tracker API...")
    
    # Ensure admin user exists
    try:
        ensure_admin_user()
    except Exception as e:
        logger.error(f"Error ensuring admin user: {e}")
    
    # Load CSV data if enabled
    try:
        load_csv_data_on_startup()
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Church Course Tracker API...")


# Create FastAPI application
# Disable redirect_slashes to prevent redirect issues through API Gateway
# API Gateway may misinterpret redirects and cause HTTPS->HTTP downgrades
app = FastAPI(
    title="Church Course Tracker API",
    description="A learning management system for church course tracking",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    redirect_slashes=False,  # Disable to prevent redirect issues
    lifespan=lifespan,
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
        "X-Real-IP",
        "sentry-trace",
        "baggage",
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
    
    # Content Security Policy. This header is on API responses, not the SPA
    # (which is served from CloudFront). In production the API serves only
    # JSON - no script/style executes from these responses - so we omit the
    # unsafe-inline/unsafe-eval that the dev-only Swagger UI needs.
    if settings.ENVIRONMENT == "production":
        script_src = "script-src 'self'"
        style_src = "style-src 'self'"
    else:
        # Swagger UI / ReDoc (mounted only outside production) need inline
        # script and style to render.
        script_src = "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
        style_src = "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
    csp_policy = (
        "default-src 'self'; "
        f"{script_src}; "
        f"{style_src}; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.quentinspencer.com https://api.planningcenteronline.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    
    # Additional security headers
    response.headers["X-Download-Options"] = "noopen"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    # NOTE: Removed Cross-Origin-Embedder-Policy and Cross-Origin-Resource-Policy
    # These headers block cross-origin requests, which we need for API access
    # from apps.quentinspencer.com to api.quentinspencer.com
    # Cross-Origin-Opener-Policy is safe for APIs
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    
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
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.4f}s")
        
        # Ensure CORS headers are present on all responses (including errors)
        origin = request.headers.get("origin")
        if origin and origin in settings.ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    except Exception as e:
        # Log unhandled exceptions
        process_time = time.time() - start_time
        error_message = str(e) if e else "Unknown error"
        logger.error(f"Unhandled exception in {request.method} {request.url.path}: {error_message}", exc_info=True)
        
        # Return error response with CORS headers
        # Ensure error_message is a string, not an exception object
        safe_error_message = str(error_message) if error_message else "Unknown error"
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Internal server error: {safe_error_message}",
                "status_code": 500,
            },
        )
        origin = request.headers.get("origin")
        if origin and origin in settings.ALLOWED_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

# Add rate limiting middleware (enhanced implementation)
if settings.RATE_LIMIT_ENABLED:
    from collections import defaultdict
    import asyncio
    
    # Simple in-memory rate limiter. Per-process only: with a single Fargate
    # task this is exact; if desired_count ever grows, each task enforces the
    # limit independently (move to Redis/ElastiCache at that point).
    rate_limit_storage = defaultdict(list)
    request_counter = {"n": 0}

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Enhanced rate limiting middleware with proper headers"""
        # API Gateway appends the real client IP as the LAST entry of
        # X-Forwarded-For. Never use the first entry: it is attacker-
        # controlled (a client can send a fresh fake XFF per request and
        # bypass the limiter entirely).
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[-1].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Periodically sweep the whole store so keys for one-off clients
        # don't accumulate forever (previously a slow memory leak).
        request_counter["n"] += 1
        if request_counter["n"] % 1000 == 0:
            stale = [
                ip
                for ip, timestamps in rate_limit_storage.items()
                if not timestamps
                or current_time - timestamps[-1] >= settings.RATE_LIMIT_WINDOW
            ]
            for ip in stale:
                del rate_limit_storage[ip]

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

# Register exception handlers BEFORE including routers to ensure they're used
# This ensures our custom handlers take precedence over FastAPI defaults

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Custom exception handlers for consistent error responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent JSON format"""
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail if exc.detail else "An error occurred",
            "status_code": exc.status_code,
        },
        headers=getattr(exc, "headers", None) or {},
    )
    # Ensure CORS headers are added to error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with consistent JSON format"""
    response = JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": f"Resource not found: {request.url.path}",
            "status_code": 404,
        },
    )
    # Ensure CORS headers are added to error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


def make_serializable(obj, _seen=None):
    """Recursively convert non-serializable objects to strings"""
    if _seen is None:
        _seen = set()
    
    # Handle circular references
    obj_id = id(obj)
    if obj_id in _seen:
        return "<circular reference>"
    _seen.add(obj_id)
    
    try:
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                result[k] = make_serializable(v, _seen)
            _seen.remove(obj_id)
            return result
        elif isinstance(obj, list):
            result = [make_serializable(item, _seen) for item in obj]
            _seen.remove(obj_id)
            return result
        elif isinstance(obj, (str, int, float, bool, type(None))):
            _seen.remove(obj_id)
            return obj
        else:
            # For any other type, try to serialize or convert to string
            try:
                import json
                json.dumps(obj)
                _seen.remove(obj_id)
                return obj
            except (TypeError, ValueError, AttributeError):
                _seen.remove(obj_id)
                return str(obj)
    except Exception:
        _seen.discard(obj_id)
        return str(obj)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    logger.info(f"Validation error handler called for {request.url.path}")
    
    # Ensure errors() returns a list that can be JSON serialized
    serializable_errors = []
    try:
        errors = exc.errors()
        logger.debug(f"Validation errors: {len(errors)} errors found")
        # Recursively make all values serializable
        serializable_errors = make_serializable(errors)
        # Double-check serialization
        import json
        json.dumps(serializable_errors)
        logger.debug("Validation errors successfully serialized")
    except Exception as e:
        # Fallback if errors() fails or serialization fails
        error_msg = str(e) if e else "Unknown validation error"
        logger.error(f"Error processing validation errors: {error_msg}", exc_info=True)
        serializable_errors = [{"msg": "Validation error", "detail": error_msg}]
    
    # Create response with safe content
    try:
        response = JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": serializable_errors,
                "status_code": 422,
                "message": "Validation error",
            },
        )
        logger.debug("Validation error JSONResponse created successfully")
    except Exception as json_error:
        # If JSONResponse creation fails, use fallback
        logger.error(f"Failed to create validation error JSONResponse: {json_error}", exc_info=True)
        from fastapi.responses import Response
        response = Response(
            content='{"detail": "Validation error", "status_code": 422}',
            status_code=422,
            media_type="application/json"
        )
    
    # Ensure CORS headers are added to error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(ValidationError)
async def custom_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle custom ValidationError with 400 Bad Request"""
    logger.warning(f"Validation error on {request.url.path}: {str(exc)}")

    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "status_code": 400,
            "message": "Validation failed",
        },
    )

    # Ensure CORS headers are added to error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


# Global exception handler for all unhandled exceptions
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with CORS headers"""
    # Safely convert exception to string
    try:
        error_message = str(exc) if exc else "Unknown error"
    except Exception:
        error_message = "Unknown error (could not convert exception to string)"
    
    logger.error(f"Unhandled exception: {error_message}", exc_info=True)
    
    # Create response with safe, serializable content
    try:
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Internal server error: {error_message}",
                "status_code": 500,
            },
        )
    except Exception as json_error:
        # If JSONResponse creation fails, create a simple text response
        logger.error(f"Failed to create JSONResponse: {json_error}")
        from fastapi.responses import Response
        response = Response(
            content=f'{{"detail": "Internal server error: {error_message}", "status_code": 500}}',
            status_code=500,
            media_type="application/json"
        )
    
    # Ensure CORS headers are added to error responses
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Accept, Accept-Language, Authorization, Content-Language, Content-Type, X-API-Key, X-CSRF-Token, X-Forwarded-For, X-Real-IP, X-Requested-With"
    return response


def ensure_default_users():
    """Ensure all default users exist in the database (idempotent)"""
    db = SessionLocal()
    try:
        # Define all default users from settings
        default_users = [
            {
                "username": settings.ADMIN_USERNAME,
                "email": settings.ADMIN_EMAIL,
                "password": settings.ADMIN_PASSWORD,
                "full_name": settings.ADMIN_FULL_NAME,
                "role": "admin"
            },
            {
                "username": settings.STAFF_USERNAME,
                "email": settings.STAFF_EMAIL,
                "password": settings.STAFF_PASSWORD,
                "full_name": settings.STAFF_FULL_NAME,
                "role": "staff"
            },
            {
                "username": settings.INSTRUCTOR_USERNAME,
                "email": settings.INSTRUCTOR_EMAIL,
                "password": settings.INSTRUCTOR_PASSWORD,
                "full_name": settings.INSTRUCTOR_FULL_NAME,
                "role": "instructor"
            },
            {
                "username": settings.VIEWER_USERNAME,
                "email": settings.VIEWER_EMAIL,
                "password": settings.VIEWER_PASSWORD,
                "full_name": settings.VIEWER_FULL_NAME,
                "role": "viewer"
            }
        ]

        is_production = settings.ENVIRONMENT == "production"

        for user_data in default_users:
            # In production, never create an account whose password is the
            # publicly known dev placeholder. ADMIN_PASSWORD is already
            # hard-blocked at config load; this closes the same hole for
            # the staff/instructor/viewer seeds on a fresh database.
            if (
                is_production
                and user_data["password"] == settings.DEV_PASSWORD_PLACEHOLDER
            ):
                logger.warning(
                    "Skipping seed user '%s': its password is the dev "
                    "placeholder. Set %s_PASSWORD to a real value to seed it.",
                    user_data["username"],
                    user_data["role"].upper(),
                )
                continue

            # Check if user exists
            existing_user = db.query(User).filter(
                (User.username == user_data["username"]) | (User.email == user_data["email"])
            ).first()

            if not existing_user:
                logger.info(f"{user_data['role'].capitalize()} user not found, creating '{user_data['username']}'...")
                new_user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True
                )
                db.add(new_user)
                db.commit()
                logger.info(f"✅ {user_data['role'].capitalize()} user created successfully ({user_data['username']})")
            else:
                logger.info(f"✅ {user_data['role'].capitalize()} user verified (username: {existing_user.username})")
    except Exception as e:
        logger.error(f"Error ensuring default users exist: {e}")
        db.rollback()
    finally:
        db.close()


def ensure_admin_user():
    """Backward compatibility wrapper - calls ensure_default_users()"""
    ensure_default_users()


# Startup and shutdown are now handled by lifespan context manager above

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Church Course Tracker API",
        "version": "1.0.0",
        "status": "running"
    }

async def get_health_status():
    """Shared health check logic"""
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

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    return await get_health_status()

@app.get("/api/v1/health")
async def health_check_v1():
    """Comprehensive health check endpoint (v1 API path)"""
    return await get_health_status()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
