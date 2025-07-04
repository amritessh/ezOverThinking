"""
Base Agent Class - Core Architecture for ezOverThinking
This module defines the abstract base class for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
import uuid
import asyncio
import logging

import os
import sys
import dotenv

dotenv.load_dotenv()


from langchain.agents import AgentExecutor
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..models.schemas import UserConcern, AgentResponse, AnxietyLevel


class AgentType(Enum):
    """Enumeration of different agent types in the system"""
    INTAKE_SPECIALIST = "intake_specialist"
    CATASTROPHE_ESCALATOR = "catastrophe_escalator"
    TIMELINE_PANIC_GENERATOR = "timeline_panic_generator"
    PROBABILITY_TWISTER = "probability_twister"
    SOCIAL_ANXIETY_AMPLIFIER = "social_anxiety_amplifier"
    FALSE_COMFORT_PROVIDER = "false_comfort_provider"
    COORDINATOR = "coordinator"


class AgentState(Enum):
    """Current state of an agent"""
    IDLE = "idle"
    PROCESSING = "processing"
    RESPONDING = "responding"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentContext:
    """Context information shared between agents"""
    conversation_id: str
    user_id: str
    current_anxiety_level: AnxietyLevel
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    agent_interactions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for agent interactions"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.interactions = []
        self.logger = logging.getLogger(f"agent.{agent_id}")
    
    def on_agent_action(self, action, **kwargs):
        """Log agent actions"""
        self.interactions.append({
            'timestamp': datetime.now(),
            'action': str(action),
            'agent_id': self.agent_id
        })
        self.logger.info(f"Agent {self.agent_id} performed action: {action}")
    
    def on_agent_finish(self, finish, **kwargs):
        """Log agent completion"""
        self.logger.info(f"Agent {self.agent_id} finished with result: {finish}")


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the ezOverThinking system.
    
    This class provides the foundational structure and interface that all
    specialized agents must implement. It handles common functionality
    like state management, communication protocols, and response formatting.
    """
    
    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.8,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Initialize the base agent with common configuration.
        
        Args:
            name: Human-readable name for the agent
            agent_type: Type of agent from AgentType enum
            model_name: LLM model to use
            temperature: Creativity level for responses
            max_tokens: Maximum tokens in response
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Initialize memory and callbacks
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.callback_handler = AgentCallbackHandler(self.id)
        
        # Agent-specific configuration
        self.config = self._initialize_config()
        
        # Performance metrics
        self.metrics = {
            'total_interactions': 0,
            'average_response_time': 0,
            'escalation_success_rate': 0,
            'last_updated': datetime.now()
        }
        
        # Logger
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.logger.info(f"Agent {self.name} initialized with ID: {self.id}")
    
    @abstractmethod
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize agent-specific configuration"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines this agent's personality"""
        pass
    
    @abstractmethod
    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        pass
    
    @abstractmethod
    async def process_concern(
        self, 
        concern: UserConcern, 
        context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and generate an appropriate response"""
        pass
    
    def update_state(self, new_state: AgentState):
        """Update the agent's current state"""
        old_state = self.state
        self.state = new_state
        self.logger.debug(f"Agent {self.name} state changed: {old_state} -> {new_state}")
    
    def add_to_memory(self, message: BaseMessage):
        """Add a message to the agent's memory"""
        self.memory.chat_memory.add_message(message)
    
    def get_memory_summary(self) -> str:
        """Get a summary of the conversation memory"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No previous conversation history."
        
        summary = "Recent conversation context:\n"
        for msg in messages[-5:]:  # Last 5 messages
            if isinstance(msg, HumanMessage):
                summary += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                summary += f"Assistant: {msg.content}\n"
        
        return summary
    
    async def communicate_with_agent(
        self, 
        target_agent: 'BaseAgent', 
        message: str,
        context: AgentContext
    ) -> str:
        """
        Communicate with another agent (agent-to-agent communication)
        
        Args:
            target_agent: The agent to communicate with
            message: The message to send
            context: Shared context
            
        Returns:
            Response from the target agent
        """
        self.logger.info(f"Communicating with agent {target_agent.name}")
        
        # Create a formatted message for inter-agent communication
        formatted_message = f"[AGENT_COMMUNICATION from {self.name}]: {message}"
        
        # This would typically go through a message broker in production
        # For now, we'll simulate direct communication
        concern = UserConcern(
            original_worry=formatted_message,
            category="agent_communication",
            user_id=context.user_id
        )
        
        response = await target_agent.process_concern(concern, context)
        return response.response
    
    def calculate_anxiety_escalation(
        self, 
        current_level: AnxietyLevel, 
        escalation_factor: float = 1.0
    ) -> AnxietyLevel:
        """
        Calculate the new anxiety level after this agent's intervention
        
        Args:
            current_level: Current anxiety level
            escalation_factor: How much this agent escalates (0.5 = reduce, 1.5 = increase)
            
        Returns:
            New anxiety level
        """
        current_value = current_level.value
        new_value = min(5, max(1, int(current_value * escalation_factor)))
        return AnxietyLevel(new_value)
    
    def format_response(
        self, 
        content: str, 
        anxiety_escalation: int = 1,
        suggested_next_agents: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        Format a response according to the standard AgentResponse schema
        
        Args:
            content: The response content
            anxiety_escalation: How much this escalates anxiety (1-5)
            suggested_next_agents: List of agent names to consider next
            metadata: Additional metadata
            
        Returns:
            Formatted AgentResponse
        """
        return AgentResponse(
            agent_name=self.name,
            response=content,
            anxiety_escalation=anxiety_escalation,
            suggested_next_agents=suggested_next_agents or [],
            metadata=metadata or {}
        )
    
    def update_metrics(self, response_time: float, escalation_success: bool):
        """Update agent performance metrics"""
        self.metrics['total_interactions'] += 1
        
        # Update average response time
        current_avg = self.metrics['average_response_time']
        total_interactions = self.metrics['total_interactions']
        self.metrics['average_response_time'] = (
            (current_avg * (total_interactions - 1) + response_time) / total_interactions
        )
        
        # Update escalation success rate
        if escalation_success:
            current_rate = self.metrics['escalation_success_rate']
            self.metrics['escalation_success_rate'] = (
                (current_rate * (total_interactions - 1) + 1) / total_interactions
            )
        
        self.metrics['last_updated'] = datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.agent_type.value,
            'state': self.state.value,
            'config': self.config,
            'metrics': self.metrics,
            'model': self.model_name,
            'temperature': self.temperature
        }
    
    async def health_check(self) -> bool:
        """Perform a health check on the agent"""
        try:
            # Simple test query to check if LLM is responsive
            test_response = await self.llm.ainvoke([HumanMessage(content="Hello")])
            return bool(test_response.content)
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def __str__(self) -> str:
        return f"Agent({self.name}, {self.agent_type.value}, {self.state.value})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"


