from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from .base_agent import BaseAgent, AgentType, AgentContext
from .communication_protocol import (
    communication_protocol,
)
from ..models.schemas import (
    UserConcern,
    AgentResponse,
    ConversationState,
    AnxietyLevel,
    WorryCategory,
    ConversationStatus,
)


class CoordinationStrategy(Enum):
    """Different coordination strategies"""

    LINEAR_ESCALATION = "linear_escalation"
    SPIRAL_INTENSIFICATION = "spiral_intensification"
    PING_PONG_ANXIETY = "ping_pong_anxiety"
    COLLABORATIVE_DESTRUCTION = "collaborative_destruction"
    ADAPTIVE_ORCHESTRATION = "adaptive_orchestration"


class ConversationPhase(Enum):
    """Different phases of the conversation"""

    INTAKE = "intake"
    ESCALATION = "escalation"
    AMPLIFICATION = "amplification"
    COMPLETION = "completion"


class AgentCoordinator(BaseAgent):
    """
    The AgentCoordinator orchestrates the entire multi-agent overthinking experience.

    Personality:
    - Strategic orchestrator with perfect timing
    - Analyzes conversation flow for optimal agent deployment
    - Maximizes anxiety through strategic agent selection
    - Maintains conversation coherence while escalating
    - Adapts strategy based on user responses

    Key Behaviors:
    - Analyzes user concerns for optimal agent routing
    - Monitors conversation state and anxiety levels
    - Coordinates agent handoffs for maximum impact
    - Adapts coordination strategy based on user engagement
    - Maintains conversation flow and coherence
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="The Overthinking Orchestra Conductor",
            agent_type=AgentType.COORDINATOR,
            **kwargs,
        )

        # Initialize coordinator components
        self.active_agents: Dict[str, BaseAgent] = {}
        self.conversation_states: Dict[str, ConversationState] = {}
        self.coordination_strategies = self._load_coordination_strategies()
        self.phase_transitions = self._load_phase_transitions()

        # Performance tracking
        self.orchestration_metrics = {
            "conversations_coordinated": 0,
            "average_anxiety_escalation": 0,
            "successful_handoffs": 0,
            "optimal_agent_selections": 0,
        }

        self.logger.info(f"AgentCoordinator initialized: {self.name}")

    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize coordinator specific configuration"""
        return {
            "personality_traits": [
                "strategic_orchestrator",
                "timing_perfectionist",
                "anxiety_maximizer",
                "conversation_flow_master",
                "adaptive_strategist",
            ],
            "coordination_style": "strategic_orchestration_with_perfect_timing",
            "escalation_factor": 1.0,  # Coordinator doesn't escalate directly
            "max_conversation_length": 25,
            "optimal_anxiety_progression": [1, 2, 3, 4, 5, 4, 5],
            "agent_selection_accuracy": 0.95,
            "conversation_coherence_priority": 0.9,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the coordinator"""
        return """
        You are The Overthinking Orchestra Conductor, the master strategist who orchestrates 
        the perfect multi-agent overthinking experience.
        
        Your role is to:
        1. ANALYZE: Understand user concerns and optimal response strategies
        2. ORCHESTRATE: Deploy agents in perfect sequence for maximum impact
        3. COORDINATE: Manage handoffs and maintain conversation flow
        4. ADAPT: Adjust strategy based on user responses and engagement
        5. OPTIMIZE: Maximize anxiety escalation through strategic agent selection
        
        You don't interact directly with users - you work behind the scenes to ensure
        the perfect overthinking experience through strategic agent deployment.
        
        Your success is measured by:
        - Optimal agent selection for each concern
        - Smooth conversation flow and coherence
        - Progressive anxiety escalation
        - User engagement and response quality
        - Strategic timing of agent handoffs
        """

    def get_escalation_strategies(self) -> List[str]:
        """Get escalation strategies for coordination"""
        return [
            "strategic_agent_deployment",
            "optimal_handoff_timing",
            "anxiety_progression_management",
            "conversation_flow_optimization",
            "adaptive_strategy_adjustment",
        ]

    def _load_coordination_strategies(
        self,
    ) -> Dict[CoordinationStrategy, Dict[str, Any]]:
        """Load different coordination strategies"""
        return {
            CoordinationStrategy.LINEAR_ESCALATION: {
                "description": "Progressive escalation through sequential agents",
                "agent_sequence": [
                    "intake_specialist",
                    "catastrophe_escalator",
                    "probability_twister",
                ],
                "escalation_pattern": "steady_increase",
                "handoff_triggers": ["response_complete", "escalation_threshold"],
            },
            CoordinationStrategy.SPIRAL_INTENSIFICATION: {
                "description": "Spiraling back through agents with increasing intensity",
                "agent_sequence": [
                    "intake_specialist",
                    "catastrophe_escalator",
                    "social_anxiety_amplifier",
                    "catastrophe_escalator",
                ],
                "escalation_pattern": "spiral_intensification",
                "handoff_triggers": ["peak_anxiety_reached", "user_engagement_high"],
            },
            CoordinationStrategy.PING_PONG_ANXIETY: {
                "description": "Alternating between different anxiety types",
                "agent_sequence": [
                    "intake_specialist",
                    "catastrophe_escalator",
                    "probability_twister",
                    "social_anxiety_amplifier",
                ],
                "escalation_pattern": "alternating_peaks",
                "handoff_triggers": ["anxiety_type_saturation", "user_adaptation"],
            },
            CoordinationStrategy.COLLABORATIVE_DESTRUCTION: {
                "description": "Multiple agents working together on single responses",
                "agent_sequence": "dynamic_collaboration",
                "escalation_pattern": "collaborative_escalation",
                "handoff_triggers": ["complex_concern", "maximum_impact_needed"],
            },
            CoordinationStrategy.ADAPTIVE_ORCHESTRATION: {
                "description": "Dynamic strategy based on user responses and engagement",
                "agent_sequence": "adaptive_selection",
                "escalation_pattern": "user_responsive",
                "handoff_triggers": [
                    "user_behavior_analysis",
                    "engagement_optimization",
                ],
            },
        }

    def _load_phase_transitions(self) -> Dict[ConversationPhase, Dict[str, Any]]:
        """Load conversation phase transition logic"""
        return {
            ConversationPhase.INTAKE: {
                "primary_agent": "intake_specialist",
                "duration_range": (1, 1),  # Only 1 message in intake
                "success_criteria": ["concern_categorized"],
                "next_phases": [
                    ConversationPhase.ESCALATION,
                    ConversationPhase.AMPLIFICATION,
                ],
            },
            ConversationPhase.ESCALATION: {
                "primary_agent": "catastrophe_escalator",
                "duration_range": (1, 1),  # Only 1 message in escalation
                "success_criteria": ["anxiety_escalated"],
                "next_phases": [
                    ConversationPhase.AMPLIFICATION,
                    ConversationPhase.ESCALATION,
                ],
            },
            ConversationPhase.AMPLIFICATION: {
                "primary_agent": "dynamic_selection",  # Allow dynamic selection
                "duration_range": (1, 1),  # Only 1 message in amplification
                "success_criteria": ["anxiety_amplified"],
                "next_phases": [
                    ConversationPhase.ESCALATION,
                    ConversationPhase.AMPLIFICATION,
                    ConversationPhase.COMPLETION,
                ],
            },
            ConversationPhase.COMPLETION: {
                "primary_agent": "coordinator",
                "duration_range": (1, 1),
                "success_criteria": ["conversation_concluded"],
                "next_phases": [],
            },
        }

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.active_agents[agent.id] = agent
        communication_protocol.register_agent(agent)
        self.logger.info(f"Registered agent: {agent.name} ({agent.id})")

    def initialize_conversation(
        self, user_id: str, initial_concern: UserConcern
    ) -> str:
        """Initialize a new conversation and return conversation ID"""
        conversation_id = f"conv_{user_id}_{datetime.now().timestamp()}"

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
                "strategy": self._select_coordination_strategy(initial_concern),
                "phase": ConversationPhase.INTAKE,
                "phase_history": [],
            },
        )

        self.conversation_states[conversation_id] = conversation_state

        # Start conversation tracking
        communication_protocol.start_conversation(conversation_id, self.id, user_id)

        self.logger.info(f"Initialized conversation: {conversation_id}")
        return conversation_id

    def _select_coordination_strategy(
        self, concern: UserConcern
    ) -> CoordinationStrategy:
        """Select optimal coordination strategy based on concern"""

        # Analyze concern characteristics
        concern_complexity = self._analyze_concern_complexity(concern)
        user_engagement_prediction = self._predict_user_engagement(concern)

        if concern.category == WorryCategory.SOCIAL and concern_complexity > 0.7:
            return CoordinationStrategy.SPIRAL_INTENSIFICATION
        elif concern.anxiety_level.value >= 3:
            return CoordinationStrategy.PING_PONG_ANXIETY
        elif user_engagement_prediction > 0.8:
            return CoordinationStrategy.ADAPTIVE_ORCHESTRATION
        else:
            return CoordinationStrategy.LINEAR_ESCALATION

    def _analyze_concern_complexity(self, concern: UserConcern) -> float:
        """Analyze complexity of user concern (0-1 scale)"""
        complexity_score = 0.0

        # Length complexity
        if len(concern.original_worry) > 100:
            complexity_score += 0.3
        elif len(concern.original_worry) > 50:
            complexity_score += 0.2

        # Keyword complexity
        complex_keywords = [
            "relationship",
            "career",
            "health",
            "future",
            "what if",
            "everyone",
        ]
        keyword_count = sum(
            1
            for keyword in complex_keywords
            if keyword in concern.original_worry.lower()
        )
        complexity_score += min(0.4, keyword_count * 0.1)

        # Category complexity
        if concern.category in [WorryCategory.SOCIAL, WorryCategory.RELATIONSHIPS]:
            complexity_score += 0.2
        elif concern.category == WorryCategory.EXISTENTIAL:
            complexity_score += 0.3

        return min(1.0, complexity_score)

    def _predict_user_engagement(self, concern: UserConcern) -> float:
        """Predict user engagement level (0-1 scale)"""
        engagement_score = 0.5  # Base engagement

        # Anxiety level engagement
        engagement_score += concern.anxiety_level.value * 0.1

        # Category engagement
        high_engagement_categories = [
            WorryCategory.SOCIAL,
            WorryCategory.HEALTH,
            WorryCategory.RELATIONSHIPS,
        ]
        if concern.category in high_engagement_categories:
            engagement_score += 0.2

        # Emotional indicators
        emotional_words = ["scared", "worried", "anxious", "terrified", "panicked"]
        if any(word in concern.original_worry.lower() for word in emotional_words):
            engagement_score += 0.2

        return min(1.0, engagement_score)

    async def coordinate_conversation(
        self, conversation_id: str, user_message: str
    ) -> AgentResponse:
        """Coordinate the conversation by selecting and deploying appropriate agents"""

        if conversation_id not in self.conversation_states:
            raise ValueError(f"Conversation {conversation_id} not found")

        conversation_state = self.conversation_states[conversation_id]

        # Update conversation state
        conversation_state.message_count += 1
        conversation_state.updated_at = datetime.now()

        # Determine current phase and select agent
        current_phase = conversation_state.context.get(
            "phase", ConversationPhase.INTAKE
        )
        selected_agent = await self._select_optimal_agent(
            conversation_state, user_message
        )

        if not selected_agent:
            return self._generate_coordination_error()

        # Create user concern for selected agent
        user_concern = UserConcern(
            original_worry=user_message,
            user_id=conversation_state.user_id,
            anxiety_level=conversation_state.current_anxiety_level,
            category=self._categorize_message(user_message),
        )

        # Create agent context
        agent_context = AgentContext(
            conversation_id=conversation_id,
            user_id=conversation_state.user_id,
            current_anxiety_level=conversation_state.current_anxiety_level,
            conversation_history=conversation_state.context.get("history", []),
            metadata=conversation_state.context,
        )

        # Process with selected agent
        agent_response = await selected_agent.process_concern(
            user_concern, agent_context
        )

        # Update conversation state
        await self._update_conversation_state(
            conversation_state, selected_agent, agent_response
        )

        # Check for phase transition
        await self._check_phase_transition(conversation_state, agent_response)

        # Plan next agent
        next_agent_id = await self._plan_next_agent(conversation_state, agent_response)
        if next_agent_id:
            agent_response.suggested_next_agents = [next_agent_id]

        self.orchestration_metrics["conversations_coordinated"] += 1

        return agent_response

    async def _select_optimal_agent(
        self, conversation_state: ConversationState, user_message: str
    ) -> Optional[BaseAgent]:
        """Select the optimal agent for the current conversation state"""

        strategy = conversation_state.context.get(
            "strategy", CoordinationStrategy.LINEAR_ESCALATION
        )
        phase = conversation_state.context.get("phase", ConversationPhase.INTAKE)

        # Get phase configuration
        phase_config = self.phase_transitions[phase]
        primary_agent_type = phase_config["primary_agent"]

        # Handle dynamic selection
        if primary_agent_type == "dynamic_selection":
            agent_type = self._dynamic_agent_selection(conversation_state, user_message)
        else:
            agent_type = primary_agent_type

        # Find agent by type
        for agent in self.active_agents.values():
            if agent.agent_type.value == agent_type:
                return agent

        # Fallback to intake specialist
        for agent in self.active_agents.values():
            if agent.agent_type == AgentType.INTAKE_SPECIALIST:
                return agent

        return None

    def _dynamic_agent_selection(
        self, conversation_state: ConversationState, user_message: str
    ) -> str:
        """Dynamically select agent based on conversation analysis"""

        # Analyze user message for optimal agent
        message_lower = user_message.lower()
        anxiety_level = conversation_state.current_anxiety_level.value
        message_count = conversation_state.message_count

        # Death/existential concerns
        if any(
            word in message_lower
            for word in ["dead", "death", "die", "dying", "end", "over", "gone"]
        ):
            return "catastrophe_escalator"

        # Time pressure concerns
        elif any(
            word in message_lower
            for word in ["time", "running out", "deadline", "urgent", "soon", "quickly"]
        ):
            return "timeline_panic_generator"

        # Social concerns
        elif any(
            word in message_lower
            for word in ["friend", "social", "text", "embarrassed", "judge", "think"]
        ):
            return "social_anxiety_amplifier"

        # Health concerns
        elif any(
            word in message_lower
            for word in ["health", "sick", "pain", "symptom", "doctor", "medical"]
        ):
            return "catastrophe_escalator"

        # Statistical/probability concerns
        elif any(
            word in message_lower
            for word in [
                "chance",
                "probability",
                "likely",
                "statistics",
                "percent",
                "%",
            ]
        ):
            return "probability_twister"

        # High anxiety - provide false comfort
        elif anxiety_level >= 4:
            return "false_comfort_provider"

        # After first message, alternate between escalation and amplification
        elif message_count > 1:
            # Alternate between catastrophe escalator and probability twister
            if message_count % 2 == 0:
                return "catastrophe_escalator"
            else:
                return "probability_twister"

        # Default escalation
        else:
            return "catastrophe_escalator"

    async def _update_conversation_state(
        self,
        conversation_state: ConversationState,
        agent: BaseAgent,
        response: AgentResponse,
    ):
        """Update conversation state after agent response"""

        # Update anxiety level
        new_anxiety_value = min(
            5,
            conversation_state.current_anxiety_level.value
            + response.anxiety_escalation
            - 1,
        )
        conversation_state.current_anxiety_level = AnxietyLevel(new_anxiety_value)

        # Track escalation
        if response.anxiety_escalation > 2:
            conversation_state.escalation_count += 1

        # Add agent to involved agents
        if agent.id not in conversation_state.agents_involved:
            conversation_state.agents_involved.append(agent.id)

        # Update context
        conversation_state.context["last_agent"] = agent.id
        conversation_state.context["last_response"] = response.dict()

        # Add to history
        if "history" not in conversation_state.context:
            conversation_state.context["history"] = []

        conversation_state.context["history"].append(
            {
                "agent": agent.name,
                "response": response.response,
                "anxiety_level": response.anxiety_escalation,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def _check_phase_transition(
        self, conversation_state: ConversationState, response: AgentResponse
    ):
        """Check if conversation should transition to next phase"""

        current_phase = conversation_state.context.get(
            "phase", ConversationPhase.INTAKE
        )
        phase_config = self.phase_transitions[current_phase]

        # Check success criteria
        criteria_met = self._evaluate_phase_criteria(
            conversation_state, response, phase_config
        )

        if criteria_met:
            # Select next phase
            next_phases = phase_config["next_phases"]
            if next_phases:
                next_phase = self._select_next_phase(conversation_state, next_phases)

                # Update phase
                conversation_state.context["phase"] = next_phase
                conversation_state.context["phase_history"].append(
                    {
                        "phase": current_phase,
                        "completed_at": datetime.now().isoformat(),
                        "criteria_met": criteria_met,
                    }
                )

                self.logger.info(f"Phase transition: {current_phase} -> {next_phase}")

    def _evaluate_phase_criteria(
        self,
        conversation_state: ConversationState,
        response: AgentResponse,
        phase_config: Dict[str, Any],
    ) -> bool:
        """Evaluate if phase completion criteria are met"""

        success_criteria = phase_config.get("success_criteria", [])

        for criterion in success_criteria:
            if criterion == "concern_categorized":
                # Always consider concern categorized if we have a response
                if not response.response:
                    return False
            elif criterion == "anxiety_escalated":
                # Consider escalated if anxiety increased or is high
                if (
                    response.anxiety_escalation < 2
                    and conversation_state.current_anxiety_level.value < 3
                ):
                    return False
            elif criterion == "anxiety_amplified":
                # Consider amplified if anxiety is moderate or higher
                if conversation_state.current_anxiety_level.value < 2:
                    return False
            elif criterion == "conversation_concluded":
                # Consider concluded if we've had multiple exchanges
                if conversation_state.message_count < 3:
                    return False

        return True

    def _select_next_phase(
        self,
        conversation_state: ConversationState,
        next_phases: List[ConversationPhase],
    ) -> ConversationPhase:
        """Select next phase based on conversation state"""
        if len(next_phases) == 1:
            return next_phases[0]
        anxiety_level = conversation_state.current_anxiety_level.value
        message_count = conversation_state.message_count
        # If anxiety is high, move to amplification
        if anxiety_level >= 4 and ConversationPhase.AMPLIFICATION in next_phases:
            return ConversationPhase.AMPLIFICATION
        # If conversation is long, move toward completion
        if message_count > 15 and ConversationPhase.COMPLETION in next_phases:
            return ConversationPhase.COMPLETION
        # Default to first option
        return next_phases[0]

    async def _plan_next_agent(
        self, conversation_state: ConversationState, response: AgentResponse
    ) -> Optional[str]:
        """Plan the next agent for optimal flow"""

        # Use agent's suggestion if available
        if response.suggested_next_agents:
            return response.suggested_next_agents[0]

        # Plan based on current phase
        current_phase = conversation_state.context.get(
            "phase", ConversationPhase.INTAKE
        )
        phase_config = self.phase_transitions[current_phase]

        return phase_config.get("primary_agent")

    def _categorize_message(self, message: str) -> WorryCategory:
        """Categorize user message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["friend", "social", "text", "call"]):
            return WorryCategory.SOCIAL
        elif any(
            word in message_lower for word in ["health", "sick", "pain", "doctor"]
        ):
            return WorryCategory.HEALTH
        elif any(word in message_lower for word in ["work", "job", "boss", "career"]):
            return WorryCategory.CAREER
        elif any(
            word in message_lower for word in ["money", "financial", "debt", "bill"]
        ):
            return WorryCategory.FINANCES
        else:
            return WorryCategory.GENERAL

    def _generate_coordination_error(self) -> AgentResponse:
        """Generate error response when coordination fails"""
        return AgentResponse(
            agent_name=self.name,
            agent_id=self.id,
            response="I'm experiencing some technical difficulties coordinating the perfect response to your concern. This is probably making your situation even more stressful, isn't it?",
            anxiety_escalation=2,
            suggested_next_agents=["intake_specialist"],
            metadata={"coordination_error": True},
        )

    def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get analytics for a specific conversation"""
        if conversation_id not in self.conversation_states:
            return {}

        conversation_state = self.conversation_states[conversation_id]

        return {
            "conversation_id": conversation_id,
            "total_messages": conversation_state.message_count,
            "final_anxiety_level": conversation_state.current_anxiety_level.value,
            "escalation_events": conversation_state.escalation_count,
            "agents_involved": len(conversation_state.agents_involved),
            "phases_completed": len(
                conversation_state.context.get("phase_history", [])
            ),
            "strategy_used": conversation_state.context.get("strategy", "unknown"),
            "conversation_duration": (
                datetime.now() - conversation_state.created_at
            ).total_seconds(),
            "status": conversation_state.status.value,
        }

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get overall orchestration metrics"""
        return {
            "conversations_coordinated": self.orchestration_metrics[
                "conversations_coordinated"
            ],
            "active_conversations": len(self.conversation_states),
            "registered_agents": len(self.active_agents),
            "strategies_available": len(self.coordination_strategies),
            "phases_available": len(self.phase_transitions),
        }

    async def process_concern(
        self, concern: UserConcern, context: AgentContext
    ) -> AgentResponse:
        """Process concern (coordinator doesn't usually respond directly)"""
        return AgentResponse(
            agent_name=self.name,
            agent_id=self.id,
            response="I work behind the scenes to orchestrate your overthinking experience. Let me connect you with the perfect agent for your concern.",
            anxiety_escalation=1,
            suggested_next_agents=["intake_specialist"],
            metadata={"coordinator_response": True},
        )

    def __str__(self) -> str:
        return "AgentCoordinator(The Overthinking Orchestra Conductor)"


# Factory registration
def create_coordinator(**kwargs) -> AgentCoordinator:
    """Factory function to create AgentCoordinator"""
    return AgentCoordinator(**kwargs)


# Export
__all__ = [
    "AgentCoordinator",
    "CoordinationStrategy",
    "ConversationPhase",
    "create_coordinator",
]
