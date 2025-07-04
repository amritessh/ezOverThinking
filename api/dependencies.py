# api/dependencies.py
from typing import Dict, Any
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
    return services["state_manager"]


async def get_conversation_orchestrator() -> ConversationOrchestrator:
    return services["conversation_orchestrator"]


async def get_anxiety_tracker() -> AnxietyTracker:
    return services["anxiety_tracker"]


async def get_analytics_service() -> AnalyticsService:
    return services["analytics_service"]
