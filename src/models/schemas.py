from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, validator


class AnxietyLevel(Enum):
    """Enumeration for anxiety escalation levels"""

    MINIMAL = 1
    MILD = 2
    MODERATE = 3
    SEVERE = 4
    PANIC = 5


class WorryCategory(Enum):
    """Categories of worries that users might have"""

    SOCIAL = "social"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    FINANCES = "finances"
    TECHNOLOGY = "technology"
    EXISTENTIAL = "existential"
    GENERAL = "general"
    AGENT_COMMUNICATION = "agent_communication"


class ConversationStatus(Enum):
    """Status of a conversation"""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    ERROR = "error"


# ==========================================
# Request/Response Models
# ==========================================


class UserConcern(BaseModel):
    """Model for user input validation"""

    original_worry: str = Field(
        ..., description="The user's initial concern", min_length=1, max_length=1000
    )
    anxiety_level: AnxietyLevel = Field(
        default=AnxietyLevel.MINIMAL, description="Initial anxiety level"
    )
    category: WorryCategory = Field(
        default=WorryCategory.GENERAL, description="Category of worry"
    )
    user_id: str = Field(..., description="Unique user identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the concern was submitted"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("original_worry")
    def validate_worry(cls, v):
        if not v.strip():
            raise ValueError("Worry cannot be empty")
        return v.strip()

    @validator("user_id")
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            AnxietyLevel: lambda v: v.value,
            WorryCategory: lambda v: v.value,
        }


class AgentResponse(BaseModel):
    """Standardized response format for all agents"""

    agent_name: str = Field(
        ..., description="Name of the agent generating the response"
    )
    agent_id: str = Field(..., description="Unique identifier of the agent")
    response: str = Field(
        ..., description="The agent's response content", min_length=1, max_length=2000
    )
    anxiety_escalation: int = Field(
        ge=1, le=5, description="How much this response escalates anxiety (1-5)"
    )
    suggested_next_agents: List[str] = Field(
        default_factory=list, description="List of agent names to consider next"
    )
    confidence_score: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in the response quality"
    )
    processing_time: float = Field(
        default=0.0, ge=0.0, description="Time taken to generate response in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional response metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the response was generated"
    )

    @validator("response")
    def validate_response(cls, v):
        if not v.strip():
            raise ValueError("Response cannot be empty")
        return v.strip()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConversationMessage(BaseModel):
    """Individual message in a conversation"""

    id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique message identifier"
    )
    conversation_id: str = Field(
        ..., description="ID of the conversation this message belongs to"
    )
    sender_type: str = Field(..., description="Type of sender (user, agent, system)")
    sender_id: str = Field(..., description="ID of the sender")
    content: str = Field(
        ..., description="Message content", min_length=1, max_length=2000
    )
    anxiety_level: AnxietyLevel = Field(
        default=AnxietyLevel.MINIMAL, description="Anxiety level at time of message"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the message was created"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional message metadata"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            AnxietyLevel: lambda v: v.value,
        }


# ==========================================
# State Management Models
# ==========================================


class ConversationState(BaseModel):
    """Current state of a conversation"""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User participating in the conversation")
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE, description="Current conversation status"
    )
    current_anxiety_level: AnxietyLevel = Field(
        default=AnxietyLevel.MINIMAL, description="Current anxiety level"
    )
    last_active_agent: Optional[str] = Field(
        default=None, description="ID of the last agent to respond"
    )
    message_count: int = Field(
        default=0, ge=0, description="Number of messages in conversation"
    )
    escalation_count: int = Field(
        default=0, ge=0, description="Number of times anxiety has been escalated"
    )
    agents_involved: List[str] = Field(
        default_factory=list, description="List of agent IDs that have participated"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the conversation was last updated",
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="When the conversation expires"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Conversation context and metadata"
    )

    @validator("message_count", "escalation_count")
    def validate_counts(cls, v):
        return max(0, v)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            AnxietyLevel: lambda v: v.value,
            ConversationStatus: lambda v: v.value,
        }


