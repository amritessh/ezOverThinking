# api/main_simple.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import Dict
import uvicorn

# Internal imports
from .endpoints import chat, analytics, health, auth
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.security import SecurityMiddleware
from .middleware.logging import LoggingMiddleware
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
services: Dict[str, any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup services"""
    logger.info("🚀 Starting ezOverThinking API server...")

    # Initialize services
    settings = get_settings()

    try:
        # For now, just set empty services to allow the app to start
        services["state_manager"] = None
        services["anxiety_tracker"] = None
        services["analytics_service"] = None
        services["conversation_orchestrator"] = None

        logger.info("✅ App started with minimal services")

        # Set services in dependencies
        from .dependencies import set_services
        set_services(services)

        yield

    except Exception as e:
        logger.error(f"❌ Critical error during startup: {e}")
        yield
    finally:
        # Cleanup
        logger.info("🔄 Shutting down services...")


# Create FastAPI app
app = FastAPI(
    title="ezOverThinking API",
    description="The AI-powered overthinking amplification system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security
security = HTTPBearer()
settings = get_settings()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

app.add_middleware(RateLimitMiddleware, calls_per_minute=settings.rate_limit_per_minute)

app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])

app.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Comment out complex endpoints for now
# app.include_router(
#     chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(security)]
# )

# app.include_router(
#     analytics.router,
#     prefix="/analytics",
#     tags=["analytics"],
#     dependencies=[Depends(security)],
# )


# Root endpoint
@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to ezOverThinking API",
        "version": "1.0.0",
        "status": "ready_to_overthink",
        "docs": "/docs",
        "health": "/health",
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": {"code": exc.status_code, "message": exc.detail, "type": "http_error"}
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "error": {
            "code": 500,
            "message": "Internal server error",
            "type": "server_error",
        }
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "api.main_simple:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    ) 