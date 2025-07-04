"""
AnxietyTracker - Real-time Anxiety Level Monitoring
This service tracks anxiety levels throughout conversations, providing
real-time monitoring, progression analysis, and escalation alerts.

File: src/services/anxiety_tracker.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

from .state_manager import StateManager
from ..models.schemas import AnxietyLevel, ConversationState


class AnxietyEvent(Enum):
    """Types of anxiety events"""
    INITIAL = "initial"
    ESCALATION = "escalation"
    DE_ESCALATION = "de_escalation"
    PLATEAU = "plateau"
    SPIKE = "spike"
    SUSTAINED_HIGH = "sustained_high"
    RECOVERY = "recovery"


class AnxietyTrend(Enum):
    """Anxiety trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class AnxietyDataPoint:
    """Individual anxiety measurement"""
    timestamp: datetime
    anxiety_level: AnxietyLevel
    agent_id: str
    event_type: AnxietyEvent
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnxietyProgression:
    """Anxiety progression analysis"""
    conversation_id: str
    data_points: List[AnxietyDataPoint]
    trend: AnxietyTrend
    average_level: float
    peak_level: AnxietyLevel
    escalation_rate: float
    volatility_score: float
    time_to_peak: Optional[float] = None
    sustained_high_duration: Optional[float] = None