class AgentFactory:
    """Factory class for creating different types of agents"""
    
    @staticmethod
    def create_agent(agent_type: AgentType, **kwargs) -> BaseAgent:
        """
        Create an agent of the specified type
        
        Args:
            agent_type: Type of agent to create
            **kwargs: Additional arguments for agent initialization
            
        Returns:
            Instantiated agent
        """
        # Import agents dynamically to avoid circular imports
        agent_classes = {}
        
        try:
            if agent_type == AgentType.INTAKE_SPECIALIST:
                from .intake_specialist import IntakeSpecialistAgent
                agent_classes[AgentType.INTAKE_SPECIALIST] = IntakeSpecialistAgent
            elif agent_type == AgentType.CATASTROPHE_ESCALATOR:
                from .catastrophe_escalator import CatastropheEscalatorAgent
                agent_classes[AgentType.CATASTROPHE_ESCALATOR] = CatastropheEscalatorAgent
            elif agent_type == AgentType.TIMELINE_PANIC_GENERATOR:
                from .timeline_panic_generator import TimelinePanicGeneratorAgent
                agent_classes[AgentType.TIMELINE_PANIC_GENERATOR] = TimelinePanicGeneratorAgent
            elif agent_type == AgentType.PROBABILITY_TWISTER:
                from .probability_twister import ProbabilityTwisterAgent
                agent_classes[AgentType.PROBABILITY_TWISTER] = ProbabilityTwisterAgent
            elif agent_type == AgentType.SOCIAL_ANXIETY_AMPLIFIER:
                from .social_anxiety_amplifier import SocialAnxietyAmplifierAgent
                agent_classes[AgentType.SOCIAL_ANXIETY_AMPLIFIER] = SocialAnxietyAmplifierAgent
            elif agent_type == AgentType.FALSE_COMFORT_PROVIDER:
                from .false_comfort_provider import FalseComfortProviderAgent
                agent_classes[AgentType.FALSE_COMFORT_PROVIDER] = FalseComfortProviderAgent
            elif agent_type == AgentType.COORDINATOR:
                from .coordinator import AgentCoordinator
                agent_classes[AgentType.COORDINATOR] = AgentCoordinator
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
        except ImportError as e:
            raise ImportError(f"Could not import agent class for {agent_type.value}: {e}")
        
        if agent_type not in agent_classes:
            raise ValueError(f"Agent type {agent_type.value} not available")
        
        agent_class = agent_classes[agent_type]
        return agent_class(**kwargs)
    
    @staticmethod
    def create_all_agents(**kwargs) -> Dict[AgentType, BaseAgent]:
        """Create all agent types and return as a dictionary"""
        agents = {}
        
        for agent_type in AgentType:
            try:
                agents[agent_type] = AgentFactory.create_agent(agent_type, **kwargs)
            except (ImportError, ValueError) as e:
                logging.warning(f"Could not create agent {agent_type.value}: {e}")
        
        return agents
    
    @staticmethod
    def create_orchestrated_agent_system(**kwargs) -> Dict[str, Any]:
        """Create a complete orchestrated agent system with coordinator"""
        
        # Create all agents
        agents = AgentFactory.create_all_agents(**kwargs)
        
        # Create coordinator
        coordinator = agents.get(AgentType.COORDINATOR)
        if not coordinator:
            raise ValueError("Coordinator agent not available")
        
        # Register all agents with coordinator
        for agent in agents.values():
            if agent.agent_type != AgentType.COORDINATOR:
                coordinator.register_agent(agent)
        
        return {
            "coordinator": coordinator,
            "agents": agents,
            "agent_count": len(agents),
            "system_ready": True
        }
    
    @staticmethod
    def get_available_agent_types() -> List[AgentType]:
        """Get list of all available agent types"""
        return list(AgentType)
    
    @staticmethod
    def get_agent_descriptions() -> Dict[AgentType, str]:
        """Get descriptions of all agent types"""
        return {
            AgentType.INTAKE_SPECIALIST: "Empathetic therapist who builds trust and categorizes concerns",
            AgentType.CATASTROPHE_ESCALATOR: "Dramatic disaster expert who turns molehills into mountains",
            AgentType.TIMELINE_PANIC_GENERATOR: "Time pressure specialist who creates artificial urgency",
            AgentType.PROBABILITY_TWISTER: "Pseudo-scientific statistician who uses fake data",
            AgentType.SOCIAL_ANXIETY_AMPLIFIER: "Social catastrophe expert who amplifies judgment fears",
            AgentType.FALSE_COMFORT_PROVIDER: "Reassurance underminer who destroys hope",
            AgentType.COORDINATOR: "Orchestra conductor who coordinates the entire experience"
        }
    
    @staticmethod
    def validate_agent_system() -> Dict[str, Any]:
        """Validate that the complete agent system can be created"""
        validation_results = {
            "all_agents_available": True,
            "agent_creation_errors": [],
            "system_integrity": True,
            "total_agents": 0
        }
        
        for agent_type in AgentType:
            try:
                agent = AgentFactory.create_agent(agent_type)
                validation_results["total_agents"] += 1
            except Exception as e:
                validation_results["all_agents_available"] = False
                validation_results["agent_creation_errors"].append({
                    "agent_type": agent_type.value,
                    "error": str(e)
                })
        
        # Test orchestrated system
        try:
            system = AgentFactory.create_orchestrated_agent_system()
            validation_results["orchestrated_system"] = True
        except Exception as e:
            validation_results["system_integrity"] = False
            validation_results["orchestration_error"] = str(e)
        
        return validation_results


# Export the main classes
__all__ = [
    'BaseAgent',
    'AgentType',
    'AgentState',
    'AgentContext',
    'AgentCallbackHandler',
    'AgentFactory'
]