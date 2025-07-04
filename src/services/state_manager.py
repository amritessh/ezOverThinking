"""
StateManager - Redis-based State Management Service
This service handles all real-time state management for conversations,
agent states, and user sessions using Redis for performance and scalability.

File: src/services/state_manager.py
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import asdict
import redis.asyncio as redis
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from ..models.schemas import (
    ConversationState,
    ConversationStatus,
    AnxietyLevel,
    AgentInteraction,
    UserConcern,
    AgentResponse
)
from ..agents.base_agent import AgentState


class StateManager:
    """
    Redis-based state management service for real-time conversation tracking
    and agent state management.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "ezoverthinking:",
        ttl_seconds: int = 3600  # 1 hour default TTL
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds
        self.redis: Optional[Redis] = None
        self.logger = logging.getLogger("StateManager")
        
        # Key patterns for different data types
        self.key_patterns = {
            "conversation": f"{key_prefix}conv:{{conversation_id}}",
            "user_session": f"{key_prefix}user:{{user_id}}",
            "agent_state": f"{key_prefix}agent:{{agent_id}}",
            "interaction": f"{key_prefix}interaction:{{interaction_id}}",
            "analytics": f"{key_prefix}analytics:{{metric_type}}:{{date}}",
            "cache": f"{key_prefix}cache:{{cache_key}}",
            "lock": f"{key_prefix}lock:{{resource_id}}",
            "queue": f"{key_prefix}queue:{{queue_name}}"
        }
        
        # Performance metrics
        self.metrics = {
            "operations_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "average_response_time": 0.0
        }
    
    async def connect(self) -> bool:
        """Connect to Redis server"""
        try:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis.ping()
            self.logger.info("Connected to Redis successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            self.logger.info("Disconnected from Redis")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis connection"""
        try:
            if not self.redis:
                return {"status": "disconnected", "error": "Not connected to Redis"}
            
            # Test basic operations
            test_key = f"{self.key_prefix}health_check"
            await self.redis.set(test_key, "test", ex=10)
            test_value = await self.redis.get(test_key)
            await self.redis.delete(test_key)
            
            if test_value == "test":
                return {
                    "status": "healthy",
                    "connected": True,
                    "metrics": self.metrics
                }
            else:
                return {"status": "unhealthy", "error": "Redis operations failed"}
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    @asynccontextmanager
    async def distributed_lock(self, resource_id: str, timeout: int = 30):
        """Distributed lock for preventing race conditions"""
        lock_key = self.key_patterns["lock"].format(resource_id=resource_id)
        lock_value = str(datetime.now().timestamp())
        
        try:
            # Acquire lock
            acquired = await self.redis.set(
                lock_key, 
                lock_value, 
                nx=True, 
                ex=timeout
            )
            
            if not acquired:
                raise Exception(f"Could not acquire lock for {resource_id}")
            
            self.logger.debug(f"Acquired lock for {resource_id}")
            yield
            
        finally:
            # Release lock
            try:
                # Use Lua script to safely release lock
                lua_script = """
                if redis.call("GET", KEYS[1]) == ARGV[1] then
                    return redis.call("DEL", KEYS[1])
                else
                    return 0
                end
                """
                await self.redis.eval(lua_script, 1, lock_key, lock_value)
                self.logger.debug(f"Released lock for {resource_id}")
            except Exception as e:
                self.logger.error(f"Error releasing lock for {resource_id}: {e}")
    
    # Conversation State Management
    async def store_conversation_state(
        self, 
        conversation_id: str, 
        state: ConversationState
    ) -> bool:
        """Store conversation state in Redis"""
        try:
            async with self.distributed_lock(f"conv_store_{conversation_id}"):
                key = self.key_patterns["conversation"].format(
                    conversation_id=conversation_id
                )
                
                # Convert state to dict for JSON serialization
                state_dict = self._serialize_conversation_state(state)
                
                # Store with TTL
                await self.redis.setex(
                    key, 
                    self.ttl_seconds, 
                    json.dumps(state_dict, default=str)
                )
                
                self.metrics["operations_count"] += 1
                self.logger.debug(f"Stored conversation state: {conversation_id}")
                return True
                
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error storing conversation state: {e}")
            return False
    
    async def get_conversation_state(
        self, 
        conversation_id: str
    ) -> Optional[ConversationState]:
        """Get conversation state from Redis"""
        try:
            key = self.key_patterns["conversation"].format(
                conversation_id=conversation_id
            )
            
            state_json = await self.redis.get(key)
            if state_json:
                self.metrics["cache_hits"] += 1
                state_dict = json.loads(state_json)
                return self._deserialize_conversation_state(state_dict)
            else:
                self.metrics["cache_misses"] += 1
                return None
                
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error getting conversation state: {e}")
            return None
    
    async def update_conversation_state(
        self, 
        conversation_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Update specific fields in conversation state"""
        try:
            async with self.distributed_lock(f"conv_update_{conversation_id}"):
                # Get current state
                current_state = await self.get_conversation_state(conversation_id)
                if not current_state:
                    return False
                
                # Apply updates
                for key, value in updates.items():
                    if hasattr(current_state, key):
                        setattr(current_state, key, value)
                
                # Update timestamp
                current_state.updated_at = datetime.now()
                
                # Store updated state
                return await self.store_conversation_state(conversation_id, current_state)
                
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error updating conversation state: {e}")
            return False
    
    async def delete_conversation_state(self, conversation_id: str) -> bool:
        """Delete conversation state from Redis"""
        try:
            key = self.key_patterns["conversation"].format(
                conversation_id=conversation_id
            )
            
            result = await self.redis.delete(key)
            self.logger.debug(f"Deleted conversation state: {conversation_id}")
            return result > 0
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error deleting conversation state: {e}")
            return False
    
    # User Session Management
    async def store_user_session(
        self, 
        user_id: str, 
        session_data: Dict[str, Any]
    ) -> bool:
        """Store user session data"""
        try:
            key = self.key_patterns["user_session"].format(user_id=user_id)
            
            # Add timestamp
            session_data["last_activity"] = datetime.now().isoformat()
            
            await self.redis.setex(
                key,
                self.ttl_seconds,
                json.dumps(session_data, default=str)
            )
            
            self.logger.debug(f"Stored user session: {user_id}")
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error storing user session: {e}")
            return False
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        try:
            key = self.key_patterns["user_session"].format(user_id=user_id)
            
            session_json = await self.redis.get(key)
            if session_json:
                self.metrics["cache_hits"] += 1
                return json.loads(session_json)
            else:
                self.metrics["cache_misses"] += 1
                return None
                
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error getting user session: {e}")
            return None
    
    async def update_user_activity(self, user_id: str) -> bool:
        """Update user's last activity timestamp"""
        try:
            session_data = await self.get_user_session(user_id)
            if not session_data:
                session_data = {}
            
            session_data["last_activity"] = datetime.now().isoformat()
            return await self.store_user_session(user_id, session_data)
            
        except Exception as e:
            self.logger.error(f"Error updating user activity: {e}")
            return False
    
    # Agent State Management
    async def store_agent_state(
        self, 
        agent_id: str, 
        state: AgentState,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store agent state"""
        try:
            key = self.key_patterns["agent_state"].format(agent_id=agent_id)
            
            state_data = {
                "state": state.value,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            await self.redis.setex(
                key,
                self.ttl_seconds,
                json.dumps(state_data, default=str)
            )
            
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error storing agent state: {e}")
            return False
    
    async def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state"""
        try:
            key = self.key_patterns["agent_state"].format(agent_id=agent_id)
            
            state_json = await self.redis.get(key)
            if state_json:
                return json.loads(state_json)
            else:
                return None
                
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error getting agent state: {e}")
            return None
    
    # Interaction Tracking
    async def store_interaction(
        self, 
        interaction: AgentInteraction
    ) -> bool:
        """Store agent interaction"""
        try:
            key = self.key_patterns["interaction"].format(
                interaction_id=interaction.interaction_id
            )
            
            # Convert interaction to dict
            interaction_dict = {
                "interaction_id": interaction.interaction_id,
                "conversation_id": interaction.conversation_id,
                "source_agent_id": interaction.source_agent_id,
                "target_agent_id": interaction.target_agent_id,
                "interaction_type": interaction.interaction_type,
                "content": interaction.content,
                "anxiety_before": interaction.anxiety_before.value,
                "anxiety_after": interaction.anxiety_after.value,
                "success": interaction.success,
                "timestamp": interaction.timestamp.isoformat(),
                "metadata": interaction.metadata
            }
            
            await self.redis.setex(
                key,
                self.ttl_seconds,
                json.dumps(interaction_dict, default=str)
            )
            
            # Also add to conversation's interaction list
            await self._add_interaction_to_conversation(
                interaction.conversation_id,
                interaction.interaction_id
            )
            
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error storing interaction: {e}")
            return False
    
    async def _add_interaction_to_conversation(
        self, 
        conversation_id: str, 
        interaction_id: str
    ):
        """Add interaction ID to conversation's interaction list"""
        try:
            list_key = f"{self.key_patterns['conversation'].format(conversation_id=conversation_id)}:interactions"
            await self.redis.lpush(list_key, interaction_id)
            await self.redis.expire(list_key, self.ttl_seconds)
            
        except Exception as e:
            self.logger.error(f"Error adding interaction to conversation: {e}")
    
    async def get_conversation_interactions(
        self, 
        conversation_id: str
    ) -> List[AgentInteraction]:
        """Get all interactions for a conversation"""
        try:
            list_key = f"{self.key_patterns['conversation'].format(conversation_id=conversation_id)}:interactions"
            interaction_ids = await self.redis.lrange(list_key, 0, -1)
            
            interactions = []
            for interaction_id in interaction_ids:
                interaction_key = self.key_patterns["interaction"].format(
                    interaction_id=interaction_id
                )
                interaction_json = await self.redis.get(interaction_key)
                if interaction_json:
                    interaction_dict = json.loads(interaction_json)
                    interactions.append(self._deserialize_interaction(interaction_dict))
            
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error getting conversation interactions: {e}")
            return []
    
    # Analytics and Metrics
    async def store_analytics_data(
        self, 
        metric_type: str, 
        data: Dict[str, Any],
        date: str = None
    ) -> bool:
        """Store analytics data"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            key = self.key_patterns["analytics"].format(
                metric_type=metric_type,
                date=date
            )
            
            await self.redis.setex(
                key,
                86400 * 7,  # 7 days TTL for analytics
                json.dumps(data, default=str)
            )
            
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Error storing analytics data: {e}")
            return False
    
    async def get_analytics_data(
        self, 
        metric_type: str, 
        date: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get analytics data"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            key = self.key_patterns["analytics"].format(
                metric_type=metric_type,
                date=date
            )
            
            data_json = await self.redis.get(key)
            if data_json:
                return json.loads(data_json)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting analytics data: {e}")
            return None
    
    # Cache Operations
    async def cache_set(
        self, 
        cache_key: str, 
        value: Any, 
        ttl: int = None
    ) -> bool:
        """Set cache value"""
        try:
            key = self.key_patterns["cache"].format(cache_key=cache_key)
            ttl = ttl or self.ttl_seconds
            
            await self.redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting cache: {e}")
            return False
    
    async def cache_get(self, cache_key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            key = self.key_patterns["cache"].format(cache_key=cache_key)
            
            value_json = await self.redis.get(key)
            if value_json:
                self.metrics["cache_hits"] += 1
                return json.loads(value_json)
            else:
                self.metrics["cache_misses"] += 1
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting cache: {e}")
            return None
    
    async def cache_delete(self, cache_key: str) -> bool:
        """Delete cache value"""
        try:
            key = self.key_patterns["cache"].format(cache_key=cache_key)
            result = await self.redis.delete(key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Error deleting cache: {e}")
            return False
    
    # Queue Operations
    async def queue_push(self, queue_name: str, item: Any) -> bool:
        """Push item to queue"""
        try:
            key = self.key_patterns["queue"].format(queue_name=queue_name)
            await self.redis.lpush(key, json.dumps(item, default=str))
            return True
            
        except Exception as e:
            self.logger.error(f"Error pushing to queue: {e}")
            return False
    
    async def queue_pop(self, queue_name: str, timeout: int = 0) -> Optional[Any]:
        """Pop item from queue"""
        try:
            key = self.key_patterns["queue"].format(queue_name=queue_name)
            
            if timeout > 0:
                result = await self.redis.brpop(key, timeout=timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = await self.redis.rpop(key)
                if result:
                    return json.loads(result)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error popping from queue: {e}")
            return None
    
    # Utility Methods
    def _serialize_conversation_state(self, state: ConversationState) -> Dict[str, Any]:
        """Serialize conversation state for Redis storage"""
        return {
            "conversation_id": state.conversation_id,
            "user_id": state.user_id,
            "status": state.status.value,
            "current_anxiety_level": state.current_anxiety_level.value,
            "last_active_agent": state.last_active_agent,
            "message_count": state.message_count,
            "escalation_count": state.escalation_count,
            "agents_involved": state.agents_involved,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
            "expires_at": state.expires_at.isoformat() if state.expires_at else None,
            "context": state.context
        }
    
    def _deserialize_conversation_state(self, state_dict: Dict[str, Any]) -> ConversationState:
        """Deserialize conversation state from Redis"""
        return ConversationState(
            conversation_id=state_dict["conversation_id"],
            user_id=state_dict["user_id"],
            status=ConversationStatus(state_dict["status"]),
            current_anxiety_level=AnxietyLevel(state_dict["current_anxiety_level"]),
            last_active_agent=state_dict.get("last_active_agent"),
            message_count=state_dict["message_count"],
            escalation_count=state_dict["escalation_count"],
            agents_involved=state_dict["agents_involved"],
            created_at=datetime.fromisoformat(state_dict["created_at"]),
            updated_at=datetime.fromisoformat(state_dict["updated_at"]),
            expires_at=datetime.fromisoformat(state_dict["expires_at"]) if state_dict.get("expires_at") else None,
            context=state_dict["context"]
        )
    
    def _deserialize_interaction(self, interaction_dict: Dict[str, Any]) -> AgentInteraction:
        """Deserialize agent interaction from Redis"""
        return AgentInteraction(
            interaction_id=interaction_dict["interaction_id"],
            conversation_id=interaction_dict["conversation_id"],
            source_agent_id=interaction_dict["source_agent_id"],
            target_agent_id=interaction_dict.get("target_agent_id"),
            interaction_type=interaction_dict["interaction_type"],
            content=interaction_dict["content"],
            anxiety_before=AnxietyLevel(interaction_dict["anxiety_before"]),
            anxiety_after=AnxietyLevel(interaction_dict["anxiety_after"]),
            success=interaction_dict["success"],
            timestamp=datetime.fromisoformat(interaction_dict["timestamp"]),
            metadata=interaction_dict["metadata"]
        )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            # Redis info
            redis_info = await self.redis.info()
            
            # Our metrics
            system_metrics = {
                "state_manager_metrics": self.metrics,
                "redis_connected_clients": redis_info.get("connected_clients", 0),
                "redis_used_memory": redis_info.get("used_memory_human", "0B"),
                "redis_operations_per_sec": redis_info.get("instantaneous_ops_per_sec", 0),
                "cache_hit_rate": (
                    self.metrics["cache_hits"] / 
                    (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                ) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0,
                "error_rate": (
                    self.metrics["errors"] / 
                    max(1, self.metrics["operations_count"])
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            return system_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data (manual cleanup for non-TTL keys)"""
        try:
            cleanup_stats = {
                "conversations_cleaned": 0,
                "interactions_cleaned": 0,
                "sessions_cleaned": 0
            }
            
            # This would typically be done by Redis TTL, but we can do manual cleanup
            # for specific patterns if needed
            
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.redis:
                await self.redis.close()
            self.logger.info("StateManager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during StateManager cleanup: {e}")

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions and conversation states"""
        try:
            # Get all session keys
            session_keys = await self.redis.keys("session:*")
            conversation_keys = await self.redis.keys("conversation:*")
            
            current_time = datetime.now()
            expired_count = 0
            
            # Check session expiration
            for key in session_keys:
                session_data = await self.redis.get(key)
                if session_data:
                    session = json.loads(session_data)
                    if "expires_at" in session:
                        expires_at = datetime.fromisoformat(session["expires_at"])
                        if current_time > expires_at:
                            await self.redis.delete(key)
                            expired_count += 1
            
            # Check conversation expiration (older than 24 hours)
            for key in conversation_keys:
                conversation_data = await self.redis.get(key)
                if conversation_data:
                    conversation = json.loads(conversation_data)
                    if "created_at" in conversation:
                        created_at = datetime.fromisoformat(conversation["created_at"])
                        if current_time - created_at > timedelta(hours=24):
                            await self.redis.delete(key)
                            expired_count += 1
            
            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired sessions/conversations")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")


# Global state manager instance
state_manager = StateManager()

# Export
__all__ = ["StateManager", "state_manager"]