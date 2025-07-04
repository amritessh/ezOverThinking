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
from fastapi.responses import JSONResponse

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
        # Initialize core services with error handling
        try:
            services["state_manager"] = StateManager(
                redis_url=settings.redis_url, ttl_seconds=settings.state_ttl
            )
            connected = await services["state_manager"].connect()
            if connected:
                logger.info("✅ StateManager connected")
            else:
                logger.warning("⚠️ StateManager failed to connect to Redis")
                services["state_manager"] = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize StateManager: {e}")
            services["state_manager"] = None

        try:
            if services.get("state_manager"):
                services["anxiety_tracker"] = AnxietyTracker(
                    state_manager=services["state_manager"]
                )
                await services["anxiety_tracker"].initialize()
                logger.info("✅ AnxietyTracker initialized")
            else:
                logger.warning(
                    "⚠️ Skipping AnxietyTracker initialization (StateManager not available)"
                )
                services["anxiety_tracker"] = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize AnxietyTracker: {e}")
            services["anxiety_tracker"] = None

        try:
            if services.get("state_manager"):
                services["analytics_service"] = AnalyticsService(
                    state_manager=services["state_manager"]
                )
                await services["analytics_service"].initialize()
                logger.info("✅ AnalyticsService initialized")
            else:
                logger.warning(
                    "⚠️ Skipping AnalyticsService initialization (StateManager not available)"
                )
                services["analytics_service"] = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize AnalyticsService: {e}")
            services["analytics_service"] = None

        try:
            if all([services.get("state_manager"), services.get("anxiety_tracker")]):
                services["conversation_orchestrator"] = ConversationOrchestrator(
                    state_manager=services["state_manager"],
                    anxiety_tracker=services["anxiety_tracker"],
                )
                await services["conversation_orchestrator"].initialize()
                
                # Register agents with the orchestrator
                from src.agents.intake_specialist import IntakeSpecialistAgent
                from src.agents.catastrophe_escalator import CatastropheEscalatorAgent
                from src.agents.probability_twister import ProbabilityTwisterAgent
                from src.agents.social_anxiety_amplifier import SocialAnxietyAmplifierAgent
                from src.agents.timeline_panic_generator import TimelinePanicGeneratorAgent
                from src.agents.false_comfort_provider import FalseComfortProviderAgent
                from src.agents.coordinator import AgentCoordinator
                
                # Register all agents
                intake_agent = IntakeSpecialistAgent()
                catastrophe_agent = CatastropheEscalatorAgent()
                probability_agent = ProbabilityTwisterAgent()
                social_agent = SocialAnxietyAmplifierAgent()
                timeline_agent = TimelinePanicGeneratorAgent()
                comfort_agent = FalseComfortProviderAgent()
                coordinator = AgentCoordinator()
                
                services["conversation_orchestrator"].register_agent(intake_agent)
                services["conversation_orchestrator"].register_agent(catastrophe_agent)
                services["conversation_orchestrator"].register_agent(probability_agent)
                services["conversation_orchestrator"].register_agent(social_agent)
                services["conversation_orchestrator"].register_agent(timeline_agent)
                services["conversation_orchestrator"].register_agent(comfort_agent)
                services["conversation_orchestrator"].register_coordinator(coordinator)
                
                logger.info("✅ ConversationOrchestrator initialized with all agents")
            else:
                logger.warning(
                    "⚠️ Skipping ConversationOrchestrator initialization (dependencies not available)"
                )
                services["conversation_orchestrator"] = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize ConversationOrchestrator: {e}")
            services["conversation_orchestrator"] = None

        logger.info("✅ Service initialization completed")

        # Set services in dependencies
        set_services(services)

        # Start background tasks only if services are available
        if services.get("analytics_service"):
            asyncio.create_task(analytics_background_task())
        if services.get("state_manager"):
            asyncio.create_task(cleanup_background_task())

        yield

    except Exception as e:
        logger.error(f"❌ Critical error during startup: {e}")
        # Don't raise - let the app start anyway
        yield
    finally:
        # Cleanup
        logger.info("🔄 Shutting down services...")
        for service_name, service in services.items():
            if service:
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

app.include_router(chat.router, prefix="/chat", tags=["chat"])

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


@app.get("/status")
async def status():
    """Check service status"""
    return {
        "state_manager": services.get("state_manager") is not None,
        "anxiety_tracker": services.get("anxiety_tracker") is not None,
        "analytics_service": services.get("analytics_service") is not None,
        "conversation_orchestrator": services.get("conversation_orchestrator")
        is not None,
    }


@app.post("/test-chat")
async def test_chat():
    """Test chat endpoint without dependencies"""
    try:
        orchestrator = services.get("conversation_orchestrator")
        if orchestrator is None:
            return {"error": "ConversationOrchestrator not available"}

        # Test basic functionality
        return {"message": "Test successful", "orchestrator_available": True}
    except Exception as e:
        return {"error": str(e)}


@app.post("/echo")
async def echo_request(request: dict):
    """Echo the request to test JSON parsing"""
    return {"received": request}


@app.post("/test-orchestrator")
async def test_orchestrator():
    """Test orchestrator directly"""
    try:
        orchestrator = services.get("conversation_orchestrator")
        if orchestrator is None:
            return {"error": "ConversationOrchestrator not available"}

        # Test orchestrator methods
        user_id = "demo_user"
        state = await orchestrator.get_conversation_state(user_id)

        return {
            "orchestrator_available": True,
            "conversation_state": state is not None,
            "state_details": str(state) if state else None,
        }
    except Exception as e:
        return {"error": str(e), "traceback": str(e.__traceback__)}

@app.post("/test-orchestrate")
async def test_orchestrate():
    """Test orchestrate_response method"""
    try:
        orchestrator = services.get("conversation_orchestrator")
        if orchestrator is None:
            return {"error": "ConversationOrchestrator not available"}
        
        # Test orchestrate_response
        user_id = "demo_user"
        state = await orchestrator.get_conversation_state(user_id)
        
        if state:
            response = await orchestrator.orchestrate_response(state.conversation_id, "test message")
            return {
                "success": True,
                "response": response.response,
                "agent_name": response.agent_name
            }
        else:
            return {"error": "No conversation state found"}
    except Exception as e:
        return {"error": str(e), "traceback": str(e.__traceback__)}


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
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail, "type": "http_error"}}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Internal server error", "type": "server_error"}}
    )


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
