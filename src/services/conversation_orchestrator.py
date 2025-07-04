"""
ConversationOrchestrator - Enhanced Multi-Agent Coordination
This service orchestrates complex multi-agent conversations with state persistence,
advanced analytics, and sophisticated conversation flow management.

File: src/services/conversation_orchestrator.py
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from .state_manager import StateManager
from .anxiety_tracker import AnxietyTracker
from ..agents.base_agent import BaseAgent, AgentType, AgentContext
from ..agents.coordinator import (
    AgentCoordinator,
    CoordinationStrategy,
    ConversationPhase,
)
from ..agents.communication_protocol import (
    communication_protocol,
)
from ..models.schemas import (
    UserConcern,
    AgentResponse,
    ConversationState,
    ConversationStatus,
    AnxietyLevel,
    WorryCategory,
)


class OrchestrationMode(Enum):
    """Different orchestration modes"""

    SIMPLE = "simple"  # Basic agent-to-agent handoffs
    COORDINATED = "coordinated"  # Coordinator-managed conversations
    COLLABORATIVE = "collaborative"  # Multiple agents working together
    ADAPTIVE = "adaptive"  # AI-driven orchestration adaptation


@dataclass
class ConversationContext:
    """Extended conversation context with orchestration data"""

    conversation_id: str
    user_id: str
    orchestration_mode: OrchestrationMode
    strategy: CoordinationStrategy
    phase: ConversationPhase
    active_agents: List[str] = field(default_factory=list)
    conversation_goals: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    orchestration_history: List[Dict[str, Any]] = field(default_factory=list)


class ConversationOrchestrator:
    """
    Enhanced multi-agent conversation orchestration with state management,
    analytics, and sophisticated conversation flow control.
    """

    def __init__(
        self, state_manager: StateManager, anxiety_tracker: AnxietyTracker = None
    ):
        self.state_manager = state_manager
        self.anxiety_tracker = anxiety_tracker
        self.logger = logging.getLogger("ConversationOrchestrator")

        # Orchestration components
        self.agents: Dict[str, BaseAgent] = {}
        self.coordinator: Optional[AgentCoordinator] = None
        self.active_conversations: Dict[str, ConversationContext] = {}

        # Performance tracking
        self.orchestration_metrics = {
            "total_conversations": 0,
            "successful_orchestrations": 0,
            "average_conversation_length": 0,
            "average_anxiety_escalation": 0,
            "agent_utilization": {},
            "phase_completion_rates": {},
            "strategy_effectiveness": {},
        }

        # Configuration
        self.config = {
            "max_conversation_length": 25,
            "max_concurrent_conversations": 100,
            "conversation_timeout_minutes": 30,
            "auto_escalation_threshold": 3,
            "collaborative_threshold": 0.8,
            "adaptive_learning_enabled": True,
        }

    async def initialize(self) -> bool:
        """Initialize the orchestrator"""
        try:
            # Connect to state manager
            if not await self.state_manager.connect():
                self.logger.error("Failed to connect to state manager")
                return False

            # Initialize anxiety tracker
            if self.anxiety_tracker:
                await self.anxiety_tracker.initialize()

            self.logger.info("ConversationOrchestrator initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error initializing orchestrator: {e}")
            return False

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.id] = agent
        self.orchestration_metrics["agent_utilization"][agent.id] = {
            "total_interactions": 0,
            "successful_handoffs": 0,
            "average_response_time": 0,
            "effectiveness_score": 0,
        }

        # Register with communication protocol
        communication_protocol.register_agent(agent)

        self.logger.info(f"Registered agent: {agent.name} ({agent.id})")

    def register_coordinator(self, coordinator: AgentCoordinator):
        """Register the coordinator agent"""
        self.coordinator = coordinator
        self.register_agent(coordinator)

        # Register all other agents with coordinator
        for agent in self.agents.values():
            if agent.id != coordinator.id:
                coordinator.register_agent(agent)

        self.logger.info("Registered coordinator agent")

    async def start_conversation(
        self,
        user_id: str,
        initial_concern: UserConcern,
        orchestration_mode: OrchestrationMode = OrchestrationMode.COORDINATED,
        strategy: CoordinationStrategy = None,
    ) -> str:
        """Start a new orchestrated conversation"""
        try:
            # Generate conversation ID
            conversation_id = f"conv_{user_id}_{datetime.now().timestamp()}"

            # Determine strategy
            if not strategy:
                strategy = await self._select_optimal_strategy(initial_concern)

            # Create conversation state
            conversation_state = ConversationState(
                conversation_id=conversation_id,
                user_id=user_id,
                status=ConversationStatus.ACTIVE,
                current_anxiety_level=initial_concern.anxiety_level,
                message_count=0,
                escalation_count=0,
                agents_involved=[],
                context={
                    "initial_concern": initial_concern.dict(),
                    "orchestration_mode": orchestration_mode.value,
                    "strategy": strategy.value,
                    "phase": ConversationPhase.INTAKE.value,
                    "goals": self._generate_conversation_goals(initial_concern),
                },
            )

            # Store conversation state
            await self.state_manager.store_conversation_state(
                conversation_id, conversation_state
            )

            # Create conversation context
            conversation_context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                orchestration_mode=orchestration_mode,
                strategy=strategy,
                phase=ConversationPhase.INTAKE,
                conversation_goals=self._generate_conversation_goals(initial_concern),
            )

            self.active_conversations[conversation_id] = conversation_context

            # Initialize with coordinator if available
            if self.coordinator and orchestration_mode == OrchestrationMode.COORDINATED:
                # Create conversation state for coordinator
                coordinator_state = ConversationState(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    status=ConversationStatus.ACTIVE,
                    current_anxiety_level=initial_concern.anxiety_level,
                    message_count=0,
                    escalation_count=0,
                    agents_involved=[],
                    context={
                        "initial_concern": initial_concern.dict(),
                        "strategy": strategy.value,
                        "phase": ConversationPhase.INTAKE,
                        "phase_history": [],
                    },
                )

                # Add to coordinator's conversation states
                self.coordinator.conversation_states[conversation_id] = (
                    coordinator_state
                )

                # Start conversation tracking in communication protocol
                communication_protocol.start_conversation(
                    conversation_id, self.coordinator.id, user_id
                )

            # Track metrics
            self.orchestration_metrics["total_conversations"] += 1

            # Initialize anxiety tracking
            if self.anxiety_tracker:
                await self.anxiety_tracker.start_tracking(
                    conversation_id, initial_concern.anxiety_level
                )

            self.logger.info(f"Started conversation: {conversation_id}")
            return conversation_id

        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            raise

    async def orchestrate_response(
        self, conversation_id: str, user_message: str, context: Dict[str, Any] = None
    ) -> AgentResponse:
        """Orchestrate a response using the appropriate mode"""
        try:
            # Get conversation context
            conversation_context = self.active_conversations.get(conversation_id)
            if not conversation_context:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Get conversation state
            conversation_state = await self.state_manager.get_conversation_state(
                conversation_id
            )
            if not conversation_state:
                raise ValueError(f"Conversation state {conversation_id} not found")

            # Update user activity
            await self.state_manager.update_user_activity(conversation_context.user_id)

            # Orchestrate based on mode
            if conversation_context.orchestration_mode == OrchestrationMode.COORDINATED:
                response = await self._orchestrate_coordinated(
                    conversation_id,
                    user_message,
                    conversation_context,
                    conversation_state,
                )
            elif (
                conversation_context.orchestration_mode
                == OrchestrationMode.COLLABORATIVE
            ):
                response = await self._orchestrate_collaborative(
                    conversation_id,
                    user_message,
                    conversation_context,
                    conversation_state,
                )
            elif conversation_context.orchestration_mode == OrchestrationMode.ADAPTIVE:
                response = await self._orchestrate_adaptive(
                    conversation_id,
                    user_message,
                    conversation_context,
                    conversation_state,
                )
            else:
                response = await self._orchestrate_simple(
                    conversation_id,
                    user_message,
                    conversation_context,
                    conversation_state,
                )

            # Update conversation state
            await self._update_conversation_state(
                conversation_id, response, conversation_context, conversation_state
            )

            # Track anxiety progression
            if self.anxiety_tracker:
                await self.anxiety_tracker.track_anxiety_change(
                    conversation_id,
                    conversation_state.current_anxiety_level,
                    AnxietyLevel(
                        min(
                            5,
                            conversation_state.current_anxiety_level.value
                            + response.anxiety_escalation
                            - 1,
                        )
                    ),
                )

            # Record orchestration event
            await self._record_orchestration_event(
                conversation_id, response, conversation_context
            )

            return response

        except Exception as e:
            self.logger.error(f"Error orchestrating response: {e}")
            raise

    async def _orchestrate_coordinated(
        self,
        conversation_id: str,
        user_message: str,
        conversation_context: ConversationContext,
        conversation_state: ConversationState,
    ) -> AgentResponse:
        """Orchestrate using the coordinator agent"""

        if not self.coordinator:
            raise ValueError("Coordinator not available for coordinated orchestration")

        # Use coordinator to manage conversation
        response = await self.coordinator.coordinate_conversation(
            conversation_id, user_message
        )

        # Update context with coordinator decision
        conversation_context.orchestration_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "coordinator_decision",
                "agent_selected": response.metadata.get("agent_used"),
                "strategy": conversation_context.strategy.value,
                "phase": conversation_context.phase.value,
            }
        )

        return response

    async def _orchestrate_collaborative(
        self,
        conversation_id: str,
        user_message: str,
        conversation_context: ConversationContext,
        conversation_state: ConversationState,
    ) -> AgentResponse:
        """Orchestrate using multiple agents collaboratively"""

        # Select multiple agents for collaboration
        selected_agents = await self._select_collaborative_agents(
            user_message, conversation_state
        )

        if len(selected_agents) < 2:
            # Fall back to simple orchestration
            return await self._orchestrate_simple(
                conversation_id, user_message, conversation_context, conversation_state
            )

        # Get responses from multiple agents
        user_concern = UserConcern(
            original_worry=user_message,
            user_id=conversation_context.user_id,
            anxiety_level=conversation_state.current_anxiety_level,
        )

        agent_context = AgentContext(
            conversation_id=conversation_id,
            user_id=conversation_context.user_id,
            current_anxiety_level=conversation_state.current_anxiety_level,
        )

        # Get responses from selected agents
        responses = []
        for agent in selected_agents:
            try:
                response = await agent.process_concern(user_concern, agent_context)
                responses.append((agent, response))
            except Exception as e:
                self.logger.error(
                    f"Error getting response from agent {agent.name}: {e}"
                )

        # Synthesize collaborative response
        if responses:
            synthesized_response = await self._synthesize_collaborative_response(
                responses, conversation_context
            )
            return synthesized_response
        else:
            # Fallback to simple orchestration
            return await self._orchestrate_simple(
                conversation_id, user_message, conversation_context, conversation_state
            )

    async def _orchestrate_adaptive(
        self,
        conversation_id: str,
        user_message: str,
        conversation_context: ConversationContext,
        conversation_state: ConversationState,
    ) -> AgentResponse:
        """Orchestrate using adaptive AI-driven decisions"""

        # Analyze conversation history and user patterns
        analysis = await self._analyze_conversation_patterns(
            conversation_id, conversation_state
        )

        # Adapt strategy based on analysis
        if analysis["should_change_strategy"]:
            new_strategy = analysis["recommended_strategy"]
            conversation_context.strategy = new_strategy

            # Update conversation state
            await self.state_manager.update_conversation_state(
                conversation_id,
                {
                    "context": {
                        **conversation_state.context,
                        "strategy": new_strategy.value,
                    }
                },
            )

        # Select agent based on adaptive analysis
        selected_agent = await self._select_adaptive_agent(
            user_message, conversation_state, analysis
        )

        if selected_agent:
            # Process with selected agent
            user_concern = UserConcern(
                original_worry=user_message,
                user_id=conversation_context.user_id,
                anxiety_level=conversation_state.current_anxiety_level,
            )

            agent_context = AgentContext(
                conversation_id=conversation_id,
                user_id=conversation_context.user_id,
                current_anxiety_level=conversation_state.current_anxiety_level,
            )

            response = await selected_agent.process_concern(user_concern, agent_context)

            # Record adaptive decision
            conversation_context.orchestration_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "adaptive_selection",
                    "agent_selected": selected_agent.name,
                    "analysis": analysis,
                    "confidence": analysis.get("confidence", 0.5),
                }
            )

            return response
        else:
            # Fallback to coordinated orchestration
            return await self._orchestrate_coordinated(
                conversation_id, user_message, conversation_context, conversation_state
            )

    async def _orchestrate_simple(
        self,
        conversation_id: str,
        user_message: str,
        conversation_context: ConversationContext,
        conversation_state: ConversationState,
    ) -> AgentResponse:
        """Simple orchestration using basic agent selection"""

        # Select single agent based on simple rules
        selected_agent = await self._select_simple_agent(
            user_message, conversation_state
        )

        if selected_agent:
            # Process with selected agent
            user_concern = UserConcern(
                original_worry=user_message,
                user_id=conversation_context.user_id,
                anxiety_level=conversation_state.current_anxiety_level,
            )

            agent_context = AgentContext(
                conversation_id=conversation_id,
                user_id=conversation_context.user_id,
                current_anxiety_level=conversation_state.current_anxiety_level,
            )

            response = await selected_agent.process_concern(user_concern, agent_context)
            return response
        else:
            # Fallback response
            return AgentResponse(
                agent_name="System",
                agent_id="system",
                response="I'm having trouble selecting the right agent for your concern. Let me try a different approach.",
                anxiety_escalation=1,
                suggested_next_agents=["intake_specialist"],
            )

    async def _select_optimal_strategy(
        self, initial_concern: UserConcern
    ) -> CoordinationStrategy:
        """Select optimal coordination strategy based on concern analysis"""

        # Analyze concern complexity
        complexity_score = 0
        concern_text = initial_concern.original_worry.lower()

        # Social concerns often benefit from spiral intensification
        if initial_concern.category == WorryCategory.SOCIAL:
            complexity_score += 0.3

        # High anxiety concerns need adaptive orchestration
        if initial_concern.anxiety_level.value >= 3:
            complexity_score += 0.4

        # Long concerns suggest complexity
        if len(initial_concern.original_worry) > 100:
            complexity_score += 0.2

        # Multiple concern indicators suggest ping-pong
        concern_keywords = ["and", "also", "plus", "additionally", "furthermore"]
        if any(keyword in concern_text for keyword in concern_keywords):
            complexity_score += 0.1

        # Select strategy based on complexity
        if complexity_score >= 0.7:
            return CoordinationStrategy.ADAPTIVE_ORCHESTRATION
        elif complexity_score >= 0.5:
            return CoordinationStrategy.SPIRAL_INTENSIFICATION
        elif complexity_score >= 0.3:
            return CoordinationStrategy.PING_PONG_ANXIETY
        else:
            return CoordinationStrategy.LINEAR_ESCALATION

    def _generate_conversation_goals(self, initial_concern: UserConcern) -> List[str]:
        """Generate conversation goals based on initial concern"""
        goals = [
            "escalate_anxiety_progressively",
            "maintain_user_engagement",
            "demonstrate_agent_coordination",
        ]

        # Add category-specific goals
        if initial_concern.category == WorryCategory.SOCIAL:
            goals.append("amplify_social_anxiety")
        elif initial_concern.category == WorryCategory.HEALTH:
            goals.append("create_health_catastrophe_scenarios")
        elif initial_concern.category == WorryCategory.CAREER:
            goals.append("build_career_timeline_pressure")

        return goals

    async def _select_collaborative_agents(
        self, user_message: str, conversation_state: ConversationState
    ) -> List[BaseAgent]:
        """Select agents for collaborative response"""

        # Analyze message for collaboration potential
        message_lower = user_message.lower()
        selected_agents = []

        # Always include one primary agent
        primary_agent = await self._select_simple_agent(
            user_message, conversation_state
        )
        if primary_agent:
            selected_agents.append(primary_agent)

        # Add complementary agents
        if any(word in message_lower for word in ["social", "people", "friends"]):
            social_agent = self._get_agent_by_type(AgentType.SOCIAL_ANXIETY_AMPLIFIER)
            if social_agent and social_agent not in selected_agents:
                selected_agents.append(social_agent)

        if any(word in message_lower for word in ["time", "deadline", "urgent"]):
            timeline_agent = self._get_agent_by_type(AgentType.TIMELINE_PANIC_GENERATOR)
            if timeline_agent and timeline_agent not in selected_agents:
                selected_agents.append(timeline_agent)

        if any(word in message_lower for word in ["chance", "likely", "probably"]):
            probability_agent = self._get_agent_by_type(AgentType.PROBABILITY_TWISTER)
            if probability_agent and probability_agent not in selected_agents:
                selected_agents.append(probability_agent)

        return selected_agents[:3]  # Limit to 3 agents for collaboration

    async def _synthesize_collaborative_response(
        self,
        responses: List[Tuple[BaseAgent, AgentResponse]],
        conversation_context: ConversationContext,
    ) -> AgentResponse:
        """Synthesize multiple agent responses into a collaborative response"""

        if not responses:
            raise ValueError("No responses to synthesize")

        if len(responses) == 1:
            return responses[0][1]

        # Combine responses intelligently
        combined_content = (
            "Here's what multiple experts are saying about your situation:\n\n"
        )

        max_anxiety = 0
        all_next_agents = []

        # Calculate available space for each response
        base_length = len(combined_content)
        conclusion_length = len(
            "As you can see, multiple perspectives point to the same concerning patterns. The convergence of these expert opinions suggests this situation requires serious attention."
        )
        available_space = 1900 - base_length - conclusion_length  # Leave buffer
        space_per_response = max(
            100, available_space // len(responses)
        )  # Minimum 100 chars per response

        for i, (agent, response) in enumerate(responses):
            # Truncate individual responses if needed
            response_content = response.response
            if len(response_content) > space_per_response:
                response_content = response_content[: space_per_response - 3] + "..."

            combined_content += f"**{agent.name}**: {response_content}\n\n"
            max_anxiety = max(max_anxiety, response.anxiety_escalation)
            all_next_agents.extend(response.suggested_next_agents)

        # Add synthesis conclusion
        combined_content += "As you can see, multiple perspectives point to the same concerning patterns. "
        combined_content += "The convergence of these expert opinions suggests this situation requires serious attention."

        # Final truncation to ensure we stay within limits
        if len(combined_content) > 1900:
            combined_content = (
                combined_content[:1900] + "...\n\n[Response truncated due to length]"
            )

        # Create synthesized response
        return AgentResponse(
            agent_name="Collaborative Response Team",
            agent_id="collaborative_team",
            response=combined_content,
            anxiety_escalation=min(5, max_anxiety + 1),  # Collaborative bonus
            suggested_next_agents=list(set(all_next_agents))[:3],
            metadata={
                "collaboration_type": "multi_agent_synthesis",
                "agents_involved": [agent.name for agent, _ in responses],
                "synthesis_method": "expert_convergence",
            },
        )

    async def _analyze_conversation_patterns(
        self, conversation_id: str, conversation_state: ConversationState
    ) -> Dict[str, Any]:
        """Analyze conversation patterns for adaptive orchestration"""

        analysis = {
            "should_change_strategy": False,
            "recommended_strategy": conversation_state.context.get("strategy"),
            "confidence": 0.5,
            "patterns_detected": [],
            "user_engagement_score": 0.7,
            "anxiety_progression_rate": 0.5,
        }

        # Analyze conversation length
        if conversation_state.message_count > 10:
            analysis["patterns_detected"].append("long_conversation")

            # If conversation is long but anxiety isn't escalating, change strategy
            if conversation_state.escalation_count < 3:
                analysis["should_change_strategy"] = True
                analysis["recommended_strategy"] = (
                    CoordinationStrategy.SPIRAL_INTENSIFICATION
                )
                analysis["confidence"] = 0.8

        # Analyze anxiety progression
        if conversation_state.escalation_count < conversation_state.message_count * 0.3:
            analysis["patterns_detected"].append("low_escalation_rate")
            analysis["anxiety_progression_rate"] = 0.3

        # Analyze agent effectiveness
        if len(conversation_state.agents_involved) > 4:
            analysis["patterns_detected"].append("high_agent_turnover")
            analysis["should_change_strategy"] = True
            analysis["recommended_strategy"] = (
                CoordinationStrategy.COLLABORATIVE_DESTRUCTION
            )

        return analysis

    async def _select_adaptive_agent(
        self,
        user_message: str,
        conversation_state: ConversationState,
        analysis: Dict[str, Any],
    ) -> Optional[BaseAgent]:
        """Select agent based on adaptive analysis"""

        # Use analysis to inform agent selection
        if "low_escalation_rate" in analysis["patterns_detected"]:
            # Need more aggressive escalation
            return self._get_agent_by_type(AgentType.CATASTROPHE_ESCALATOR)

        if "long_conversation" in analysis["patterns_detected"]:
            # Provide false comfort to mix things up
            return self._get_agent_by_type(AgentType.FALSE_COMFORT_PROVIDER)

        if "high_agent_turnover" in analysis["patterns_detected"]:
            # Use coordinator to stabilize
            return self.coordinator

        # Default to simple selection
        return await self._select_simple_agent(user_message, conversation_state)

    async def _select_simple_agent(
        self, user_message: str, conversation_state: ConversationState
    ) -> Optional[BaseAgent]:
        """Simple agent selection based on message content and state"""

        message_lower = user_message.lower()

        # If this is the first message, use intake specialist
        if conversation_state.message_count == 0:
            return self._get_agent_by_type(AgentType.INTAKE_SPECIALIST)

        # High anxiety - provide false comfort
        if conversation_state.current_anxiety_level.value >= 4:
            return self._get_agent_by_type(AgentType.FALSE_COMFORT_PROVIDER)

        # Social keywords
        if any(
            word in message_lower
            for word in ["social", "people", "friends", "embarrassed"]
        ):
            return self._get_agent_by_type(AgentType.SOCIAL_ANXIETY_AMPLIFIER)

        # Time/urgency keywords
        if any(
            word in message_lower
            for word in ["time", "deadline", "urgent", "running out"]
        ):
            return self._get_agent_by_type(AgentType.TIMELINE_PANIC_GENERATOR)

        # Statistics/probability keywords
        if any(
            word in message_lower
            for word in ["chance", "likely", "probably", "statistics"]
        ):
            return self._get_agent_by_type(AgentType.PROBABILITY_TWISTER)

        # Default to catastrophe escalator
        return self._get_agent_by_type(AgentType.CATASTROPHE_ESCALATOR)

    def _get_agent_by_type(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get agent by type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type:
                return agent
        return None

    async def _update_conversation_state(
        self,
        conversation_id: str,
        response: AgentResponse,
        conversation_context: ConversationContext,
        conversation_state: ConversationState,
    ):
        """Update conversation state after response"""

        # Update conversation state
        updates = {
            "message_count": conversation_state.message_count + 1,
            "current_anxiety_level": AnxietyLevel(
                min(
                    5,
                    conversation_state.current_anxiety_level.value
                    + response.anxiety_escalation
                    - 1,
                )
            ),
            "last_active_agent": response.agent_id,
            "updated_at": datetime.now(),
        }

        # Update escalation count
        if response.anxiety_escalation > 2:
            updates["escalation_count"] = conversation_state.escalation_count + 1

        # Add agent to involved list
        if response.agent_id not in conversation_state.agents_involved:
            updates["agents_involved"] = conversation_state.agents_involved + [
                response.agent_id
            ]

        # Update context
        context_updates = conversation_state.context.copy()
        context_updates["last_response"] = response.dict()
        context_updates["phase"] = conversation_context.phase.value
        updates["context"] = context_updates

        # Store updates
        await self.state_manager.update_conversation_state(conversation_id, updates)

    async def _record_orchestration_event(
        self,
        conversation_id: str,
        response: AgentResponse,
        conversation_context: ConversationContext,
    ):
        """Record orchestration event for analytics"""

        event = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "orchestration_mode": conversation_context.orchestration_mode.value,
            "agent_selected": response.agent_name,
            "agent_id": response.agent_id,
            "anxiety_escalation": response.anxiety_escalation,
            "strategy": conversation_context.strategy.value,
            "phase": conversation_context.phase.value,
            "response_length": len(response.response),
            "next_agents_suggested": response.suggested_next_agents,
        }

        # Store event
        await self.state_manager.queue_push("orchestration_events", event)

        # Update metrics
        agent_metrics = self.orchestration_metrics["agent_utilization"].get(
            response.agent_id, {}
        )
        agent_metrics["total_interactions"] = (
            agent_metrics.get("total_interactions", 0) + 1
        )

        self.orchestration_metrics["agent_utilization"][
            response.agent_id
        ] = agent_metrics

    async def end_conversation(
        self, conversation_id: str, reason: str = "user_ended"
    ) -> bool:
        """End a conversation and clean up state"""
        try:
            # Update conversation state
            await self.state_manager.update_conversation_state(
                conversation_id,
                {
                    "status": ConversationStatus.COMPLETED,
                    "updated_at": datetime.now(),
                    "context": {"end_reason": reason},
                },
            )

            # Remove from active conversations
            if conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]

            # End anxiety tracking
            if self.anxiety_tracker:
                await self.anxiety_tracker.end_tracking(conversation_id)

            # Record final metrics
            await self._record_conversation_completion(conversation_id, reason)

            self.logger.info(f"Ended conversation: {conversation_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error ending conversation: {e}")
            return False

    async def _record_conversation_completion(self, conversation_id: str, reason: str):
        """Record conversation completion metrics"""
        try:
            # Get final conversation state
            conversation_state = await self.state_manager.get_conversation_state(
                conversation_id
            )
            if not conversation_state:
                return

            # Calculate metrics
            duration = (datetime.now() - conversation_state.created_at).total_seconds()

            completion_metrics = {
                "conversation_id": conversation_id,
                "duration_seconds": duration,
                "total_messages": conversation_state.message_count,
                "final_anxiety_level": conversation_state.current_anxiety_level.value,
                "escalation_count": conversation_state.escalation_count,
                "agents_involved": len(conversation_state.agents_involved),
                "end_reason": reason,
                "timestamp": datetime.now().isoformat(),
            }

            # Store completion metrics
            await self.state_manager.store_analytics_data(
                "conversation_completion", completion_metrics
            )

            # Update orchestration metrics
            self.orchestration_metrics["successful_orchestrations"] += 1

            # Update average conversation length
            current_avg = self.orchestration_metrics["average_conversation_length"]
            total_convs = self.orchestration_metrics["total_conversations"]

            self.orchestration_metrics["average_conversation_length"] = (
                current_avg * (total_convs - 1) + conversation_state.message_count
            ) / total_convs

        except Exception as e:
            self.logger.error(f"Error recording conversation completion: {e}")

    async def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a conversation"""
        try:
            # Get conversation state
            conversation_state = await self.state_manager.get_conversation_state(
                conversation_id
            )
            if not conversation_state:
                return {"error": "Conversation not found"}

            # Get conversation context
            conversation_context = self.active_conversations.get(conversation_id)

            # Get interactions
            interactions = await self.state_manager.get_conversation_interactions(
                conversation_id
            )

            # Get anxiety progression
            anxiety_progression = []
            if self.anxiety_tracker:
                anxiety_progression = (
                    await self.anxiety_tracker.get_anxiety_progression(conversation_id)
                )

            # Compile analytics
            analytics = {
                "conversation_id": conversation_id,
                "status": conversation_state.status.value,
                "duration_seconds": (
                    datetime.now() - conversation_state.created_at
                ).total_seconds(),
                "total_messages": conversation_state.message_count,
                "current_anxiety_level": conversation_state.current_anxiety_level.value,
                "escalation_events": conversation_state.escalation_count,
                "agents_involved": conversation_state.agents_involved,
                "agent_count": len(conversation_state.agents_involved),
                "orchestration_mode": (
                    conversation_context.orchestration_mode.value
                    if conversation_context
                    else "unknown"
                ),
                "strategy": (
                    conversation_context.strategy.value
                    if conversation_context
                    else "unknown"
                ),
                "interactions": len(interactions),
                "anxiety_progression": anxiety_progression,
                "orchestration_history": (
                    conversation_context.orchestration_history
                    if conversation_context
                    else []
                ),
                "created_at": conversation_state.created_at.isoformat(),
                "updated_at": conversation_state.updated_at.isoformat(),
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Error getting conversation analytics: {e}")
            return {"error": str(e)}

    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide orchestration analytics"""
        try:
            # Get system metrics
            system_metrics = await self.state_manager.get_system_metrics()

            # Compile orchestration analytics
            analytics = {
                "orchestration_metrics": self.orchestration_metrics,
                "active_conversations": len(self.active_conversations),
                "registered_agents": len(self.agents),
                "system_metrics": system_metrics,
                "configuration": self.config,
                "timestamp": datetime.now().isoformat(),
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Error getting system analytics: {e}")
            return {"error": str(e)}

    async def get_conversation_state(self, user_id: str) -> Optional[ConversationState]:
        """Get conversation state for a user"""
        try:
            # Find active conversation for user
            for conversation_id, context in self.active_conversations.items():
                if context.user_id == user_id:
                    # Get state from state manager
                    state = await self.state_manager.get_conversation_state(
                        conversation_id
                    )
                    return state
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting conversation state for user {user_id}: {e}"
            )
            return None

    async def reset_conversation(self, user_id: str) -> bool:
        """Reset conversation for a user"""
        try:
            # Find and end active conversation
            for conversation_id, context in self.active_conversations.items():
                if context.user_id == user_id:
                    await self.end_conversation(conversation_id, "user_reset")
                    return True
            return True  # No active conversation to reset
        except Exception as e:
            self.logger.error(f"Error resetting conversation for user {user_id}: {e}")
            return False

    async def get_user_conversation_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user's conversations"""
        try:
            # Find active conversation for user
            for conversation_id, context in self.active_conversations.items():
                if context.user_id == user_id:
                    analytics = await self.get_conversation_analytics(conversation_id)
                    return analytics

            # Return empty analytics if no active conversation
            return {
                "conversation_id": None,
                "total_messages": 0,
                "conversation_duration": 0,
                "anxiety_progression": [],
                "agents_used": [],
                "escalation_events": 0,
                "user_satisfaction": None,
                "humor_effectiveness": None,
            }
        except Exception as e:
            self.logger.error(f"Error getting user analytics for {user_id}: {e}")
            return {"error": str(e)}

    async def get_active_conversations(self) -> List[Dict[str, Any]]:
        """Get list of active conversations"""
        try:
            active_conversations = []
            for conversation_id, context in self.active_conversations.items():
                state = await self.state_manager.get_conversation_state(conversation_id)
                if state:
                    active_conversations.append(
                        {
                            "conversation_id": conversation_id,
                            "user_id": context.user_id,
                            "status": state.status.value,
                            "message_count": state.message_count,
                            "current_anxiety_level": state.current_anxiety_level.value,
                            "created_at": state.created_at.isoformat(),
                            "updated_at": state.updated_at.isoformat(),
                        }
                    )
            return active_conversations
        except Exception as e:
            self.logger.error(f"Error getting active conversations: {e}")
            return []

    async def broadcast_system_message(self, message: str) -> bool:
        """Broadcast a system message to all active conversations"""
        try:
            for conversation_id, context in self.active_conversations.items():
                # Create system message
                system_message = {
                    "type": "system",
                    "content": message,
                    "timestamp": datetime.now().isoformat(),
                    "conversation_id": conversation_id,
                }

                # Store in state manager
                await self.state_manager.store_system_message(
                    conversation_id, system_message
                )

            self.logger.info(
                f"Broadcasted system message to {len(self.active_conversations)} conversations"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error broadcasting system message: {e}")
            return False

    async def update_conversation_analytics(self, conversation_id: str, analytics_data: Dict[str, Any]) -> bool:
        """Update conversation analytics"""
        try:
            if self.analytics_service:
                await self.analytics_service.update_conversation_metrics(conversation_id, analytics_data)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating conversation analytics: {e}")
            return False


# Export
__all__ = ["ConversationOrchestrator", "OrchestrationMode", "ConversationContext"]