class AnxietyTracker:
    """
    Real-time anxiety level monitoring and analysis system
    """
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.logger = logging.getLogger("AnxietyTracker")
        
        # Active tracking sessions
        self.active_sessions: Dict[str, List[AnxietyDataPoint]] = {}
        
        # Anxiety thresholds and configurations
        self.config = {
            "high_anxiety_threshold": 4,
            "escalation_threshold": 2,  # Level increase to trigger escalation event
            "volatility_threshold": 0.5,
            "sustained_high_duration": 300,  # 5 minutes
            "plateau_duration": 180,  # 3 minutes
            "spike_threshold": 3,  # Immediate jump of 3 levels
            "max_tracking_duration": 3600  # 1 hour
        }
        
        # Analytics data
        self.analytics = {
            "total_sessions": 0,
            "average_peak_anxiety": 0.0,
            "average_escalation_rate": 0.0,
            "common_escalation_patterns": [],
            "anxiety_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "trend_distribution": {trend.value: 0 for trend in AnxietyTrend},
            "event_counts": {event.value: 0 for event in AnxietyEvent}
        }
        
        # Alert callbacks
        self.alert_callbacks: List[callable] = []
    
    async def initialize(self) -> bool:
        """Initialize anxiety tracker"""
        try:
            # Load historical analytics if available
            await self._load_historical_analytics()
            
            self.logger.info("AnxietyTracker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing anxiety tracker: {e}")
            return False
    
    async def start_tracking(
        self, 
        conversation_id: str, 
        initial_anxiety: AnxietyLevel,
        agent_id: str = "system"
    ) -> bool:
        """Start tracking anxiety for a conversation"""
        try:
            # Create initial data point
            initial_point = AnxietyDataPoint(
                timestamp=datetime.now(),
                anxiety_level=initial_anxiety,
                agent_id=agent_id,
                event_type=AnxietyEvent.INITIAL
            )
            
            # Initialize tracking session
            self.active_sessions[conversation_id] = [initial_point]
            
            # Store in state manager
            await self._store_anxiety_data(conversation_id, initial_point)
            
            # Update analytics
            self.analytics["total_sessions"] += 1
            self.analytics["anxiety_distribution"][initial_anxiety.value] += 1
            self.analytics["event_counts"][AnxietyEvent.INITIAL.value] += 1
            
            self.logger.info(f"Started anxiety tracking for conversation: {conversation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting anxiety tracking: {e}")
            return False
    
    async def track_anxiety_change(
        self,
        conversation_id: str,
        old_level: AnxietyLevel,
        new_level: AnxietyLevel,
        agent_id: str = "unknown"
    ) -> bool:
        """Track anxiety level change"""
        try:
            if conversation_id not in self.active_sessions:
                self.logger.warning(f"No active tracking session for conversation: {conversation_id}")
                return False
            
            # Determine event type
            event_type = self._classify_anxiety_event(old_level, new_level)
            
            # Create data point
            data_point = AnxietyDataPoint(
                timestamp=datetime.now(),
                anxiety_level=new_level,
                agent_id=agent_id,
                event_type=event_type,
                metadata={
                    "previous_level": old_level.value,
                    "change": new_level.value - old_level.value,
                    "agent_responsible": agent_id
                }
            )
            
            # Add to session
            self.active_sessions[conversation_id].append(data_point)
            
            # Store in state manager
            await self._store_anxiety_data(conversation_id, data_point)
            
            # Update analytics
            self.analytics["anxiety_distribution"][new_level.value] += 1
            self.analytics["event_counts"][event_type.value] += 1
            
            # Check for alerts
            await self._check_anxiety_alerts(conversation_id, data_point)
            
            # Analyze patterns
            await self._analyze_anxiety_patterns(conversation_id)
            
            self.logger.debug(f"Tracked anxiety change: {old_level.value} -> {new_level.value} ({event_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking anxiety change: {e}")
            return False
    
    async def get_anxiety_progression(
        self, 
        conversation_id: str
    ) -> Optional[AnxietyProgression]:
        """Get anxiety progression analysis for a conversation"""
        try:
            if conversation_id not in self.active_sessions:
                # Try to load from state manager
                data_points = await self._load_anxiety_data(conversation_id)
                if not data_points:
                    return None
            else:
                data_points = self.active_sessions[conversation_id]
            
            if not data_points:
                return None
            
            # Calculate progression metrics
            progression = self._calculate_progression(conversation_id, data_points)
            return progression
            
        except Exception as e:
            self.logger.error(f"Error getting anxiety progression: {e}")
            return None
    
    async def get_real_time_anxiety(self, conversation_id: str) -> Optional[AnxietyLevel]:
        """Get current anxiety level for a conversation"""
        try:
            if conversation_id not in self.active_sessions:
                return None
            
            data_points = self.active_sessions[conversation_id]
            if not data_points:
                return None
            
            return data_points[-1].anxiety_level
            
        except Exception as e:
            self.logger.error(f"Error getting real-time anxiety: {e}")
            return None
    
    async def get_anxiety_trends(
        self, 
        conversation_id: str, 
        window_minutes: int = 10
    ) -> Dict[str, Any]:
        """Get anxiety trends within a time window"""
        try:
            if conversation_id not in self.active_sessions:
                return {}
            
            data_points = self.active_sessions[conversation_id]
            if not data_points:
                return {}
            
            # Filter to time window
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_points = [
                point for point in data_points 
                if point.timestamp >= cutoff_time
            ]
            
            if len(recent_points) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend
            levels = [point.anxiety_level.value for point in recent_points]
            
            # Linear regression for trend
            n = len(levels)
            x = list(range(n))
            slope = (n * sum(x[i] * levels[i] for i in range(n)) - sum(x) * sum(levels)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
            
            # Determine trend
            if slope > 0.1:
                trend = AnxietyTrend.INCREASING
            elif slope < -0.1:
                trend = AnxietyTrend.DECREASING
            else:
                trend = AnxietyTrend.STABLE
            
            # Calculate volatility
            volatility = statistics.stdev(levels) if len(levels) > 1 else 0
            
            return {
                "trend": trend.value,
                "slope": slope,
                "volatility": volatility,
                "current_level": recent_points[-1].anxiety_level.value,
                "min_level": min(levels),
                "max_level": max(levels),
                "average_level": sum(levels) / len(levels),
                "data_points": len(recent_points)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting anxiety trends: {e}")
            return {"error": str(e)}
    
    async def detect_anxiety_patterns(
        self, 
        conversation_id: str
    ) -> Dict[str, Any]:
        """Detect patterns in anxiety progression"""
        try:
            progression = await self.get_anxiety_progression(conversation_id)
            if not progression:
                return {}
            
            patterns = {
                "escalation_pattern": self._detect_escalation_pattern(progression),
                "plateau_periods": self._detect_plateau_periods(progression),
                "spike_events": self._detect_spike_events(progression),
                "recovery_periods": self._detect_recovery_periods(progression),
                "cycle_patterns": self._detect_cycle_patterns(progression)
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting anxiety patterns: {e}")
            return {"error": str(e)}
    
    def _classify_anxiety_event(
        self, 
        old_level: AnxietyLevel, 
        new_level: AnxietyLevel
    ) -> AnxietyEvent:
        """Classify the type of anxiety event"""
        change = new_level.value - old_level.value
        
        if change >= self.config["spike_threshold"]:
            return AnxietyEvent.SPIKE
        elif change >= self.config["escalation_threshold"]:
            return AnxietyEvent.ESCALATION
        elif change <= -self.config["escalation_threshold"]:
            return AnxietyEvent.DE_ESCALATION
        elif change == 0:
            return AnxietyEvent.PLATEAU
        elif change < 0:
            return AnxietyEvent.RECOVERY
        else:
            return AnxietyEvent.ESCALATION
    
    def _calculate_progression(
        self, 
        conversation_id: str, 
        data_points: List[AnxietyDataPoint]
    ) -> AnxietyProgression:
        """Calculate detailed anxiety progression analysis"""
        
        if not data_points:
            raise ValueError("No data points provided")
        
        # Basic metrics
        levels = [point.anxiety_level.value for point in data_points]
        timestamps = [point.timestamp for point in data_points]
        
        average_level = sum(levels) / len(levels)
        peak_level = AnxietyLevel(max(levels))
        
        # Calculate escalation rate (anxiety increase per minute)
        if len(data_points) > 1:
            total_time = (timestamps[-1] - timestamps[0]).total_seconds() / 60  # minutes
            total_escalation = levels[-1] - levels[0]
            escalation_rate = total_escalation / max(total_time, 1)
        else:
            escalation_rate = 0
        
        # Calculate volatility (standard deviation)
        volatility_score = statistics.stdev(levels) if len(levels) > 1 else 0
        
        # Determine trend
        trend = self._determine_trend(levels)
        
        # Time to peak
        time_to_peak = None
        peak_time = None
        for i, level in enumerate(levels):
            if level == peak_level.value:
                peak_time = timestamps[i]
                time_to_peak = (peak_time - timestamps[0]).total_seconds() / 60
                break
        
        # Sustained high duration
        sustained_high_duration = self._calculate_sustained_high_duration(
            data_points, self.config["high_anxiety_threshold"]
        )
        
        return AnxietyProgression(
            conversation_id=conversation_id,
            data_points=data_points,
            trend=trend,
            average_level=average_level,
            peak_level=peak_level,
            escalation_rate=escalation_rate,
            volatility_score=volatility_score,
            time_to_peak=time_to_peak,
            sustained_high_duration=sustained_high_duration
        )
    
    def _determine_trend(self, levels: List[int]) -> AnxietyTrend:
        """Determine overall anxiety trend"""
        if len(levels) < 2:
            return AnxietyTrend.STABLE
        
        # Calculate overall direction
        first_third = levels[:len(levels)//3] if len(levels) > 3 else levels[:1]
        last_third = levels[-len(levels)//3:] if len(levels) > 3 else levels[-1:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        change = last_avg - first_avg
        
        # Calculate volatility
        volatility = statistics.stdev(levels) if len(levels) > 1 else 0
        
        if volatility > self.config["volatility_threshold"]:
            return AnxietyTrend.VOLATILE
        elif change > 0.5:
            return AnxietyTrend.INCREASING
        elif change < -0.5:
            return AnxietyTrend.DECREASING
        else:
            return AnxietyTrend.STABLE
    
    def _calculate_sustained_high_duration(
        self, 
        data_points: List[AnxietyDataPoint], 
        threshold: int
    ) -> Optional[float]:
        """Calculate duration of sustained high anxiety"""
        high_periods = []
        current_period_start = None
        
        for point in data_points:
            if point.anxiety_level.value >= threshold:
                if current_period_start is None:
                    current_period_start = point.timestamp
            else:
                if current_period_start is not None:
                    duration = (point.timestamp - current_period_start).total_seconds() / 60
                    high_periods.append(duration)
                    current_period_start = None
        
        # Handle case where conversation ends with high anxiety
        if current_period_start is not None:
            duration = (data_points[-1].timestamp - current_period_start).total_seconds() / 60
            high_periods.append(duration)
        
        return max(high_periods) if high_periods else None
    
    async def _check_anxiety_alerts(
        self, 
        conversation_id: str, 
        data_point: AnxietyDataPoint
    ):
        """Check for anxiety alerts and trigger callbacks"""
        try:
            alerts = []
            
            # High anxiety alert
            if data_point.anxiety_level.value >= self.config["high_anxiety_threshold"]:
                alerts.append({
                    "type": "high_anxiety",
                    "level": data_point.anxiety_level.value,
                    "timestamp": data_point.timestamp.isoformat(),
                    "message": f"High anxiety level detected: {data_point.anxiety_level.value}"
                })
            
            # Spike alert
            if data_point.event_type == AnxietyEvent.SPIKE:
                alerts.append({
                    "type": "anxiety_spike",
                    "level": data_point.anxiety_level.value,
                    "change": data_point.metadata.get("change", 0),
                    "timestamp": data_point.timestamp.isoformat(),
                    "message": f"Anxiety spike detected: +{data_point.metadata.get('change', 0)} levels"
                })
            
            # Sustained high anxiety alert
            if conversation_id in self.active_sessions:
                sustained_duration = self._calculate_sustained_high_duration(
                    self.active_sessions[conversation_id][-10:],  # Last 10 points
                    self.config["high_anxiety_threshold"]
                )
                
                if sustained_duration and sustained_duration > self.config["sustained_high_duration"] / 60:
                    alerts.append({
                        "type": "sustained_high_anxiety",
                        "duration_minutes": sustained_duration,
                        "timestamp": data_point.timestamp.isoformat(),
                        "message": f"Sustained high anxiety for {sustained_duration:.1f} minutes"
                    })
            
            # Trigger alert callbacks
            for alert in alerts:
                await self._trigger_alert_callbacks(conversation_id, alert)
                
        except Exception as e:
            self.logger.error(f"Error checking anxiety alerts: {e}")
    
    async def _trigger_alert_callbacks(
        self, 
        conversation_id: str, 
        alert: Dict[str, Any]
    ):
        """Trigger alert callbacks"""
        try:
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(conversation_id, alert)
                    else:
                        callback(conversation_id, alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error triggering alert callbacks: {e}")
    
    def add_alert_callback(self, callback: callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: callable):
        """Remove alert callback function"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    async def _analyze_anxiety_patterns(self, conversation_id: str):
        """Analyze anxiety patterns for learning"""
        try:
            if conversation_id not in self.active_sessions:
                return
            
            data_points = self.active_sessions[conversation_id]
            if len(data_points) < 3:
                return
            
            # Look for common patterns
            recent_events = [point.event_type for point in data_points[-5:]]
            
            # Update common patterns
            pattern_key = "->".join([event.value for event in recent_events])
            if pattern_key not in self.analytics["common_escalation_patterns"]:
                self.analytics["common_escalation_patterns"].append(pattern_key)
            
        except Exception as e:
            self.logger.error(f"Error analyzing anxiety patterns: {e}")
    
    def _detect_escalation_pattern(self, progression: AnxietyProgression) -> Dict[str, Any]:
        """Detect escalation patterns in anxiety progression"""
        if not progression.data_points:
            return {}
        
        escalation_events = [
            point for point in progression.data_points 
            if point.event_type == AnxietyEvent.ESCALATION
        ]
        
        if not escalation_events:
            return {"pattern": "no_escalation"}
        
        # Analyze escalation timing
        escalation_intervals = []
        for i in range(1, len(escalation_events)):
            interval = (escalation_events[i].timestamp - escalation_events[i-1].timestamp).total_seconds() / 60
            escalation_intervals.append(interval)
        
        if escalation_intervals:
            avg_interval = sum(escalation_intervals) / len(escalation_intervals)
            pattern_type = "regular" if statistics.stdev(escalation_intervals) < 2 else "irregular"
        else:
            avg_interval = 0
            pattern_type = "single"
        
        return {
            "pattern": pattern_type,
            "escalation_count": len(escalation_events),
            "average_interval_minutes": avg_interval,
            "escalation_rate": progression.escalation_rate
        }
    
    def _detect_plateau_periods(self, progression: AnxietyProgression) -> List[Dict[str, Any]]:
        """Detect plateau periods in anxiety levels"""
        plateaus = []
        current_plateau = None
        
        for i, point in enumerate(progression.data_points):
            if point.event_type == AnxietyEvent.PLATEAU:
                if current_plateau is None:
                    current_plateau = {
                        "start_time": point.timestamp,
                        "level": point.anxiety_level.value,
                        "duration": 0
                    }
                else:
                    current_plateau["duration"] = (point.timestamp - current_plateau["start_time"]).total_seconds() / 60
            else:
                if current_plateau is not None:
                    if current_plateau["duration"] > self.config["plateau_duration"] / 60:
                        plateaus.append(current_plateau)
                    current_plateau = None
        
        return plateaus
    
    def _detect_spike_events(self, progression: AnxietyProgression) -> List[Dict[str, Any]]:
        """Detect anxiety spike events"""
        spikes = []
        
        for point in progression.data_points:
            if point.event_type == AnxietyEvent.SPIKE:
                spikes.append({
                    "timestamp": point.timestamp.isoformat(),
                    "level": point.anxiety_level.value,
                    "change": point.metadata.get("change", 0),
                    "agent_responsible": point.metadata.get("agent_responsible", "unknown")
                })
        
        return spikes
    
    def _detect_recovery_periods(self, progression: AnxietyProgression) -> List[Dict[str, Any]]:
        """Detect anxiety recovery periods"""
        recoveries = []
        
        for point in progression.data_points:
            if point.event_type == AnxietyEvent.RECOVERY:
                recoveries.append({
                    "timestamp": point.timestamp.isoformat(),
                    "level": point.anxiety_level.value,
                    "change": point.metadata.get("change", 0),
                    "agent_responsible": point.metadata.get("agent_responsible", "unknown")
                })
        
        return recoveries
    
    def _detect_cycle_patterns(self, progression: AnxietyProgression) -> Dict[str, Any]:
        """Detect cyclical patterns in anxiety levels"""
        if len(progression.data_points) < 6:
            return {"pattern": "insufficient_data"}
        
        levels = [point.anxiety_level.value for point in progression.data_points]
        
        # Simple cycle detection - look for repeated patterns
        cycle_length = 0
        for length in range(2, len(levels) // 2):
            if self._is_cycle(levels, length):
                cycle_length = length
                break
        
        if cycle_length > 0:
            return {
                "pattern": "cyclical",
                "cycle_length": cycle_length,
                "confidence": 0.8
            }
        else:
            return {"pattern": "non_cyclical"}
    
    def _is_cycle(self, levels: List[int], length: int) -> bool:
        """Check if levels contain a cycle of given length"""
        if len(levels) < length * 2:
            return False
        
        # Check if pattern repeats
        for i in range(length, len(levels)):
            if levels[i] != levels[i % length]:
                return False
        
        return True
    
    async def _store_anxiety_data(
        self, 
        conversation_id: str, 
        data_point: AnxietyDataPoint
    ):
        """Store anxiety data point in state manager"""
        try:
            key = f"anxiety_data_{conversation_id}"
            data = {
                "timestamp": data_point.timestamp.isoformat(),
                "anxiety_level": data_point.anxiety_level.value,
                "agent_id": data_point.agent_id,
                "event_type": data_point.event_type.value,
                "metadata": data_point.metadata
            }
            
            # Use queue to store sequential data points
            await self.state_manager.queue_push(key, data)
            
        except Exception as e:
            self.logger.error(f"Error storing anxiety data: {e}")
    
    async def _load_anxiety_data(
        self, 
        conversation_id: str
    ) -> List[AnxietyDataPoint]:
        """Load anxiety data from state manager"""
        try:
            key = f"anxiety_data_{conversation_id}"
            data_points = []
            
            # Load all data points from queue
            while True:
                data = await self.state_manager.queue_pop(key)
                if data is None:
                    break
                
                data_point = AnxietyDataPoint(
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    anxiety_level=AnxietyLevel(data["anxiety_level"]),
                    agent_id=data["agent_id"],
                    event_type=AnxietyEvent(data["event_type"]),
                    metadata=data["metadata"]
                )
                data_points.append(data_point)
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error loading anxiety data: {e}")
            return []
    
    async def _load_historical_analytics(self):
        """Load historical analytics data"""
        try:
            # Load analytics from state manager
            analytics_data = await self.state_manager.get_analytics_data("anxiety_tracker")
            
            if analytics_data:
                self.analytics.update(analytics_data)
                
        except Exception as e:
            self.logger.error(f"Error loading historical analytics: {e}")
    
    async def _save_analytics(self):
        """Save analytics data to state manager"""
        try:
            await self.state_manager.store_analytics_data("anxiety_tracker", self.analytics)
            
        except Exception as e:
            self.logger.error(f"Error saving analytics: {e}")
    
    async def end_tracking(self, conversation_id: str) -> bool:
        """End anxiety tracking for a conversation"""
        try:
            if conversation_id in self.active_sessions:
                # Final analysis
                progression = await self.get_anxiety_progression(conversation_id)
                
                if progression:
                    # Update analytics
                    self.analytics["average_peak_anxiety"] = (
                        (self.analytics["average_peak_anxiety"] * (self.analytics["total_sessions"] - 1) + 
                         progression.peak_level.value) / self.analytics["total_sessions"]
                    )
                    
                    self.analytics["average_escalation_rate"] = (
                        (self.analytics["average_escalation_rate"] * (self.analytics["total_sessions"] - 1) + 
                         progression.escalation_rate) / self.analytics["total_sessions"]
                    )
                    
                    self.analytics["trend_distribution"][progression.trend.value] += 1
                
                # Clean up active session
                del self.active_sessions[conversation_id]
                
                # Save analytics
                await self._save_analytics()
                
                self.logger.info(f"Ended anxiety tracking for conversation: {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error ending anxiety tracking: {e}")
            return False
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide anxiety analytics"""
        try:
            # Add real-time metrics
            real_time_metrics = {
                "active_sessions": len(self.active_sessions),
                "current_high_anxiety_sessions": sum(
                    1 for session in self.active_sessions.values()
                    if session and session[-1].anxiety_level.value >= self.config["high_anxiety_threshold"]
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                **self.analytics,
                "real_time_metrics": real_time_metrics,
                "configuration": self.config
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system analytics: {e}")
            return {"error": str(e)}


# Export
__all__ = [
    "AnxietyTracker", 
    "AnxietyEvent", 
    "AnxietyTrend", 
    "AnxietyDataPoint", 
    "AnxietyProgression"
]