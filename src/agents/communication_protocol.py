"""
Agent Communication Protocol
This module handles communication between agents, including handoffs,
coordination, and information sharing.

File: src/agents/communication_protocol.py
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .base_agent import BaseAgent
from ..models.schemas import (
    AnxietyLevel,
)


class MessageType(Enum):
    """Types of messages between agents"""

    HANDOFF = "handoff"
    CONSULTATION = "consultation"
    INFORMATION_SHARING = "information_sharing"
    COORDINATION = "coordination"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"


class HandoffReason(Enum):
    """Reasons for agent handoff"""

    ESCALATION_COMPLETE = "escalation_complete"
    SPECIALIZED_NEEDED = "specialized_needed"
    MAX_INTERACTION_REACHED = "max_interaction_reached"
    USER_REQUEST = "user_request"
    CONVERSATION_STALLED = "conversation_stalled"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class AgentMessage:
    """Message between agents"""

    id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: str = ""
    user_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
        }


@dataclass
class HandoffRequest:
    """Request to hand off conversation to another agent"""

    target_agent: str
    reason: HandoffReason
    context_summary: str
    escalation_level: AnxietyLevel
    conversation_history: List[Dict[str, Any]]
    user_state: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    urgency: int = 1  # 1-5 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert handoff request to dictionary"""
        return {
            "target_agent": self.target_agent,
            "reason": self.reason.value,
            "context_summary": self.context_summary,
            "escalation_level": self.escalation_level.value,
            "conversation_history": self.conversation_history,
            "user_state": self.user_state,
            "recommendations": self.recommendations,
            "urgency": self.urgency,
        }


