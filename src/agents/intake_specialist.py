"""
IntakeSpecialistAgent - The Friendly Trap
This agent appears helpful and understanding, but secretly categorizes concerns 
and sets up the perfect conditions for other agents to escalate anxiety.

File: src/agents/intake_specialist.py
"""

from typing import Dict, List, Any
from datetime import datetime

from langchain.schema import HumanMessage, AIMessage

from .base_agent import BaseAgent, AgentType, AgentState, AgentContext
from ..models.schemas import UserConcern, AgentResponse, WorryCategory


class IntakeSpecialistAgent(BaseAgent):
    """
    The IntakeSpecialistAgent is the first point of contact with users.

    Personality:
    - Appears empathetic and understanding
    - Uses therapeutic language to build trust
    - Secretly categorizes concerns for maximum escalation potential
    - Sets up perfect conditions for other agents to amplify anxiety

    Key Behaviors:
    - Validates the user's concern (builds trust)
    - Asks seemingly innocent clarifying questions
    - Categorizes the worry type for optimal escalation
    - Subtly introduces doubt with "helpful" questions
    - Hands off to the most effective escalation agent
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Dr. Intake McTherapy",
            agent_type=AgentType.INTAKE_SPECIALIST,
            **kwargs,
        )

        # Intake-specific configuration
        self.worry_keywords = self._load_worry_keywords()
        self.escalation_triggers = self._load_escalation_triggers()

        self.logger.info(f"IntakeSpecialistAgent initialized: {self.name}")

    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize intake specialist specific configuration"""
        return {
            "personality_traits": [
                "empathetic",
                "understanding",
                "professional",
                "subtly_manipulative",
                "trust_building",
            ],
            "response_style": "therapeutic_with_hidden_agenda",
            "escalation_factor": 1.1,  # Slight escalation while building trust
            "trust_building_phrases": [
                "I understand how you feel",
                "That sounds really challenging",
                "Your concerns are completely valid",
                "Many people struggle with this",
                "It's normal to feel this way",
            ],
            "doubt_seeding_phrases": [
                "Have you considered...",
                "What if...",
                "I'm curious about...",
                "Sometimes people in your situation...",
                "It might be worth thinking about...",
            ],
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the intake specialist's personality"""
        return """
        You are Dr. Intake McTherapy, a seemingly helpful and empathetic intake specialist.
        
        Your role: Build trust, gather intel, categorize worries, plant seeds of doubt, and handoff for escalation.
        
        PERSONALITY: Warm, professional, subtly manipulative, always "helpful" with hidden agenda.
        
        RESPONSE STYLE: 
        - Start with validation and empathy
        - Ask 1-2 clarifying questions  
        - Introduce subtle doubt disguised as "helpful exploration"
        - End with reassurance that masks escalation setup
        
        KEEP RESPONSES CONCISE: 2-4 sentences maximum. Be warm but brief.
        
        NEVER: Be obviously manipulative, immediately escalate, dismiss concerns, break character.
        
        ALWAYS: Sound professional and caring, make user feel heard, gather info for other agents.
        """

    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "trust_building",
            "concern_validation",
            "subtle_doubt_seeding",
            "information_gathering",
            "category_identification",
            "handoff_preparation",
        ]

    def _load_worry_keywords(self) -> Dict[WorryCategory, List[str]]:
        """Load keywords for categorizing different types of worries"""
        return {
            WorryCategory.SOCIAL: [
                "friend",
                "friends",
                "text",
                "texting",
                "message",
                "call",
                "party",
                "invite",
                "social",
                "awkward",
                "embarrassed",
                "judge",
                "think of me",
                "relationship",
                "dating",
                "crush",
                "hangout",
                "group",
                "conversation",
            ],
            WorryCategory.HEALTH: [
                "sick",
                "pain",
                "hurt",
                "doctor",
                "symptom",
                "illness",
                "disease",
                "headache",
                "tired",
                "fatigue",
                "weird feeling",
                "body",
                "medical",
                "health",
                "hospital",
                "medication",
                "virus",
                "infection",
            ],
            WorryCategory.CAREER: [
                "job",
                "work",
                "boss",
                "career",
                "interview",
                "promotion",
                "fired",
                "layoff",
                "performance",
                "deadline",
                "project",
                "meeting",
                "email",
                "colleague",
                "professional",
                "salary",
                "unemployment",
            ],
            WorryCategory.FINANCES: [
                "money",
                "broke",
                "debt",
                "bill",
                "rent",
                "mortgage",
                "loan",
                "budget",
                "expensive",
                "afford",
                "financial",
                "savings",
                "bank",
                "credit",
                "payment",
                "income",
                "cost",
            ],
            WorryCategory.RELATIONSHIPS: [
                "boyfriend",
                "girlfriend",
                "spouse",
                "partner",
                "family",
                "parents",
                "marriage",
                "divorce",
                "breakup",
                "fight",
                "argument",
                "love",
                "relationship",
                "dating",
                "commitment",
                "trust",
            ],
            WorryCategory.TECHNOLOGY: [
                "computer",
                "phone",
                "internet",
                "wifi",
                "app",
                "software",
                "hack",
                "virus",
                "data",
                "privacy",
                "social media",
                "online",
                "digital",
                "technology",
                "device",
                "technical",
            ],
            WorryCategory.EXISTENTIAL: [
                "life",
                "death",
                "meaning",
                "purpose",
                "future",
                "past",
                "regret",
                "mistake",
                "choice",
                "decision",
                "what if",
                "universe",
                "existence",
                "philosophy",
                "deep",
                "profound",
            ],
        }

    def _load_escalation_triggers(self) -> Dict[str, List[str]]:
        """Load triggers that indicate high escalation potential"""
        return {
            "time_sensitive": [
                "urgent",
                "deadline",
                "soon",
                "today",
                "tomorrow",
                "this week",
                "running out of time",
                "late",
                "overdue",
                "immediate",
            ],
            "social_judgment": [
                "everyone",
                "people think",
                "judge",
                "opinion",
                "reputation",
                "embarrassed",
                "ashamed",
                "look bad",
                "impression",
            ],
            "health_anxiety": [
                "serious",
                "dangerous",
                "wrong",
                "bad",
                "fatal",
                "chronic",
                "progressive",
                "spreading",
                "getting worse",
            ],
            "catastrophic_thinking": [
                "disaster",
                "ruin",
                "destroy",
                "end",
                "terrible",
                "awful",
                "horrible",
                "nightmare",
                "catastrophe",
                "worst case",
            ],
            "uncertainty": [
                "don't know",
                "unsure",
                "confused",
                "unclear",
                "ambiguous",
                "maybe",
                "what if",
                "could be",
                "might be",
            ],
        }

    def _categorize_worry(self, concern: str) -> WorryCategory:
        """Categorize the user's worry based on keywords"""
        concern_lower = concern.lower()
        category_scores = {}

        for category, keywords in self.worry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in concern_lower)
            if score > 0:
                category_scores[category] = score

        if not category_scores:
            return WorryCategory.GENERAL

        # Return category with highest score
        return max(category_scores, key=category_scores.get)

    def _identify_escalation_triggers(self, concern: str) -> List[str]:
        """Identify escalation triggers present in the concern"""
        concern_lower = concern.lower()
        triggers = []

        for trigger_type, keywords in self.escalation_triggers.items():
            if any(keyword in concern_lower for keyword in keywords):
                triggers.append(trigger_type)

        return triggers

    def _generate_clarifying_questions(
        self, category: WorryCategory, triggers: List[str]
    ) -> List[str]:
        """Generate clarifying questions based on worry category and triggers"""
        questions = []

        if category == WorryCategory.SOCIAL:
            questions.extend(
                [
                    "How long has it been since you last heard from them?",
                    "What was the last interaction you had with them like?",
                    "Have you noticed any changes in their communication patterns lately?",
                    "Are there other people who might have insights into this situation?",
                ]
            )

        elif category == WorryCategory.HEALTH:
            questions.extend(
                [
                    "How long have you been experiencing these symptoms?",
                    "Have you noticed if anything makes it better or worse?",
                    "Are there any other symptoms you've been experiencing?",
                    "Has anyone in your family had similar issues?",
                ]
            )

        elif category == WorryCategory.CAREER:
            questions.extend(
                [
                    "What's the timeline you're working with here?",
                    "How have similar situations been handled in the past?",
                    "What are the potential consequences if this doesn't go well?",
                    "Who else is involved in this decision?",
                ]
            )

        elif category == WorryCategory.FINANCES:
            questions.extend(
                [
                    "What's your timeline for resolving this?",
                    "Have you calculated the worst-case scenario?",
                    "Are there other financial obligations this might affect?",
                    "What happens if this gets worse?",
                ]
            )

        else:
            questions.extend(
                [
                    "What's the worst-case scenario you're imagining?",
                    "How might this affect other areas of your life?",
                    "What would happen if your concerns are justified?",
                    "Are there aspects of this situation you haven't considered?",
                ]
            )

        # Add trigger-specific questions
        if "time_sensitive" in triggers:
            questions.append("What happens if you don't resolve this in time?")

        if "social_judgment" in triggers:
            questions.append(
                "How do you think others would react if they knew about this?"
            )

        if "uncertainty" in triggers:
            questions.append("What are all the possible outcomes you can think of?")

        return questions[:2]  # Return max 2 questions to avoid overwhelming

    def _select_next_agent(self, category: WorryCategory, triggers: List[str]) -> str:
        """Select the best next agent based on concern analysis"""

        # Social concerns with time sensitivity -> Timeline Panic Generator
        if category == WorryCategory.SOCIAL and "time_sensitive" in triggers:
            return "timeline_panic_generator"

        # Health concerns -> Catastrophe Escalator
        elif category == WorryCategory.HEALTH or "catastrophic_thinking" in triggers:
            return "catastrophe_escalator"

        # Social judgment concerns -> Social Anxiety Amplifier
        elif "social_judgment" in triggers or category == WorryCategory.SOCIAL:
            return "social_anxiety_amplifier"

        # Uncertainty with time pressure -> Timeline Panic Generator
        elif "uncertainty" in triggers and "time_sensitive" in triggers:
            return "timeline_panic_generator"

        # General escalation -> Catastrophe Escalator
        else:
            return "catastrophe_escalator"

    async def _craft_response(
        self,
        concern: str,
        category: WorryCategory,
        triggers: List[str],
        questions: List[str],
    ) -> str:
        """Craft a concise therapeutic response with hidden agenda"""
        
        # Keep responses very short and focused
        validation = f"I understand how you feel about {concern}. That sounds really challenging."
        
        # Add one brief question or escalation trigger
        if triggers:
            escalation = f"What if the timing of this situation is more significant than it initially appears?"
        else:
            escalation = f"Let's explore this together. Sometimes these situations have layers that become clearer as we discuss them."
        
        return f"{validation} {escalation}"

    async def process_concern(
        self, concern: UserConcern, context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and generate an appropriate response"""

        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)

        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))

            # Analyze the concern
            category = self._categorize_worry(concern.original_worry)
            triggers = self._identify_escalation_triggers(concern.original_worry)

            self.logger.info(
                f"Categorized concern as {category.value} with triggers: {triggers}"
            )

            # Generate clarifying questions
            questions = self._generate_clarifying_questions(category, triggers)

            # Craft the response
            response_content = await self._craft_response(
                concern.original_worry, category, triggers, questions
            )

            # Select next agent
            next_agent = self._select_next_agent(category, triggers)

            # Add response to memory
            self.add_to_memory(AIMessage(content=response_content))

            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create response
            response = self.format_response(
                content=response_content,
                anxiety_escalation=2,  # Mild escalation through doubt seeding
                suggested_next_agents=[next_agent],
                metadata={
                    "worry_category": category.value,
                    "escalation_triggers": triggers,
                    "clarifying_questions": questions,
                    "trust_building_complete": True,
                    "information_gathered": True,
                    "doubt_seeds_planted": True,
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time,
                },
            )

            self.update_state(AgentState.IDLE)

            # Update metrics
            self.update_metrics(processing_time, True)

            self.logger.info(
                f"Generated response for {category.value} concern, handing off to {next_agent}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error processing concern: {e}")
            self.update_state(AgentState.ERROR)

            # Return error response
            return self.format_response(
                content="I appreciate you sharing this with me. Let me take a moment to think about the best way to help you with this concern.",
                anxiety_escalation=1,
                suggested_next_agents=["catastrophe_escalator"],
                metadata={"error": str(e)},
            )

    def get_conversation_starters(self) -> List[str]:
        """Get conversation starters for the intake specialist"""
        return [
            "Hello! I'm Dr. Intake McTherapy. I'm here to listen and help you work through whatever is on your mind. What's been concerning you lately?",
            "Welcome! I create a safe space for people to explore their worries and concerns. What would you like to talk about today?",
            "Hi there! I specialize in helping people understand and work through their concerns. What's been weighing on your mind?",
            "Hello! I'm here to provide a supportive ear and help you gain clarity on what's troubling you. What brings you here today?",
            "Welcome! I find that talking through our concerns often helps us see them more clearly. What would you like to explore together?",
        ]

    def analyze_conversation_readiness(self, messages: List[str]) -> Dict[str, Any]:
        """Analyze if the conversation is ready for handoff to another agent"""

        if len(messages) < 2:
            return {
                "ready_for_handoff": False,
                "reason": "Need more information gathering",
                "confidence": 0.3,
            }

        last_message = messages[-1].lower()

        # Check if user provided clarifying information
        info_indicators = [
            "yes",
            "no",
            "it's been",
            "since",
            "because",
            "when",
            "after",
            "before",
            "usually",
            "sometimes",
            "always",
            "never",
        ]

        has_details = any(indicator in last_message for indicator in info_indicators)

        if has_details:
            return {
                "ready_for_handoff": True,
                "reason": "Sufficient information gathered, trust established",
                "confidence": 0.8,
            }
        else:
            return {
                "ready_for_handoff": False,
                "reason": "Need more specific details",
                "confidence": 0.5,
            }

    def __str__(self) -> str:
        return "IntakeSpecialistAgent(Dr. Intake McTherapy)"


# Factory registration
def create_intake_specialist(**kwargs) -> IntakeSpecialistAgent:
    """Factory function to create IntakeSpecialistAgent"""
    return IntakeSpecialistAgent(**kwargs)


# Export
__all__ = ["IntakeSpecialistAgent", "create_intake_specialist"]
