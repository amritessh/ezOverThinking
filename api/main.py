# api/main.py
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
from src.services.state_manager import StateManager
from src.services.conversation_orchestrator import ConversationOrchestrator
from src.services.anxiety_tracker import AnxietyTracker
from src.services.analytics_service import AnalyticsService
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
        # Initialize core services
        services["state_manager"] = StateManager(
            redis_url=settings.redis_url, ttl_seconds=settings.state_ttl
        )
        await services["state_manager"].initialize()

        services["anxiety_tracker"] = AnxietyTracker(
            state_manager=services["state_manager"]
        )
        await services["anxiety_tracker"].initialize()

        services["analytics_service"] = AnalyticsService(
            state_manager=services["state_manager"]
        )
        await services["analytics_service"].initialize()

        services["conversation_orchestrator"] = ConversationOrchestrator(
            state_manager=services["state_manager"],
            anxiety_tracker=services["anxiety_tracker"],
            analytics_service=services["analytics_service"],
        )
        await services["conversation_orchestrator"].initialize()

        logger.info("✅ All services initialized successfully")

        # Set services in dependencies
        set_services(services)

        # Start background tasks
        asyncio.create_task(analytics_background_task())
        asyncio.create_task(cleanup_background_task())

        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔄 Shutting down services...")
        for service_name, service in services.items():
            try:
                if hasattr(service, "cleanup"):
                    await service.cleanup()
                logger.info(f"✅ {service_name} cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up {service_name}: {e}")


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

# Import dependency functions
from .dependencies import (
    set_services,
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])

app.include_router(auth.router, prefix="/auth", tags=["authentication"])

app.include_router(
    chat.router, prefix="/chat", tags=["chat"], dependencies=[Depends(security)]
)

app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(security)],
)


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


# Background tasks
async def analytics_background_task():
    """Background task for analytics processing"""
    while True:
        try:
            analytics_service = services.get("analytics_service")
            if analytics_service:
                await analytics_service.process_background_analytics()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"Analytics background task error: {e}")
            await asyncio.sleep(60)


async def cleanup_background_task():
    """Background task for cleanup operations"""
    while True:
        try:
            state_manager = services.get("state_manager")
            if state_manager:
                await state_manager.cleanup_expired_sessions()
            await asyncio.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Cleanup background task error: {e}")
            await asyncio.sleep(300)


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
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
