"""
Analytics Service - Performance Metrics Dashboard Backend
This service provides comprehensive analytics, performance metrics, and insights
for the ezOverThinking multi-agent system.

File: src/services/analytics_service.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter

from .state_manager import StateManager
from .anxiety_tracker import AnxietyTracker
from ..models.schemas import (
    ConversationState,
    ConversationStatus,
    AnxietyLevel,
    WorryCategory,
    AgentInteraction
)


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"


class MetricType(Enum):
    """Types of metrics to collect"""
    CONVERSATION_METRICS = "conversation_metrics"
    AGENT_PERFORMANCE = "agent_performance"
    ANXIETY_ANALYTICS = "anxiety_analytics"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"
    ORCHESTRATION_METRICS = "orchestration_metrics"


@dataclass
class ConversationMetrics:
    """Conversation-level metrics"""
    total_conversations: int
    active_conversations: int
    completed_conversations: int
    average_duration: float
    average_message_count: float
    average_anxiety_escalation: float
    completion_rate: float
    user_satisfaction_score: float = 0.0


@dataclass
class AgentPerformanceMetrics:
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    total_interactions: int
    successful_interactions: int
    average_response_time: float
    average_anxiety_escalation: float
    user_engagement_score: float
    effectiveness_rating: float
    error_rate: float
    handoff_success_rate: float


@dataclass
class AnxietyAnalytics:
    """Anxiety progression analytics"""
    average_initial_anxiety: float
    average_peak_anxiety: float
    average_escalation_rate: float
    common_escalation_patterns: List[str]
    anxiety_distribution: Dict[int, int]
    escalation_success_rate: float
    time_to_peak_anxiety: float


@dataclass
class UserEngagementMetrics:
    """User engagement metrics"""
    total_users: int
    active_users: int
    returning_users: int
    average_session_duration: float
    average_conversations_per_user: float
    user_retention_rate: float
    engagement_score: float


class AnalyticsService:
    """
    Comprehensive analytics service for the ezOverThinking system
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        anxiety_tracker: AnxietyTracker = None
    ):
        self.state_manager = state_manager
        self.anxiety_tracker = anxiety_tracker
        self.logger = logging.getLogger("AnalyticsService")
        
        # Analytics cache
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
        # Configuration
        self.config = {
            "cache_ttl_seconds": 300,  # 5 minutes
            "batch_size": 100,
            "max_historical_days": 30,
            "real_time_update_interval": 60,  # 1 minute
            "aggregation_intervals": {
                "minute": 1,
                "hour": 60,
                "day": 1440,
                "week": 10080
            }
        }
        
        # Background tasks
        self.background_tasks = []
        self.is_running = False
        
        # Metrics storage
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Performance tracking
        self.performance_metrics = {
            "queries_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_query_time": 0.0,
            "errors": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize analytics service"""
        try:
            # Load historical metrics
            await self._load_historical_metrics()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            self.logger.info("AnalyticsService initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing analytics service: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown analytics service"""
        try:
            self.is_running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Save metrics
            await self._save_metrics()
            
            self.logger.info("AnalyticsService shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error shutting down analytics service: {e}")
    
    async def get_conversation_metrics(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAY
    ) -> ConversationMetrics:
        """Get conversation-level metrics"""
        try:
            cache_key = f"conversation_metrics_{timeframe.value}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Calculate metrics
            start_time = self._get_timeframe_start(timeframe)
            
            # Get conversation data
            conversations = await self._get_conversations_in_timeframe(start_time)
            
            if not conversations:
                return ConversationMetrics(
                    total_conversations=0,
                    active_conversations=0,
                    completed_conversations=0,
                    average_duration=0,
                    average_message_count=0,
                    average_anxiety_escalation=0,
                    completion_rate=0
                )
            
            # Calculate metrics
            total_conversations = len(conversations)
            active_conversations = len([c for c in conversations if c.status == ConversationStatus.ACTIVE])
            completed_conversations = len([c for c in conversations if c.status == ConversationStatus.COMPLETED])
            
            # Duration metrics
            durations = []
            for conv in conversations:
                if conv.status == ConversationStatus.COMPLETED:
                    duration = (conv.updated_at - conv.created_at).total_seconds() / 60
                    durations.append(duration)
            
            average_duration = statistics.mean(durations) if durations else 0
            
            # Message count metrics
            message_counts = [conv.message_count for conv in conversations]
            average_message_count = statistics.mean(message_counts) if message_counts else 0
            
            # Anxiety escalation metrics
            escalation_counts = [conv.escalation_count for conv in conversations]
            average_anxiety_escalation = statistics.mean(escalation_counts) if escalation_counts else 0
            
            # Completion rate
            completion_rate = (completed_conversations / total_conversations) if total_conversations > 0 else 0
            
            metrics = ConversationMetrics(
                total_conversations=total_conversations,
                active_conversations=active_conversations,
                completed_conversations=completed_conversations,
                average_duration=average_duration,
                average_message_count=average_message_count,
                average_anxiety_escalation=average_anxiety_escalation,
                completion_rate=completion_rate
            )
            
            # Cache results
            self.analytics_cache[cache_key] = metrics
            self.cache_timestamps[cache_key] = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting conversation metrics: {e}")
            self.performance_metrics["errors"] += 1
            raise
    
    async def get_agent_performance_metrics(
        self, 
        agent_id: str = None,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAY
    ) -> List[AgentPerformanceMetrics]:
        """Get agent performance metrics"""
        try:
            cache_key = f"agent_performance_{agent_id or 'all'}_{timeframe.value}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Calculate metrics
            start_time = self._get_timeframe_start(timeframe)
            
            # Get interaction data
            interactions = await self._get_interactions_in_timeframe(start_time)
            
            if not interactions:
                return []
            
            # Group by agent
            agent_interactions = defaultdict(list)
            for interaction in interactions:
                agent_interactions[interaction.source_agent_id].append(interaction)
            
            # Calculate metrics for each agent
            agent_metrics = []
            for agent_id_key, agent_interaction_list in agent_interactions.items():
                
                # Skip if filtering by specific agent
                if agent_id and agent_id_key != agent_id:
                    continue
                
                # Calculate metrics
                total_interactions = len(agent_interaction_list)
                successful_interactions = len([i for i in agent_interaction_list if i.success])
                
                # Response time (simulated for now)
                response_times = [1.5 + (i.anxiety_after.value - i.anxiety_before.value) * 0.3 for i in agent_interaction_list]
                average_response_time = statistics.mean(response_times) if response_times else 0
                
                # Anxiety escalation
                anxiety_escalations = [i.anxiety_after.value - i.anxiety_before.value for i in agent_interaction_list]
                average_anxiety_escalation = statistics.mean(anxiety_escalations) if anxiety_escalations else 0
                
                # User engagement score (based on interaction success and escalation)
                user_engagement_score = (successful_interactions / total_interactions) * 0.7 + (average_anxiety_escalation / 5) * 0.3
                
                # Effectiveness rating
                effectiveness_rating = (successful_interactions / total_interactions) * (1 + average_anxiety_escalation / 5)
                
                # Error rate
                error_rate = 1 - (successful_interactions / total_interactions)
                
                # Handoff success rate (simulated)
                handoff_success_rate = 0.85 + (effectiveness_rating * 0.15)
                
                metrics = AgentPerformanceMetrics(
                    agent_id=agent_id_key,
                    agent_name=f"Agent_{agent_id_key}",  # Would be resolved from agent registry
                    total_interactions=total_interactions,
                    successful_interactions=successful_interactions,
                    average_response_time=average_response_time,
                    average_anxiety_escalation=average_anxiety_escalation,
                    user_engagement_score=min(1.0, user_engagement_score),
                    effectiveness_rating=min(1.0, effectiveness_rating),
                    error_rate=error_rate,
                    handoff_success_rate=min(1.0, handoff_success_rate)
                )
                
                agent_metrics.append(metrics)
            
            # Sort by effectiveness rating
            agent_metrics.sort(key=lambda x: x.effectiveness_rating, reverse=True)
            
            # Cache results
            self.analytics_cache[cache_key] = agent_metrics
            self.cache_timestamps[cache_key] = datetime.now()
            
            return agent_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting agent performance metrics: {e}")
            self.performance_metrics["errors"] += 1
            raise
    
    async def get_anxiety_analytics(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAY
    ) -> AnxietyAnalytics:
        """Get anxiety progression analytics"""
        try:
            cache_key = f"anxiety_analytics_{timeframe.value}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Get anxiety data from tracker
            if not self.anxiety_tracker:
                return AnxietyAnalytics(
                    average_initial_anxiety=0,
                    average_peak_anxiety=0,
                    average_escalation_rate=0,
                    common_escalation_patterns=[],
                    anxiety_distribution={},
                    escalation_success_rate=0,
                    time_to_peak_anxiety=0
                )
            
            # Get system analytics from anxiety tracker
            anxiety_system_analytics = await self.anxiety_tracker.get_system_analytics()
            
            # Calculate additional metrics
            start_time = self._get_timeframe_start(timeframe)
            conversations = await self._get_conversations_in_timeframe(start_time)
            
            # Calculate initial anxiety average
            initial_anxiety_levels = []
            peak_anxiety_levels = []
            escalation_rates = []
            
            for conv in conversations:
                if conv.context.get("initial_concern"):
                    initial_concern = conv.context["initial_concern"]
                    initial_anxiety_levels.append(initial_concern.get("anxiety_level", 1))
                
                # Peak anxiety is current anxiety for active conversations
                peak_anxiety_levels.append(conv.current_anxiety_level.value)
                
                # Escalation rate based on escalation count and duration
                if conv.message_count > 0:
                    escalation_rate = conv.escalation_count / conv.message_count
                    escalation_rates.append(escalation_rate)
            
            average_initial_anxiety = statistics.mean(initial_anxiety_levels) if initial_anxiety_levels else 0
            average_peak_anxiety = statistics.mean(peak_anxiety_levels) if peak_anxiety_levels else 0
            average_escalation_rate = statistics.mean(escalation_rates) if escalation_rates else 0
            
            # Time to peak anxiety (simulated)
            time_to_peak_anxiety = average_peak_anxiety * 2.5  # minutes
            
            # Escalation success rate
            successful_escalations = len([r for r in escalation_rates if r > 0.3])
            escalation_success_rate = (successful_escalations / len(escalation_rates)) if escalation_rates else 0
            
            analytics = AnxietyAnalytics(
                average_initial_anxiety=average_initial_anxiety,
                average_peak_anxiety=average_peak_anxiety,
                average_escalation_rate=average_escalation_rate,
                common_escalation_patterns=anxiety_system_analytics.get("common_escalation_patterns", []),
                anxiety_distribution=anxiety_system_analytics.get("anxiety_distribution", {}),
                escalation_success_rate=escalation_success_rate,
                time_to_peak_anxiety=time_to_peak_anxiety
            )
            
            # Cache results
            self.analytics_cache[cache_key] = analytics
            self.cache_timestamps[cache_key] = datetime.now()
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting anxiety analytics: {e}")
            self.performance_metrics["errors"] += 1
            raise
    
    async def get_user_engagement_metrics(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAY
    ) -> UserEngagementMetrics:
        """Get user engagement metrics"""
        try:
            cache_key = f"user_engagement_{timeframe.value}"
            
            # Check cache
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Calculate metrics
            start_time = self._get_timeframe_start(timeframe)
            
            # Get conversation data
            conversations = await self._get_conversations_in_timeframe(start_time)
            
            if not conversations:
                return UserEngagementMetrics(
                    total_users=0,
                    active_users=0,
                    returning_users=0,
                    average_session_duration=0,
                    average_conversations_per_user=0,
                    user_retention_rate=0,
                    engagement_score=0
                )
            
            # User metrics
            user_conversations = defaultdict(list)
            for conv in conversations:
                user_conversations[conv.user_id].append(conv)
            
            total_users = len(user_conversations)
            active_users = len([user_id for user_id, convs in user_conversations.items() if convs])
            
            # Returning users (users with more than one conversation)
            returning_users = len([user_id for user_id, convs in user_conversations.items() if len(convs) > 1])
            
            # Session duration
            session_durations = []
            for user_id, user_convs in user_conversations.items():
                for conv in user_convs:
                    if conv.status == ConversationStatus.COMPLETED:
                        duration = (conv.updated_at - conv.created_at).total_seconds() / 60
                        session_durations.append(duration)
            
            average_session_duration = statistics.mean(session_durations) if session_durations else 0
            
            # Conversations per user
            conversations_per_user = [len(convs) for convs in user_conversations.values()]
            average_conversations_per_user = statistics.mean(conversations_per_user) if conversations_per_user else 0
            
            # User retention rate
            user_retention_rate = (returning_users / total_users) if total_users > 0 else 0
            
            # Engagement score (composite metric)
            engagement_score = (
                (average_session_duration / 10) * 0.3 +  # Session duration component
                (average_conversations_per_user / 5) * 0.3 +  # Conversations per user component
                user_retention_rate * 0.4  # Retention component
            )
            engagement_score = min(1.0, engagement_score)
            
            metrics = UserEngagementMetrics(
                total_users=total_users,
                active_users=active_users,
                returning_users=returning_users,
                average_session_duration=average_session_duration,
                average_conversations_per_user=average_conversations_per_user,
                user_retention_rate=user_retention_rate,
                engagement_score=engagement_score
            )
            
            # Cache results
            self.analytics_cache[cache_key] = metrics
            self.cache_timestamps[cache_key] = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting user engagement metrics: {e}")
            self.performance_metrics["errors"] += 1
            raise
    
    async def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # Get state manager metrics
            state_manager_metrics = await self.state_manager.get_system_metrics()
            
            # Get anxiety tracker metrics
            anxiety_tracker_metrics = {}
            if self.anxiety_tracker:
                anxiety_tracker_metrics = await self.anxiety_tracker.get_system_analytics()
            
            # Combine with analytics service metrics
            system_metrics = {
                "analytics_service": {
                    "queries_processed": self.performance_metrics["queries_processed"],
                    "cache_hit_rate": (
                        self.performance_metrics["cache_hits"] / 
                        max(1, self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"])
                    ),
                    "average_query_time": self.performance_metrics["average_query_time"],
                    "error_rate": (
                        self.performance_metrics["errors"] / 
                        max(1, self.performance_metrics["queries_processed"])
                    ),
                    "cache_size": len(self.analytics_cache),
                    "is_running": self.is_running
                },
                "state_manager": state_manager_metrics,
                "anxiety_tracker": anxiety_tracker_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            return system_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system performance metrics: {e}")
            self.performance_metrics["errors"] += 1
            return {"error": str(e)}
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        try:
            # Get all metrics with short timeframes
            conversation_metrics = await self.get_conversation_metrics(AnalyticsTimeframe.HOUR)
            agent_metrics = await self.get_agent_performance_metrics(timeframe=AnalyticsTimeframe.HOUR)
            anxiety_analytics = await self.get_anxiety_analytics(AnalyticsTimeframe.HOUR)
            user_engagement = await self.get_user_engagement_metrics(AnalyticsTimeframe.HOUR)
            system_performance = await self.get_system_performance_metrics()
            
            # Compile dashboard
            dashboard = {
                "overview": {
                    "total_conversations": conversation_metrics.total_conversations,
                    "active_conversations": conversation_metrics.active_conversations,
                    "average_anxiety_level": anxiety_analytics.average_peak_anxiety,
                    "user_engagement_score": user_engagement.engagement_score,
                    "system_health": "healthy" if system_performance.get("analytics_service", {}).get("is_running") else "unhealthy"
                },
                "conversation_metrics": conversation_metrics,
                "top_agents": agent_metrics[:5],  # Top 5 agents
                "anxiety_analytics": anxiety_analytics,
                "user_engagement": user_engagement,
                "system_performance": system_performance,
                "alerts": await self._get_system_alerts(),
                "timestamp": datetime.now().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error getting real-time dashboard: {e}")
            return {"error": str(e)}
    
    async def get_historical_trends(
        self, 
        metric_type: MetricType,
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEK
    ) -> Dict[str, Any]:
        """Get historical trend data"""
        try:
            # Get historical data points
            end_time = datetime.now()
            start_time = self._get_timeframe_start(timeframe)
            
            # Generate time series data
            time_series = []
            current_time = start_time
            
            # Determine interval based on timeframe
            if timeframe == AnalyticsTimeframe.HOUR:
                interval = timedelta(minutes=5)
            elif timeframe == AnalyticsTimeframe.DAY:
                interval = timedelta(hours=1)
            elif timeframe == AnalyticsTimeframe.WEEK:
                interval = timedelta(hours=6)
            else:
                interval = timedelta(days=1)
            
            while current_time <= end_time:
                # Get metrics for this time point
                if metric_type == MetricType.CONVERSATION_METRICS:
                    # Simulate conversation metrics over time
                    data_point = {
                        "timestamp": current_time.isoformat(),
                        "total_conversations": max(0, int((current_time - start_time).total_seconds() / 3600)),
                        "active_conversations": max(0, int((current_time - start_time).total_seconds() / 7200)),
                        "completion_rate": 0.8 + (hash(current_time.hour) % 20) / 100
                    }
                elif metric_type == MetricType.ANXIETY_ANALYTICS:
                    data_point = {
                        "timestamp": current_time.isoformat(),
                        "average_anxiety": 2.5 + (hash(current_time.hour) % 20) / 10,
                        "peak_anxiety": 4.0 + (hash(current_time.hour) % 10) / 10,
                        "escalation_rate": 0.6 + (hash(current_time.hour) % 30) / 100
                    }
                else:
                    data_point = {
                        "timestamp": current_time.isoformat(),
                        "value": hash(current_time.hour) % 100
                    }
                
                time_series.append(data_point)
                current_time += interval
            
            return {
                "metric_type": metric_type.value,
                "timeframe": timeframe.value,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "data_points": len(time_series),
                "time_series": time_series
            }
            
        except Exception as e:
            self.logger.error(f"Error getting historical trends: {e}")
            return {"error": str(e)}
    
    async def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts"""
        alerts = []
        
        try:
            # Check system performance
            system_metrics = await self.get_system_performance_metrics()
            
            # High error rate alert
            error_rate = system_metrics.get("analytics_service", {}).get("error_rate", 0)
            if error_rate > 0.1:
                alerts.append({
                    "level": "warning",
                    "type": "high_error_rate",
                    "message": f"High error rate detected: {error_rate:.1%}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Low cache hit rate alert
            cache_hit_rate = system_metrics.get("analytics_service", {}).get("cache_hit_rate", 0)
            if cache_hit_rate < 0.5:
                alerts.append({
                    "level": "info",
                    "type": "low_cache_hit_rate",
                    "message": f"Low cache hit rate: {cache_hit_rate:.1%}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check conversation metrics
            conv_metrics = await self.get_conversation_metrics(AnalyticsTimeframe.HOUR)
            if conv_metrics.completion_rate < 0.5:
                alerts.append({
                    "level": "warning",
                    "type": "low_completion_rate",
                    "message": f"Low conversation completion rate: {conv_metrics.completion_rate:.1%}",
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            self.logger.error(f"Error getting system alerts: {e}")
        
        return alerts
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self.analytics_cache:
            self.performance_metrics["cache_misses"] += 1
            return False
        
        timestamp = self.cache_timestamps.get(cache_key)
        if not timestamp:
            self.performance_metrics["cache_misses"] += 1
            return False
        
        age = (datetime.now() - timestamp).total_seconds()
        if age > self.config["cache_ttl_seconds"]:
            self.performance_metrics["cache_misses"] += 1
            return False
        
        self.performance_metrics["cache_hits"] += 1
        return True
    
    def _get_timeframe_start(self, timeframe: AnalyticsTimeframe) -> datetime:
        """Get start time for timeframe"""
        now = datetime.now()
        
        if timeframe == AnalyticsTimeframe.HOUR:
            return now - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAY:
            return now - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEK:
            return now - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTH:
            return now - timedelta(days=30)
        else:
            return datetime.min
    
    async def _get_conversations_in_timeframe(self, start_time: datetime) -> List[ConversationState]:
        """Get conversations within timeframe"""
        try:
            # This would typically query the database
            # For now, we'll return simulated data
            conversations = []
            
            # Simulate some conversations
            for i in range(20):
                conv_time = start_time + timedelta(minutes=i * 30)
                if conv_time <= datetime.now():
                    conv = ConversationState(
                        conversation_id=f"conv_{i}",
                        user_id=f"user_{i % 5}",
                        status=ConversationStatus.COMPLETED if i % 3 == 0 else ConversationStatus.ACTIVE,
                        current_anxiety_level=AnxietyLevel(min(5, 1 + i % 5)),
                        message_count=5 + i % 10,
                        escalation_count=i % 3,
                        agents_involved=[f"agent_{j}" for j in range(i % 3 + 1)],
                        created_at=conv_time,
                        updated_at=conv_time + timedelta(minutes=15),
                        context={"initial_concern": {"anxiety_level": 1 + i % 3}}
                    )
                    conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error getting conversations in timeframe: {e}")
            return []
    
    async def _get_interactions_in_timeframe(self, start_time: datetime) -> List[AgentInteraction]:
        """Get interactions within timeframe"""
        try:
            # This would typically query the database
            # For now, we'll return simulated data
            interactions = []
            
            # Simulate some interactions
            for i in range(50):
                interaction_time = start_time + timedelta(minutes=i * 10)
                if interaction_time <= datetime.now():
                    interaction = AgentInteraction(
                        interaction_id=f"interaction_{i}",
                        conversation_id=f"conv_{i % 10}",
                        source_agent_id=f"agent_{i % 6}",
                        target_agent_id=f"agent_{(i + 1) % 6}",
                        interaction_type="response",
                        content=f"Response {i}",
                        anxiety_before=AnxietyLevel(min(5, 1 + i % 4)),
                        anxiety_after=AnxietyLevel(min(5, 2 + i % 4)),
                        success=i % 7 != 0,  # 85% success rate
                        timestamp=interaction_time
                    )
                    interactions.append(interaction)
            
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error getting interactions in timeframe: {e}")
            return []
    
    async def _start_background_tasks(self):
        """Start background analytics tasks"""
        try:
            # Real-time metrics update task
            task = asyncio.create_task(self._real_time_metrics_update())
            self.background_tasks.append(task)
            
            # Cache cleanup task
            task = asyncio.create_task(self._cache_cleanup())
            self.background_tasks.append(task)
            
            # Metrics aggregation task
            task = asyncio.create_task(self._metrics_aggregation())
            self.background_tasks.append(task)
            
        except Exception as e:
            self.logger.error(f"Error starting background tasks: {e}")
    
    async def _real_time_metrics_update(self):
        """Background task for real-time metrics updates"""
        while self.is_running:
            try:
                # Update real-time metrics
                await asyncio.sleep(self.config["real_time_update_interval"])
                
                # Clear expired cache entries
                await self._clear_expired_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in real-time metrics update: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _cache_cleanup(self):
        """Background task for cache cleanup"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._clear_expired_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cache cleanup: {e}")
    
    async def _metrics_aggregation(self):
        """Background task for metrics aggregation"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._aggregate_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics aggregation: {e}")
    
    async def _clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            now = datetime.now()
            expired_keys = []
            
            for key, timestamp in self.cache_timestamps.items():
                if (now - timestamp).total_seconds() > self.config["cache_ttl_seconds"]:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.analytics_cache[key]
                del self.cache_timestamps[key]
            
            if expired_keys:
                self.logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {e}")
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for historical analysis"""
        try:
            # Get current metrics
            current_metrics = {
                "conversation_metrics": await self.get_conversation_metrics(AnalyticsTimeframe.HOUR),
                "user_engagement": await self.get_user_engagement_metrics(AnalyticsTimeframe.HOUR),
                "anxiety_analytics": await self.get_anxiety_analytics(AnalyticsTimeframe.HOUR),
                "system_performance": await self.get_system_performance_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in metrics history
            self.metrics_history["hourly"].append(current_metrics)
            
            # Limit history size
            max_history = self.config["max_historical_days"] * 24  # Hourly data points
            if len(self.metrics_history["hourly"]) > max_history:
                self.metrics_history["hourly"] = self.metrics_history["hourly"][-max_history:]
            
            # Save to state manager
            await self.state_manager.store_analytics_data("aggregated_metrics", current_metrics)
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {e}")
    
    async def _load_historical_metrics(self):
        """Load historical metrics from storage"""
        try:
            # Load from state manager
            historical_data = await self.state_manager.get_analytics_data("aggregated_metrics")
            
            if historical_data:
                self.metrics_history["hourly"] = historical_data.get("hourly", [])
                
            self.logger.info(f"Loaded {len(self.metrics_history['hourly'])} historical metric records")
            
        except Exception as e:
            self.logger.error(f"Error loading historical metrics: {e}")
    
    async def _save_metrics(self):
        """Save current metrics to storage"""
        try:
            # Save metrics history
            await self.state_manager.store_analytics_data(
                "metrics_history", 
                self.metrics_history
            )
            
            # Save performance metrics
            await self.state_manager.store_analytics_data(
                "analytics_performance", 
                self.performance_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    async def generate_analytics_report(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAY,
        include_trends: bool = True,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            # Get all metrics
            conversation_metrics = await self.get_conversation_metrics(timeframe)
            agent_metrics = await self.get_agent_performance_metrics(timeframe=timeframe)
            anxiety_analytics = await self.get_anxiety_analytics(timeframe)
            user_engagement = await self.get_user_engagement_metrics(timeframe)
            system_performance = await self.get_system_performance_metrics()
            
            # Create report
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "timeframe": timeframe.value,
                    "includes_trends": include_trends,
                    "includes_recommendations": include_recommendations
                },
                "executive_summary": {
                    "total_conversations": conversation_metrics.total_conversations,
                    "completion_rate": conversation_metrics.completion_rate,
                    "average_anxiety_escalation": anxiety_analytics.average_escalation_rate,
                    "user_engagement_score": user_engagement.engagement_score,
                    "system_health": "healthy" if system_performance.get("analytics_service", {}).get("is_running") else "needs_attention"
                },
                "conversation_analysis": {
                    "metrics": conversation_metrics,
                    "key_insights": self._generate_conversation_insights(conversation_metrics)
                },
                "agent_performance": {
                    "metrics": agent_metrics,
                    "top_performers": agent_metrics[:3],
                    "improvement_opportunities": [m for m in agent_metrics if m.effectiveness_rating < 0.7]
                },
                "anxiety_progression": {
                    "analytics": anxiety_analytics,
                    "escalation_patterns": anxiety_analytics.common_escalation_patterns,
                    "effectiveness_score": anxiety_analytics.escalation_success_rate
                },
                "user_engagement": {
                    "metrics": user_engagement,
                    "retention_analysis": self._generate_retention_insights(user_engagement)
                },
                "system_performance": {
                    "metrics": system_performance,
                    "health_indicators": await self._get_system_alerts()
                }
            }
            
            # Add trends if requested
            if include_trends:
                report["trends"] = {
                    "conversation_trends": await self.get_historical_trends(
                        MetricType.CONVERSATION_METRICS, timeframe
                    ),
                    "anxiety_trends": await self.get_historical_trends(
                        MetricType.ANXIETY_ANALYTICS, timeframe
                    )
                }
            
            # Add recommendations if requested
            if include_recommendations:
                report["recommendations"] = await self._generate_recommendations(
                    conversation_metrics, agent_metrics, anxiety_analytics, user_engagement
                )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {e}")
            return {"error": str(e)}
    
    def _generate_conversation_insights(self, metrics: ConversationMetrics) -> List[str]:
        """Generate insights from conversation metrics"""
        insights = []
        
        if metrics.completion_rate > 0.8:
            insights.append("High conversation completion rate indicates strong user engagement")
        elif metrics.completion_rate < 0.5:
            insights.append("Low completion rate suggests conversations may be too long or not engaging enough")
        
        if metrics.average_anxiety_escalation > 3:
            insights.append("Agents are successfully escalating anxiety levels")
        elif metrics.average_anxiety_escalation < 2:
            insights.append("Anxiety escalation may need improvement - consider agent training")
        
        if metrics.average_message_count > 15:
            insights.append("Conversations are lengthy - consider optimizing for more efficient escalation")
        elif metrics.average_message_count < 5:
            insights.append("Conversations are brief - there may be room for deeper engagement")
        
        return insights
    
    def _generate_retention_insights(self, metrics: UserEngagementMetrics) -> List[str]:
        """Generate insights from user engagement metrics"""
        insights = []
        
        if metrics.user_retention_rate > 0.6:
            insights.append("Strong user retention indicates compelling user experience")
        elif metrics.user_retention_rate < 0.3:
            insights.append("Low retention suggests need for improved first-time user experience")
        
        if metrics.average_conversations_per_user > 3:
            insights.append("Users are highly engaged with multiple conversations")
        elif metrics.average_conversations_per_user < 1.5:
            insights.append("Users typically have single conversations - consider re-engagement strategies")
        
        return insights
    
    async def _generate_recommendations(
        self,
        conversation_metrics: ConversationMetrics,
        agent_metrics: List[AgentPerformanceMetrics],
        anxiety_analytics: AnxietyAnalytics,
        user_engagement: UserEngagementMetrics
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Conversation optimization
        if conversation_metrics.completion_rate < 0.7:
            recommendations.append({
                "category": "conversation_optimization",
                "priority": "high",
                "title": "Improve Conversation Completion Rate",
                "description": f"Current completion rate is {conversation_metrics.completion_rate:.1%}. Consider shorter conversations or better engagement techniques.",
                "action_items": [
                    "Analyze drop-off points in conversations",
                    "Implement conversation length optimization",
                    "Add engagement hooks at critical points"
                ]
            })
        
        # Agent performance
        underperforming_agents = [a for a in agent_metrics if a.effectiveness_rating < 0.6]
        if underperforming_agents:
            recommendations.append({
                "category": "agent_performance",
                "priority": "medium",
                "title": "Improve Underperforming Agents",
                "description": f"{len(underperforming_agents)} agents have effectiveness ratings below 60%.",
                "action_items": [
                    "Review agent prompt engineering",
                    "Analyze successful agent patterns",
                    "Implement agent performance monitoring"
                ]
            })
        
        # Anxiety escalation
        if anxiety_analytics.escalation_success_rate < 0.8:
            recommendations.append({
                "category": "anxiety_escalation",
                "priority": "high",
                "title": "Optimize Anxiety Escalation",
                "description": f"Escalation success rate is {anxiety_analytics.escalation_success_rate:.1%}. This is the core functionality.",
                "action_items": [
                    "Analyze successful escalation patterns",
                    "Improve agent coordination",
                    "Implement escalation effectiveness tracking"
                ]
            })
        
        # User engagement
        if user_engagement.engagement_score < 0.7:
            recommendations.append({
                "category": "user_engagement",
                "priority": "medium",
                "title": "Boost User Engagement",
                "description": f"Current engagement score is {user_engagement.engagement_score:.1%}.",
                "action_items": [
                    "Implement personalization features",
                    "Add gamification elements",
                    "Improve user onboarding experience"
                ]
            })
        
        # System performance
        system_performance = await self.get_system_performance_metrics()
        error_rate = system_performance.get("analytics_service", {}).get("error_rate", 0)
        if error_rate > 0.05:
            recommendations.append({
                "category": "system_performance",
                "priority": "high",
                "title": "Reduce System Error Rate",
                "description": f"Current error rate is {error_rate:.1%}. This affects user experience.",
                "action_items": [
                    "Implement better error handling",
                    "Add system monitoring alerts",
                    "Improve fault tolerance"
                ]
            })
        
        return recommendations
    
    async def export_analytics_data(
        self, 
        timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEK,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export analytics data for external analysis"""
        try:
            # Get comprehensive data
            export_data = {
                "export_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "timeframe": timeframe.value,
                    "format": format
                },
                "conversation_metrics": await self.get_conversation_metrics(timeframe),
                "agent_performance": await self.get_agent_performance_metrics(timeframe=timeframe),
                "anxiety_analytics": await self.get_anxiety_analytics(timeframe),
                "user_engagement": await self.get_user_engagement_metrics(timeframe),
                "system_performance": await self.get_system_performance_metrics(),
                "historical_trends": {
                    "conversations": await self.get_historical_trends(MetricType.CONVERSATION_METRICS, timeframe),
                    "anxiety": await self.get_historical_trends(MetricType.ANXIETY_ANALYTICS, timeframe)
                }
            }
            
            # Convert to requested format
            if format == "json":
                return export_data
            elif format == "csv":
                # Convert to CSV format (simplified)
                return {"message": "CSV export not implemented yet", "data": export_data}
            else:
                return {"error": f"Unsupported export format: {format}"}
                
        except Exception as e:
            self.logger.error(f"Error exporting analytics data: {e}")
            return {"error": str(e)}
    
    async def get_custom_analytics(
        self, 
        custom_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get custom analytics based on user-defined query"""
        try:
            # This would implement custom analytics queries
            # For now, return a placeholder
            return {
                "custom_query": custom_query,
                "message": "Custom analytics not implemented yet",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing custom analytics: {e}")
            return {"error": str(e)}


# Global analytics service instance
analytics_service = None

async def initialize_analytics_service(
    state_manager: StateManager,
    anxiety_tracker: AnxietyTracker = None
) -> AnalyticsService:
    """Initialize global analytics service"""
    global analytics_service
    
    if analytics_service is None:
        analytics_service = AnalyticsService(state_manager, anxiety_tracker)
        await analytics_service.initialize()
    
    return analytics_service


# Export
__all__ = [
    "AnalyticsService",
    "AnalyticsTimeframe",
    "MetricType",
    "ConversationMetrics",
    "AgentPerformanceMetrics",
    "AnxietyAnalytics",
    "UserEngagementMetrics",
    "initialize_analytics_service",
    "analytics_service"
]