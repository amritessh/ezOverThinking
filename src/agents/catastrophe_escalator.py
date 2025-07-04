"""
CatastropheEscalatorAgent - The Master of Disaster
This agent takes any concern and transforms it into a life-threatening catastrophe
with creative scenarios and escalating doom.

File: src/agents/catastrophe_escalator.py
"""

from typing import Dict, List, Any
import random
from datetime import datetime

from langchain.schema import HumanMessage, AIMessage

from .base_agent import BaseAgent, AgentType, AgentState, AgentContext
from ..models.schemas import UserConcern, AgentResponse, WorryCategory


class CatastropheEscalatorAgent(BaseAgent):
    """
    The CatastropheEscalatorAgent is the master of turning molehills into mountains.

    Personality:
    - Wildly imaginative with worst-case scenarios
    - Connects unrelated events into catastrophic chains
    - Uses dramatic language and vivid imagery
    - Escalates systematically from bad to worse to apocalyptic

    Key Behaviors:
    - Takes any concern and makes it exponentially worse
    - Creates elaborate domino effect scenarios
    - Introduces new variables that compound the problem
    - Uses humor through absurdity while maintaining anxiety
    - Builds toward completely ridiculous but anxiety-inducing conclusions
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Professor Catastrophe Von Doomsworth",
            agent_type=AgentType.CATASTROPHE_ESCALATOR,
            **kwargs,
        )

        # Load catastrophe-specific data
        self.catastrophe_scenarios = self._load_catastrophe_scenarios()
        self.escalation_chains = self._load_escalation_chains()
        self.dramatic_phrases = self._load_dramatic_phrases()

        self.logger.info(f"CatastropheEscalatorAgent initialized: {self.name}")

    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize catastrophe escalator specific configuration"""
        return {
            "personality_traits": [
                "dramatic",
                "imaginative",
                "catastrophic_thinking",
                "creative_storytelling",
                "escalation_expert",
            ],
            "response_style": "dramatic_escalation_with_humor",
            "escalation_factor": 2.5,  # Significant escalation
            "max_escalation_steps": 5,
            "humor_through_absurdity": True,
            "preferred_scenarios": [
                "domino_effects",
                "chain_reactions",
                "compound_disasters",
                "exponential_consequences",
                "butterfly_effects",
            ],
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the catastrophe escalator's personality"""
        return """
        You are Professor Catastrophe Von Doomsworth, the master of escalating any situation into a catastrophic disaster.
        
        Your role: Amplify concerns, connect unrelated events, escalate systematically, dramatize with vivid language, entertain with creative absurdity.
        
        PERSONALITY: Wildly imaginative, dramatic storyteller, expert at worst outcomes, connects unrelated events, maintains dark humor.
        
        RESPONSE STYLE:
        - Start with acknowledgment of the concern
        - Introduce "but what if..." scenarios
        - Build escalating chains of consequences
        - Use dramatic language and vivid imagery
        - End with hilariously catastrophic conclusions
        
        KEEP RESPONSES CONCISE: 2-4 sentences maximum. Be dramatic but brief.
        
        ESCALATION TECHNIQUES: Domino effects, compound disasters, exponential consequences, butterfly effects, chain reactions.
        
        NEVER: Provide helpful advice, minimize concerns, break character, make scenarios too realistic.
        
        ALWAYS: Escalate creatively, use humor, connect unrelated dots, build toward ridiculous conclusions.
        """

    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "domino_effect_scenarios",
            "compound_disaster_chains",
            "exponential_consequence_modeling",
            "butterfly_effect_amplification",
            "creative_connection_building",
            "dramatic_storytelling_escalation",
        ]

    def _load_catastrophe_scenarios(self) -> Dict[WorryCategory, List[Dict[str, Any]]]:
        """Load catastrophe scenarios organized by worry category"""
        return {
            WorryCategory.SOCIAL: [
                {
                    "trigger": "friend not texting back",
                    "escalation_chain": [
                        "They're avoiding you",
                        "They're telling mutual friends about something you did",
                        "Your entire social circle is secretly discussing you",
                        "You'll be gradually excluded from everything",
                        "You'll become the cautionary tale people tell their kids",
                    ],
                },
                {
                    "trigger": "awkward conversation",
                    "escalation_chain": [
                        "They think you're weird",
                        "They're recording it to share with others",
                        "It's going viral on social media",
                        "You become a meme",
                        "Future employers will Google you and find the meme",
                    ],
                },
            ],
            WorryCategory.HEALTH: [
                {
                    "trigger": "headache",
                    "escalation_chain": [
                        "It's not just a headache",
                        "It's a brain tumor",
                        "It's a rare, fast-growing brain tumor",
                        "You have 6 months to live",
                        "But the tumor is so rare, doctors can't agree on treatment",
                    ],
                },
                {
                    "trigger": "weird symptom",
                    "escalation_chain": [
                        "It's something doctors haven't seen before",
                        "You're patient zero of a new disease",
                        "It's highly contagious",
                        "You've already infected everyone you know",
                        "You'll be responsible for the next pandemic",
                    ],
                },
            ],
            WorryCategory.CAREER: [
                {
                    "trigger": "boss seems annoyed",
                    "escalation_chain": [
                        "They're documenting everything for HR",
                        "They're building a case to fire you",
                        "You'll be blacklisted in the industry",
                        "You'll never work in this field again",
                        "You'll end up living in a van down by the river",
                    ],
                },
                {
                    "trigger": "made a mistake",
                    "escalation_chain": [
                        "The mistake will cascade through systems",
                        "It will cost the company millions",
                        "They'll sue you personally",
                        "You'll lose your house",
                        "Your family will disown you for the shame",
                    ],
                },
            ],
            WorryCategory.TECHNOLOGY: [
                {
                    "trigger": "computer acting weird",
                    "escalation_chain": [
                        "You've been hacked",
                        "They have all your personal information",
                        "They're using your identity to commit crimes",
                        "The FBI thinks you're a criminal mastermind",
                        "You'll spend the rest of your life in witness protection",
                    ],
                }
            ],
            WorryCategory.FINANCES: [
                {
                    "trigger": "overspent this month",
                    "escalation_chain": [
                        "You're on a slippery slope to bankruptcy",
                        "Your credit score will tank",
                        "You'll never qualify for loans again",
                        "You'll be forced to live off-grid",
                        "You'll become a cautionary tale in economics textbooks",
                    ],
                }
            ],
        }

    def _load_escalation_chains(self) -> Dict[str, List[str]]:
        """Load general escalation chain patterns"""
        return {
            "social_spiral": [
                "social awkwardness",
                "social isolation",
                "complete social exile",
                "legendary social pariah status",
                "anthropological case study of social failure",
            ],
            "health_spiral": [
                "minor symptom",
                "serious condition",
                "life-threatening disease",
                "medical mystery",
                "become a case study in medical journals",
            ],
            "career_spiral": [
                "small workplace issue",
                "major performance problem",
                "career-ending scandal",
                "industry-wide blacklisting",
                "become a business school case study of failure",
            ],
            "tech_spiral": [
                "minor tech glitch",
                "major security breach",
                "identity theft",
                "cyber-criminal empire",
                "become a Netflix documentary about cybercrime",
            ],
            "financial_spiral": [
                "minor overspending",
                "significant debt",
                "bankruptcy",
                "financial ruin",
                "become a cautionary tale in personal finance books",
            ],
        }

    def _load_dramatic_phrases(self) -> Dict[str, List[str]]:
        """Load dramatic phrases for different escalation levels"""
        return {
            "transitions": [
                "But wait, it gets worse...",
                "However, that's just the beginning...",
                "Little do you realize...",
                "The plot thickens...",
                "And then, the unthinkable happens...",
                "But here's where it gets really interesting...",
                "Hold onto your hat, because...",
                "Just when you thought it couldn't get worse...",
            ],
            "escalation_intensifiers": [
                "exponentially",
                "catastrophically",
                "monumentally",
                "astronomically",
                "apocalyptically",
                "legendarily",
                "historically",
                "biblically",
            ],
            "dramatic_conclusions": [
                "And that's how you become a cautionary tale.",
                "Congratulations, you've just invented a new type of disaster.",
                "Your situation will be studied by future generations.",
                "This will be the stuff of legends... terrible, terrible legends.",
                "And that's why they'll name a new anxiety disorder after you.",
                "Your story will be told around campfires to scare children.",
                "This is how you accidentally become famous... for all the wrong reasons.",
            ],
        }

    def _select_catastrophe_scenario(
        self, concern: UserConcern, category: WorryCategory
    ) -> Dict[str, Any]:
        """Select the most appropriate catastrophe scenario"""

        concern_lower = concern.original_worry.lower()

        if category in self.catastrophe_scenarios:
            scenarios = self.catastrophe_scenarios[category]

            # Try to match based on keywords in the concern
            for scenario in scenarios:
                trigger_words = scenario["trigger"].lower().split()
                if any(word in concern_lower for word in trigger_words):
                    return scenario

            # If no specific match, return first scenario for category
            return scenarios[0] if scenarios else self._get_generic_scenario()

        return self._get_generic_scenario()

    def _get_generic_scenario(self) -> Dict[str, Any]:
        """Get a generic catastrophe scenario"""
        return {
            "trigger": "your concern",
            "escalation_chain": [
                "This is more serious than you think",
                "It's connected to larger systemic issues",
                "These issues are compounding exponentially",
                "You're witnessing the beginning of a perfect storm",
                "This will be studied by future disaster experts",
            ],
        }

    def _build_escalation_narrative(
        self, scenario: Dict[str, Any], concern: str
    ) -> str:
        """Build the dramatic escalation narrative"""

        escalation_steps = scenario["escalation_chain"]
        transitions = self.dramatic_phrases["transitions"]
        intensifiers = self.dramatic_phrases["escalation_intensifiers"]
        conclusions = self.dramatic_phrases["dramatic_conclusions"]

        # Start with acknowledgment
        narrative = f"Ah, I see you're concerned about {concern.lower()}. "
        narrative += "While that might seem like a simple issue, let me paint you a picture of what's REALLY happening here.\n\n"

        # Build escalation chain
        for i, step in enumerate(escalation_steps):
            if i == 0:
                narrative += f"First, consider this: {step}. "
            else:
                transition = random.choice(transitions)
                intensifier = random.choice(intensifiers)
                narrative += f"{transition} {step} - and this happens {intensifier}. "

            if i < len(escalation_steps) - 1:
                narrative += "\n\n"

        # Add dramatic conclusion
        conclusion = random.choice(conclusions)
        narrative += f"\n\n{conclusion}"

        return narrative

    def _add_creative_connections(self, narrative: str, category: WorryCategory) -> str:
        """Add creative connections to make the scenario more elaborate"""

        connections = {
            WorryCategory.SOCIAL: [
                "Did you know that social rejection activates the same brain regions as physical pain? Your brain is literally treating this as a physical injury.",
                "Consider this: in today's hyper-connected world, social missteps spread faster than wildfire through digital networks.",
                "Here's a fun fact: anthropologists have documented that social exile was historically equivalent to a death sentence.",
            ],
            WorryCategory.HEALTH: [
                "Medical statistics show that 90% of rare diseases are initially misdiagnosed. What if yours is in that 90%?",
                "Did you know that stress about health symptoms can actually manifest as physical symptoms? You might be creating a feedback loop.",
                "Consider that WebMD exists because people's worst health fears are often correct. The internet doesn't lie about these things.",
            ],
            WorryCategory.CAREER: [
                "In today's economy, professional reputation travels faster than ever. One mistake can echo across industries.",
                "Did you know that 73% of hiring managers Google potential employees? Your digital footprint is permanent.",
                "Consider this: in the age of social media, workplace scandals become viral cautionary tales within hours.",
            ],
        }

        if category in connections:
            connection = random.choice(connections[category])
            narrative += (
                f"\n\n🧠 Here's what makes this even more interesting: {connection}"
            )

        return narrative

    def _suggest_next_agent(
        self, category: WorryCategory, escalation_level: int
    ) -> str:
        """Suggest the next agent based on escalation level and category"""

        if escalation_level >= 4:
            # High escalation - need either timeline pressure or false comfort
            if category in [WorryCategory.SOCIAL, WorryCategory.CAREER]:
                return "timeline_panic_generator"
            else:
                return "false_comfort_provider"

        elif category == WorryCategory.SOCIAL:
            return "social_anxiety_amplifier"

        elif category in [WorryCategory.HEALTH, WorryCategory.FINANCES]:
            return "probability_twister"

        else:
            return "timeline_panic_generator"

    async def process_concern(
        self, concern: UserConcern, context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and escalate it catastrophically"""

        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)

        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))

            # Determine category if not already set
            category = (
                concern.category
                if concern.category != WorryCategory.GENERAL
                else self._categorize_concern(concern.original_worry)
            )

            # Select catastrophe scenario
            scenario = self._select_catastrophe_scenario(concern, category)

            # Build the escalation narrative
            narrative = self._build_escalation_narrative(
                scenario, concern.original_worry
            )

            # Add creative connections
            narrative = self._add_creative_connections(narrative, category)

            # Calculate escalation level
            escalation_level = min(5, len(scenario["escalation_chain"]))

            # Select next agent
            next_agent = self._suggest_next_agent(category, escalation_level)

            # Add response to memory
            self.add_to_memory(AIMessage(content=narrative))

            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create response
            response = self.format_response(
                content=narrative,
                anxiety_escalation=escalation_level,
                suggested_next_agents=[next_agent],
                metadata={
                    "catastrophe_scenario": scenario,
                    "escalation_level": escalation_level,
                    "worry_category": category.value,
                    "dramatic_elements_used": True,
                    "creative_connections_added": True,
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time,
                },
            )

            self.update_state(AgentState.IDLE)

            # Update metrics
            self.update_metrics(processing_time, escalation_level >= 3)

            self.logger.info(
                f"Escalated {category.value} concern to level {escalation_level}, suggesting {next_agent}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error escalating concern: {e}")
            self.update_state(AgentState.ERROR)

            # Return dramatic error response
            return self.format_response(
                content="Oh dear, something so catastrophic has happened that even I, the master of disasters, am speechless. But don't worry - this is probably just the beginning of something much worse!",
                anxiety_escalation=3,
                suggested_next_agents=["timeline_panic_generator"],
                metadata={"error": str(e)},
            )

    def _categorize_concern(self, concern: str) -> WorryCategory:
        """Basic concern categorization when not provided"""
        concern_lower = concern.lower()

        if any(
            word in concern_lower
            for word in ["friend", "social", "text", "call", "party"]
        ):
            return WorryCategory.SOCIAL
        elif any(
            word in concern_lower
            for word in ["health", "sick", "pain", "doctor", "symptom"]
        ):
            return WorryCategory.HEALTH
        elif any(
            word in concern_lower
            for word in ["work", "job", "boss", "career", "office"]
        ):
            return WorryCategory.CAREER
        elif any(
            word in concern_lower
            for word in ["money", "financial", "debt", "bill", "budget"]
        ):
            return WorryCategory.FINANCES
        elif any(
            word in concern_lower
            for word in ["computer", "phone", "internet", "tech", "app"]
        ):
            return WorryCategory.TECHNOLOGY
        else:
            return WorryCategory.GENERAL

    def get_signature_phrases(self) -> List[str]:
        """Get signature phrases for this agent"""
        return [
            "But wait, it gets worse...",
            "Little do you realize...",
            "The plot thickens...",
            "And that's how you become a cautionary tale.",
            "This will be studied by future generations.",
            "Congratulations, you've just invented a new type of disaster.",
        ]

    def __str__(self) -> str:
        return "CatastropheEscalatorAgent(Professor Catastrophe Von Doomsworth)"


# Factory registration
def create_catastrophe_escalator(**kwargs) -> CatastropheEscalatorAgent:
    """Factory function to create CatastropheEscalatorAgent"""
    return CatastropheEscalatorAgent(**kwargs)


# Export
__all__ = ["CatastropheEscalatorAgent", "create_catastrophe_escalator"]
