# api/dependencies.py
from typing import Dict, Any
from fastapi import HTTPException
from src.services.state_manager import StateManager
from src.services.conversation_orchestrator import ConversationOrchestrator
from src.services.anxiety_tracker import AnxietyTracker
from src.services.analytics_service import AnalyticsService

# Global service instances - will be set by main.py
services: Dict[str, Any] = {}


def set_services(service_dict: Dict[str, Any]):
    """Set the global services dictionary"""
    global services
    services = service_dict


# Dependency injection functions
async def get_state_manager() -> StateManager:
    service = services.get("state_manager")
    if service is None:
        raise HTTPException(status_code=503, detail="StateManager not available")
    return service


async def get_conversation_orchestrator() -> ConversationOrchestrator:
    service = services.get("conversation_orchestrator")
    if service is None:
        raise HTTPException(
            status_code=503, detail="ConversationOrchestrator not available"
        )
    return service


async def get_anxiety_tracker() -> AnxietyTracker:
    service = services.get("anxiety_tracker")
    if service is None:
        raise HTTPException(status_code=503, detail="AnxietyTracker not available")
    return service


async def get_analytics_service() -> AnalyticsService:
    service = services.get("analytics_service")
    if service is None:
        raise HTTPException(status_code=503, detail="AnalyticsService not available")
    return service