class AgentInteraction(BaseModel):
    """Record of an interaction between agents"""

    interaction_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique interaction identifier",
    )
    conversation_id: str = Field(
        ..., description="Conversation this interaction belongs to"
    )
    source_agent_id: str = Field(
        ..., description="Agent that initiated the interaction"
    )
    target_agent_id: Optional[str] = Field(
        default=None, description="Agent that received the interaction"
    )
    interaction_type: str = Field(
        ..., description="Type of interaction (response, handoff, collaboration)"
    )
    content: str = Field(..., description="Interaction content or message")
    anxiety_before: AnxietyLevel = Field(
        ..., description="Anxiety level before interaction"
    )
    anxiety_after: AnxietyLevel = Field(
        ..., description="Anxiety level after interaction"
    )
    success: bool = Field(
        default=True, description="Whether the interaction was successful"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the interaction occurred"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional interaction metadata"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            AnxietyLevel: lambda v: v.value,
        }


# ==========================================
# Analytics Models
# ==========================================


class ConversationAnalytics(BaseModel):
    """Analytics data for a conversation"""

    conversation_id: str = Field(..., description="Conversation identifier")
    total_messages: int = Field(default=0, ge=0, description="Total number of messages")
    conversation_duration: float = Field(
        default=0.0, ge=0.0, description="Duration in seconds"
    )
    anxiety_progression: List[int] = Field(
        default_factory=list,
        description="List of anxiety levels throughout conversation",
    )
    agents_used: List[str] = Field(
        default_factory=list, description="List of agents that participated"
    )
    escalation_events: int = Field(
        default=0, ge=0, description="Number of escalation events"
    )
    user_satisfaction: Optional[float] = Field(
        default=None, ge=0.0, le=5.0, description="User satisfaction rating"
    )
    humor_effectiveness: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="How funny the user found the conversation",
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When analytics were generated"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AgentPerformanceMetrics(BaseModel):
    """Performance metrics for an individual agent"""

    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    total_interactions: int = Field(
        default=0, ge=0, description="Total number of interactions"
    )
    average_response_time: float = Field(
        default=0.0, ge=0.0, description="Average response time in seconds"
    )
    escalation_success_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Success rate of escalations"
    )
    user_engagement_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="How engaging users find this agent"
    )
    error_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Rate of errors or failed responses"
    )
    last_active: datetime = Field(
        default_factory=datetime.now, description="When agent was last active"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SystemAnalytics(BaseModel):
    """System-wide analytics data"""

    total_conversations: int = Field(
        default=0, ge=0, description="Total number of conversations"
    )
    active_conversations: int = Field(
        default=0, ge=0, description="Currently active conversations"
    )
    total_users: int = Field(default=0, ge=0, description="Total number of users")
    average_anxiety_level: float = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Average anxiety level across all users",
    )
    system_uptime: float = Field(
        default=0.0, ge=0.0, description="System uptime in seconds"
    )
    average_response_time: float = Field(
        default=0.0, ge=0.0, description="Average response time across all agents"
    )
    error_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall system error rate"
    )
    agent_performance: List[AgentPerformanceMetrics] = Field(
        default_factory=list, description="Performance metrics for all agents"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When analytics were generated"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==========================================
# API Request/Response Models
# ==========================================


class ChatRequest(BaseModel):
    """Request model for chat API"""

    message: str = Field(
        ..., description="User's message", min_length=1, max_length=1000
    )
    conversation_id: Optional[str] = Field(
        default=None, description="Existing conversation ID"
    )
    user_id: str = Field(..., description="User identifier")
    preferred_agent: Optional[str] = Field(
        default=None, description="Preferred agent to respond"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat API"""

    conversation_id: str = Field(..., description="Conversation identifier")
    message: str = Field(..., description="Agent's response message")
    agent_name: str = Field(..., description="Name of responding agent")
    anxiety_level: AnxietyLevel = Field(..., description="Current anxiety level")
    next_suggested_agents: List[str] = Field(
        default_factory=list, description="Suggested agents for next interaction"
    )
    conversation_status: ConversationStatus = Field(
        ..., description="Current conversation status"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            AnxietyLevel: lambda v: v.value,
            ConversationStatus: lambda v: v.value,
        }


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Health check timestamp"
    )
    services: Dict[str, bool] = Field(
        default_factory=dict, description="Status of individual services"
    )
    agents: Dict[str, bool] = Field(
        default_factory=dict, description="Status of individual agents"
    )
    version: str = Field(default="1.0.0", description="Application version")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==========================================
# Configuration Models
# ==========================================


class AgentConfig(BaseModel):
    """Configuration for an individual agent"""

    name: str = Field(..., description="Agent name")
    model_name: str = Field(
        default="gemini-1.5-flash", description="LLM model to use"
    )
    temperature: float = Field(
        default=0.8, ge=0.0, le=2.0, description="Response creativity level"
    )
    max_tokens: int = Field(
        default=2048, ge=1, le=4096, description="Maximum tokens in response"
    )
    escalation_factor: float = Field(
        default=1.2, ge=0.1, le=3.0, description="How much this agent escalates anxiety"
    )
    humor_level: float = Field(
        default=0.8, ge=0.0, le=1.0, description="How humorous the agent should be"
    )
    personality_traits: List[str] = Field(
        default_factory=list, description="List of personality traits"
    )
    custom_prompts: Dict[str, str] = Field(
        default_factory=dict, description="Custom prompts for different scenarios"
    )
    enabled: bool = Field(default=True, description="Whether the agent is enabled")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SystemConfig(BaseModel):
    """System-wide configuration"""

    max_conversation_length: int = Field(
        default=50, ge=1, le=200, description="Maximum messages per conversation"
    )
    max_anxiety_level: int = Field(
        default=5, ge=1, le=10, description="Maximum anxiety level"
    )
    default_escalation_threshold: int = Field(
        default=3, ge=1, le=5, description="Default threshold for escalation"
    )
    conversation_timeout: int = Field(
        default=1800, ge=300, le=7200, description="Conversation timeout in seconds"
    )
    rate_limit_requests: int = Field(
        default=100, ge=1, le=1000, description="Rate limit for API requests"
    )
    rate_limit_window: int = Field(
        default=60, ge=1, le=3600, description="Rate limit window in seconds"
    )
    debug_mode: bool = Field(default=False, description="Enable debug mode")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==========================================
# WebSocket Models
# ==========================================


class WebSocketMessageType(Enum):
    """Types of WebSocket messages"""

    CHAT = "chat"
    SYSTEM = "system"
    TYPING = "typing"
    ANXIETY_UPDATE = "anxiety_update"
    ERROR = "error"
    STATUS = "status"


class WebSocketMessage(BaseModel):
    """WebSocket message model for real-time communication"""

    message_type: WebSocketMessageType = Field(..., description="Type of message")
    conversation_id: str = Field(..., description="Conversation identifier")
    user_id: str = Field(..., description="User identifier")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            WebSocketMessageType: lambda v: v.value,
        }


class WebSocketStatus(BaseModel):
    """WebSocket connection status"""

    status: str = Field(
        ..., description="Connection status (connected, disconnected, error)"
    )
    conversation_id: str = Field(..., description="Conversation identifier")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Status timestamp"
    )
    message: Optional[str] = Field(default=None, description="Status message")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Export all models
__all__ = [
    # Enums
    "AnxietyLevel",
    "WorryCategory",
    "ConversationStatus",
    # Core Models
    "UserConcern",
    "AgentResponse",
    "ConversationMessage",
    "ConversationState",
    "AgentInteraction",
    # Analytics
    "ConversationAnalytics",
    "AgentPerformanceMetrics",
    "SystemAnalytics",
    # API Models
    "ChatRequest",
    "ChatResponse",
    "HealthCheckResponse",
    # Configuration
    "AgentConfig",
    "SystemConfig",
    # WebSocket Models
    "WebSocketMessage",
    "WebSocketStatus",
]
