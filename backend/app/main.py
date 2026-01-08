"""
ContentForge FastAPI Application

Purpose: Entry point for FastAPI server
Responsibilities:
• Initialize FastAPI app with production configuration
• Register all routers (content, publish)
• Configure CORS for frontend integration
• Set up middleware for logging and error handling
• Provide health check and documentation endpoints
• Handle application lifecycle (startup/shutdown)

Architecture Decision:
- Clean separation of concerns (routes in separate modules)
- Comprehensive CORS configuration for SaaS deployment
- Structured error handling with detailed logging
- OpenAPI documentation auto-generated
- Ready for Azure App Service deployment
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.api import content, publish

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for resource initialization
    and cleanup.
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 80)
    
    # Initialize global resources
    # (Clients are lazily initialized, but we could pre-warm here)
    
    yield
    
    # Shutdown
    logger.info("Shutting down ContentForge")
    # Cleanup resources if needed


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **ContentForge: Intelligent Enterprise Content Engine**
    
    A production-ready AI platform for generating structured business content using:
    - Multi-agent AI orchestration (Planning, Research, Drafting, Editing)
    - RAG (Retrieval-Augmented Generation) with Azure AI Search
    - Azure OpenAI (GPT-4o)
    - Microsoft Graph for SharePoint and Teams publishing
    
    ## Features
    - Generate reports, summaries, articles, and marketing copy
    - Ground all content in enterprise documents (anti-hallucination)
    - Automatic citation tracking for transparency
    - Publish to SharePoint and Teams
    - Scalable multi-agent architecture
    
    ## API Structure
    - `/api/v1/content/*` - Content generation endpoints
    - `/api/v1/publish/*` - Publishing endpoints
    - `/health` - Service health check
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ========================================
# Middleware Configuration
# ========================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    start_time = time.time()
    
    # Generate correlation ID for request tracing
    correlation_id = f"req-{int(start_time * 1000000)}"
    
    logger.info(
        f"Request started",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        }
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info(
            f"Request completed",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3),
            }
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        logger.error(
            f"Request failed",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "duration_seconds": round(duration, 3),
                "error": str(e),
            },
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "correlation_id": correlation_id,
            },
        )


# ========================================
# Exception Handlers
# ========================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed messages."""
    logger.warning(
        f"Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        f"Unhandled exception",
        extra={
            "path": request.url.path,
            "error_type": type(exc).__name__,
        },
        exc_info=True,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_type": type(exc).__name__,
        },
    )


# ========================================
# Route Registration
# ========================================

# Register API routers with versioning
app.include_router(content.router, prefix=settings.API_V1_PREFIX)
app.include_router(publish.router, prefix=settings.API_V1_PREFIX)


# ========================================
# Root and Health Endpoints
# ========================================

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API metadata and navigation
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health")
async def health_check():
    """
    Application health check endpoint.
    
    Used by load balancers and monitoring systems.
    
    Returns:
        Health status and service information
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with dependency status.
    
    Returns:
        Detailed health information including external dependencies
    """
    # TODO: Add actual health checks for:
    # - Azure OpenAI connectivity
    # - Azure AI Search connectivity
    # - Microsoft Graph API connectivity
    # - Database connectivity (when implemented)
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "dependencies": {
            "azure_openai": "not_checked",  # TODO: Implement actual check
            "ai_search": "not_checked",      # TODO: Implement actual check
            "graph_api": "not_checked",      # TODO: Implement actual check
        },
    }


# ========================================
# Development Server
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
