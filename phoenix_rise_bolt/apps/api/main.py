import asyncio
import logging
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.core.security import SecurityHeaders
from app.core.rate_limiter import RateLimiter
from app.core.database import database, engine, metadata
from app.api.v1 import api_router
from app.core.exceptions import PhoenixException
from app.core.logging import configure_logging
from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_DURATION,
    ERROR_COUNT,
    setup_metrics,
)

# Configure structured logging
configure_logging()
logger = structlog.get_logger(__name__)

# Initialize rate limiter
rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Phoenix Rise API")
    
    # Database connection
    await database.connect()
    logger.info("Database connected")
    
    # Setup metrics
    setup_metrics()
    logger.info("Metrics initialized")
    
    yield
    
    # Cleanup
    await database.disconnect()
    logger.info("Phoenix Rise API stopped")

# Create FastAPI app
app = FastAPI(
    title="Phoenix Rise & Dojo Mental API",
    description="Mental traction ecosystem API - Production ready",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(SecurityHeaders)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting"""
    client_ip = request.client.host
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/metrics"]:
        return await call_next(request)
    
    if not await rate_limiter.is_allowed(client_ip):
        ERROR_COUNT.labels(error_type="rate_limit").inc()
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            }
        )
    
    return await call_next(request)

# Request logging and metrics middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log requests and collect metrics"""
    import time
    
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    logger.info("Request started", method=method, path=path)
    
    try:
        response = await call_next(request)
        
        duration = time.time() - start_time
        status_code = response.status_code
        
        # Metrics
        REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
        
        logger.info(
            "Request completed",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        ERROR_COUNT.labels(error_type="internal").inc()
        
        logger.error(
            "Request failed",
            method=method,
            path=path,
            error=str(e),
            duration=duration,
        )
        raise

# Exception handlers
@app.exception_handler(PhoenixException)
async def phoenix_exception_handler(request: Request, exc: PhoenixException):
    """Handle Phoenix-specific exceptions"""
    logger.error("Phoenix exception", error=str(exc), error_code=exc.error_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    ERROR_COUNT.labels(error_type="validation").inc()
    logger.warning("Validation error", errors=exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "error_code": "VALIDATION_ERROR",
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    ERROR_COUNT.labels(error_type="http").inc()
    logger.warning("HTTP exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR",
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    ERROR_COUNT.labels(error_type="internal").inc()
    logger.error("Unexpected error", error=str(exc), error_type=type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await database.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "phoenix-rise-api",
            "version": "0.1.0",
            "timestamp": "2025-01-27T10:00:00Z",
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "phoenix-rise-api",
                "error": str(e),
            }
        )

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# API routes
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,  # Use our structured logging
    )