# api/endpoints/health.py
from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from ..dependencies import get_state_manager, get_anxiety_tracker, get_analytics_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check(
    state_manager=Depends(get_state_manager),
    anxiety_tracker=Depends(get_anxiety_tracker),
    analytics_service=Depends(get_analytics_service),
) -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        # Check service health
        services_status = {}

        # Check state manager
        try:
            state_health = await state_manager.health_check()
            services_status["state_manager"] = state_health.get("status") == "healthy"
        except Exception as e:
            logger.error(f"State manager health check failed: {e}")
            services_status["state_manager"] = False

        # Check anxiety tracker
        try:
            anxiety_health = await anxiety_tracker.get_system_analytics()
            services_status["anxiety_tracker"] = True
        except Exception as e:
            logger.error(f"Anxiety tracker health check failed: {e}")
            services_status["anxiety_tracker"] = False

        # Check analytics service
        try:
            analytics_health = await analytics_service.get_system_performance_metrics()
            services_status["analytics_service"] = True
        except Exception as e:
            logger.error(f"Analytics service health check failed: {e}")
            services_status["analytics_service"] = False

        # Overall status
        overall_status = "healthy" if all(services_status.values()) else "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": services_status,
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0",
        }