class AgentCommunicationProtocol:
    """
    Central communication hub for agent interactions
    """

    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.agent_registry: Dict[str, BaseAgent] = {}
        self.handoff_rules: Dict[str, List[str]] = {}
        self.communication_log: List[AgentMessage] = []

        self.logger = logging.getLogger("agent_communication")

        # Initialize handoff rules
        self._initialize_handoff_rules()

    def _initialize_handoff_rules(self):
        """Initialize rules for agent handoffs"""
        self.handoff_rules = {
            "intake_specialist": [
                "catastrophe_escalator",
                "social_anxiety_amplifier",
                "timeline_panic_generator",
            ],
            "catastrophe_escalator": [
                "timeline_panic_generator",
                "probability_twister",
                "false_comfort_provider",
            ],
            "timeline_panic_generator": [
                "social_anxiety_amplifier",
                "probability_twister",
                "false_comfort_provider",
            ],
            "probability_twister": [
                "false_comfort_provider",
                "social_anxiety_amplifier",
                "timeline_panic_generator",
            ],
            "social_anxiety_amplifier": [
                "false_comfort_provider",
                "probability_twister",
                "catastrophe_escalator",
            ],
            "false_comfort_provider": [
                "catastrophe_escalator",
                "timeline_panic_generator",
                "intake_specialist",  # Loop back for new concerns
            ],
        }

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the communication protocol"""
        self.agent_registry[agent.id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.id})")

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agent_registry:
            agent_name = self.agent_registry[agent_id].name
            del self.agent_registry[agent_id]
            self.logger.info(f"Unregistered agent: {agent_name} ({agent_id})")

    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message between agents"""
        try:
            # Validate agents exist
            if message.from_agent not in self.agent_registry:
                self.logger.error(f"Sender agent not found: {message.from_agent}")
                return False

            if message.to_agent not in self.agent_registry:
                self.logger.error(f"Recipient agent not found: {message.to_agent}")
                return False

            # Add to message queue
            self.message_queue.append(message)

            # Log communication
            self.communication_log.append(message)

            # Process message immediately
            await self._process_message(message)

            self.logger.info(
                f"Message sent: {message.from_agent} -> {message.to_agent}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False

    async def _process_message(self, message: AgentMessage):
        """Process a message between agents"""
        try:
            sender = self.agent_registry[message.from_agent]
            recipient = self.agent_registry[message.to_agent]

            # Handle different message types
            if message.message_type == MessageType.HANDOFF:
                await self._process_handoff(message, sender, recipient)
            elif message.message_type == MessageType.CONSULTATION:
                await self._process_consultation(message, sender, recipient)
            elif message.message_type == MessageType.INFORMATION_SHARING:
                await self._process_information_sharing(message, sender, recipient)
            elif message.message_type == MessageType.STATUS_UPDATE:
                await self._process_status_update(message, sender, recipient)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def _process_handoff(
        self, message: AgentMessage, sender: BaseAgent, recipient: BaseAgent
    ):
        """Process a handoff request"""
        try:
            # Extract handoff data
            handoff_data = message.metadata.get("handoff_request", {})

            # Update conversation state
            conversation_id = message.conversation_id
            if conversation_id in self.active_conversations:
                self.active_conversations[conversation_id][
                    "current_agent"
                ] = recipient.id
                self.active_conversations[conversation_id]["handoff_history"].append(
                    {
                        "from": sender.id,
                        "to": recipient.id,
                        "timestamp": datetime.now(),
                        "reason": handoff_data.get("reason", "unspecified"),
                    }
                )

            # Notify recipient about handoff
            await recipient.communicate_with_agent(
                sender,
                f"Handoff received: {handoff_data.get('context_summary', 'No context provided')}",
                message.metadata.get("context", {}),
            )

            self.logger.info(f"Handoff processed: {sender.name} -> {recipient.name}")

        except Exception as e:
            self.logger.error(f"Error processing handoff: {e}")

    async def _process_consultation(
        self, message: AgentMessage, sender: BaseAgent, recipient: BaseAgent
    ):
        """Process a consultation request"""
        try:
            # Recipients can provide advice without taking over
            consultation_response = await recipient.communicate_with_agent(
                sender, message.content, message.metadata.get("context", {})
            )

            # Send response back to sender
            response_message = AgentMessage(
                id=f"consultation_response_{datetime.now().timestamp()}",
                from_agent=recipient.id,
                to_agent=sender.id,
                message_type=MessageType.INFORMATION_SHARING,
                content=consultation_response,
                metadata={
                    "consultation_response": True,
                    "original_message_id": message.id,
                },
            )

            await self.send_message(response_message)

        except Exception as e:
            self.logger.error(f"Error processing consultation: {e}")

    async def _process_information_sharing(
        self, message: AgentMessage, sender: BaseAgent, recipient: BaseAgent
    ):
        """Process information sharing between agents"""
        try:
            # Update recipient's knowledge about the conversation
            if hasattr(recipient, "add_shared_information"):
                recipient.add_shared_information(message.content, sender.id)

            self.logger.info(f"Information shared: {sender.name} -> {recipient.name}")

        except Exception as e:
            self.logger.error(f"Error processing information sharing: {e}")

    async def _process_status_update(
        self, message: AgentMessage, sender: BaseAgent, recipient: BaseAgent
    ):
        """Process status updates between agents"""
        try:
            # Log status update
            self.logger.info(
                f"Status update: {sender.name} -> {recipient.name}: {message.content}"
            )

        except Exception as e:
            self.logger.error(f"Error processing status update: {e}")

    async def request_handoff(
        self,
        from_agent: BaseAgent,
        handoff_request: HandoffRequest,
        conversation_id: str,
    ) -> bool:
        """Request handoff to another agent"""
        try:
            # Validate handoff rules
            if not self._validate_handoff(
                from_agent.agent_type.value, handoff_request.target_agent
            ):
                self.logger.warning(
                    f"Handoff validation failed: {from_agent.name} -> {handoff_request.target_agent}"
                )
                return False

            # Create handoff message
            message = AgentMessage(
                id=f"handoff_{datetime.now().timestamp()}",
                from_agent=from_agent.id,
                to_agent=handoff_request.target_agent,
                message_type=MessageType.HANDOFF,
                content=f"Handoff request: {handoff_request.context_summary}",
                metadata={
                    "handoff_request": handoff_request.to_dict(),
                    "conversation_id": conversation_id,
                },
                conversation_id=conversation_id,
            )

            # Send handoff message
            success = await self.send_message(message)

            if success:
                self.logger.info(
                    f"Handoff requested: {from_agent.name} -> {handoff_request.target_agent}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error requesting handoff: {e}")
            return False

    def _validate_handoff(self, from_agent_type: str, to_agent_id: str) -> bool:
        """Validate if handoff is allowed"""
        # Check if target agent exists
        if to_agent_id not in self.agent_registry:
            return False

        # Check handoff rules
        if from_agent_type in self.handoff_rules:
            to_agent = self.agent_registry[to_agent_id]
            to_agent_type = to_agent.agent_type.value

            allowed_targets = self.handoff_rules[from_agent_type]
            return to_agent_type in allowed_targets

        return True  # Allow handoff if no specific rules

    def get_conversation_agents(self, conversation_id: str) -> List[str]:
        """Get all agents involved in a conversation"""
        if conversation_id not in self.active_conversations:
            return []

        return self.active_conversations[conversation_id].get("agents_involved", [])

    def get_current_agent(self, conversation_id: str) -> Optional[str]:
        """Get the current agent for a conversation"""
        if conversation_id not in self.active_conversations:
            return None

        return self.active_conversations[conversation_id].get("current_agent")

    def start_conversation(
        self, conversation_id: str, initial_agent_id: str, user_id: str
    ):
        """Start a new conversation tracking"""
        self.active_conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "current_agent": initial_agent_id,
            "agents_involved": [initial_agent_id],
            "handoff_history": [],
            "started_at": datetime.now(),
            "last_activity": datetime.now(),
        }

        self.logger.info(
            f"Started conversation tracking: {conversation_id} with agent {initial_agent_id}"
        )

    def end_conversation(self, conversation_id: str):
        """End conversation tracking"""
        if conversation_id in self.active_conversations:
            conversation = self.active_conversations[conversation_id]
            conversation["ended_at"] = datetime.now()

            # Archive conversation (in a real system, this would go to a database)
            self.logger.info(f"Ended conversation: {conversation_id}")

            # Remove from active conversations
            del self.active_conversations[conversation_id]

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            "total_messages": len(self.communication_log),
            "active_conversations": len(self.active_conversations),
            "registered_agents": len(self.agent_registry),
            "message_types": {
                msg_type.value: len(
                    [
                        msg
                        for msg in self.communication_log
                        if msg.message_type == msg_type
                    ]
                )
                for msg_type in MessageType
            },
            "handoff_patterns": self._analyze_handoff_patterns(),
        }

    def _analyze_handoff_patterns(self) -> Dict[str, List[str]]:
        """Analyze handoff patterns"""
        patterns = {}

        for conversation in self.active_conversations.values():
            handoff_history = conversation.get("handoff_history", [])

            for handoff in handoff_history:
                from_agent = handoff["from"]
                to_agent = handoff["to"]

                if from_agent not in patterns:
                    patterns[from_agent] = []
                patterns[from_agent].append(to_agent)

        return patterns

    def get_message_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get message history for a conversation"""
        return [
            msg.to_dict()
            for msg in self.communication_log
            if msg.conversation_id == conversation_id
        ]


# Global communication protocol instance
communication_protocol = AgentCommunicationProtocol()

# Export
__all__ = [
    "MessageType",
    "HandoffReason",
    "AgentMessage",
    "HandoffRequest",
    "AgentCommunicationProtocol",
    "communication_protocol",
]
