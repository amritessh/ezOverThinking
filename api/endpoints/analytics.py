# api/endpoints/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from enum import Enum

from src.services.analytics_service import AnalyticsService
from src.services.anxiety_tracker import AnxietyTracker
from ..auth.jwt_handler import get_current_user
from ..dependencies import get_analytics_service, get_anxiety_tracker

logger = logging.getLogger(__name__)

router = APIRouter()


class TimeRange(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL = "all"


class MetricType(str, Enum):
    ANXIETY_PROGRESSION = "anxiety_progression"
    AGENT_PERFORMANCE = "agent_performance"
    CONVERSATION_PATTERNS = "conversation_patterns"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_HEALTH = "system_health"


# User Analytics Endpoints
@router.get("/user/overview")
async def get_user_analytics_overview(
    time_range: TimeRange = Query(TimeRange.WEEK),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get user analytics overview"""
    try:
        user_id = current_user["user_id"]

        # Calculate time range
        end_time = datetime.now()
        if time_range == TimeRange.HOUR:
            start_time = end_time - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            start_time = end_time - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            start_time = end_time - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            start_time = end_time - timedelta(days=30)
        else:  # ALL
            start_time = None

        analytics = await analytics_service.get_user_analytics(
            user_id=user_id, start_time=start_time, end_time=end_time
        )

        return {
            "user_id": user_id,
            "time_range": time_range.value,
            "analytics": analytics,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_user_analytics_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/anxiety-trends")
async def get_anxiety_trends(
    time_range: TimeRange = Query(TimeRange.WEEK),
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Get anxiety level trends over time"""
    try:
        user_id = current_user["user_id"]

        # Get anxiety history
        anxiety_history = await anxiety_tracker.get_anxiety_history(
            user_id=user_id, time_range=time_range.value
        )

        # Calculate trends
        trends = await anxiety_tracker.analyze_anxiety_trends(
            user_id=user_id, time_range=time_range.value
        )

        return {
            "user_id": user_id,
            "time_range": time_range.value,
            "anxiety_history": [
                {
                    "level": entry.anxiety_level.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "trigger": entry.trigger,
                    "context": entry.context,
                }
                for entry in anxiety_history
            ],
            "trends": trends,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_anxiety_trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/conversation-patterns")
async def get_conversation_patterns(
    time_range: TimeRange = Query(TimeRange.WEEK),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get user conversation patterns and insights"""
    try:
        user_id = current_user["user_id"]

        patterns = await analytics_service.get_conversation_patterns(
            user_id=user_id, time_range=time_range.value
        )

        return {
            "user_id": user_id,
            "time_range": time_range.value,
            "patterns": patterns,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_conversation_patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/worry-categories")
async def get_worry_categories(
    time_range: TimeRange = Query(TimeRange.WEEK),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get breakdown of worry categories"""
    try:
        user_id = current_user["user_id"]

        categories = await analytics_service.get_worry_categories_breakdown(
            user_id=user_id, time_range=time_range.value
        )

        return {
            "user_id": user_id,
            "time_range": time_range.value,
            "categories": categories,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_worry_categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Analytics Endpoints
@router.get("/system/overview")
async def get_system_analytics_overview(
    time_range: TimeRange = Query(TimeRange.DAY),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get system-wide analytics overview"""
    try:
        # Note: Add admin role check in production

        system_analytics = await analytics_service.get_system_analytics(
            time_range=time_range.value
        )

        return {
            "time_range": time_range.value,
            "system_analytics": system_analytics,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_system_analytics_overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/agent-performance")
async def get_agent_performance_metrics(
    time_range: TimeRange = Query(TimeRange.DAY),
    agent_name: Optional[str] = Query(None),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get agent performance metrics"""
    try:
        # Note: Add admin role check in production

        performance_metrics = await analytics_service.get_agent_performance_metrics(
            time_range=time_range.value, agent_name=agent_name
        )

        return {
            "time_range": time_range.value,
            "agent_name": agent_name,
            "performance_metrics": performance_metrics,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_agent_performance_metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health")
async def get_system_health(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get system health metrics"""
    try:
        # Note: Add admin role check in production

        health_metrics = await analytics_service.get_system_health()

        return {
            "health_metrics": health_metrics,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_system_health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Real-time Analytics Endpoints
@router.get("/realtime/active-conversations")
async def get_realtime_active_conversations(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get real-time active conversations count"""
    try:
        active_count = await analytics_service.get_active_conversations_count()

        return {
            "active_conversations": active_count,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_realtime_active_conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/realtime/anxiety-distribution")
async def get_realtime_anxiety_distribution(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get real-time anxiety level distribution"""
    try:
        distribution = await analytics_service.get_anxiety_level_distribution()

        return {
            "anxiety_distribution": distribution,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_realtime_anxiety_distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export Endpoints
@router.get("/export/user-data")
async def export_user_data(
    format: str = Query("json", regex="^(json|csv|excel)$"),
    time_range: TimeRange = Query(TimeRange.ALL),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Export user data in various formats"""
    try:
        user_id = current_user["user_id"]

        data = await analytics_service.export_user_data(
            user_id=user_id, format=format, time_range=time_range.value
        )

        if format == "json":
            return data
        elif format == "csv":
            return Response(
                content=data,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=user_data_{user_id}.csv"
                },
            )
        elif format == "excel":
            return Response(
                content=data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=user_data_{user_id}.xlsx"
                },
            )

    except Exception as e:
        logger.error(f"❌ Error in export_user_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Custom Analytics Endpoints
@router.post("/custom/query")
async def custom_analytics_query(
    query: Dict[str, Any],
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Execute custom analytics query"""
    try:
        # Note: Add validation and security checks for custom queries

        result = await analytics_service.execute_custom_query(
            query=query, user_id=current_user["user_id"]
        )

        return {
            "query": query,
            "result": result,
            "executed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in custom_analytics_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/recommendations")
async def get_personalized_recommendations(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get personalized recommendations based on analytics"""
    try:
        user_id = current_user["user_id"]

        recommendations = await analytics_service.get_personalized_recommendations(
            user_id=user_id
        )

        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_personalized_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/prediction")
async def get_anxiety_prediction(
    hours_ahead: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get anxiety level prediction"""
    try:
        user_id = current_user["user_id"]

        prediction = await analytics_service.predict_anxiety_levels(
            user_id=user_id, hours_ahead=hours_ahead
        )

        return {
            "user_id": user_id,
            "hours_ahead": hours_ahead,
            "prediction": prediction,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_anxiety_prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Comparison Endpoints
@router.get("/comparison/peer-analysis")
async def get_peer_comparison(
    anonymous: bool = Query(True),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: dict = Depends(get_current_user),
):
    """Get anonymized peer comparison analysis"""
    try:
        user_id = current_user["user_id"]

        comparison = await analytics_service.get_peer_comparison(
            user_id=user_id, anonymous=anonymous
        )

        return {
            "user_id": user_id if not anonymous else "anonymous",
            "comparison": comparison,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error in get_peer_comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))
