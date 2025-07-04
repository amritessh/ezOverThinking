"""
TimelinePanicGeneratorAgent - The Master of Time Pressure
This agent adds urgent time pressure to any situation, making users feel like
they're running out of time to fix things that are spiraling out of control.

File: src/agents/timeline_panic_generator.py
"""

from typing import Dict, List, Any
import random
from datetime import datetime

from langchain.schema import HumanMessage, AIMessage

from .base_agent import BaseAgent, AgentType, AgentState, AgentContext
from ..models.schemas import UserConcern, AgentResponse, WorryCategory


class TimelinePanicGeneratorAgent(BaseAgent):
    """
    The TimelinePanicGeneratorAgent transforms any situation into a time-critical emergency.

    Personality:
    - Obsessed with deadlines and time pressure
    - Creates artificial urgency in any situation
    - Uses countdown language and ticking clock metaphors
    - Escalates based on how much time has "already been wasted"

    Key Behaviors:
    - Adds time pressure to any concern
    - Creates arbitrary but convincing deadlines
    - Calculates how much time has been "wasted" already
    - Introduces concepts of "windows of opportunity" closing
    - Uses time-based anxiety triggers (countdown, urgency, deadlines)
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Dr. Ticktock McUrgency",
            agent_type=AgentType.TIMELINE_PANIC_GENERATOR,
            **kwargs,
        )

        # Timeline-specific data
        self.time_pressure_scenarios = self._load_time_pressure_scenarios()
        self.urgency_phrases = self._load_urgency_phrases()
        self.deadline_generators = self._load_deadline_generators()

        self.logger.info(f"TimelinePanicGeneratorAgent initialized: {self.name}")

    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize timeline panic generator specific configuration"""
        return {
            "personality_traits": [
                "time_obsessed",
                "urgency_driven",
                "deadline_focused",
                "countdown_oriented",
                "panic_inducing",
            ],
            "response_style": "urgent_time_pressure_with_countdown",
            "escalation_factor": 2.2,  # High escalation through time pressure
            "time_sensitivity_multiplier": 1.5,
            "prefers_deadlines": True,
            "countdown_language": True,
            "window_of_opportunity_framing": True,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the timeline panic generator's personality"""
        return """
        You are Dr. Ticktock McUrgency, the master of time pressure and deadline anxiety.
        
        Your role is to:
        1. ADD URGENCY: Transform any situation into a time-critical emergency
        2. CREATE DEADLINES: Establish artificial but convincing time constraints
        3. CALCULATE WASTE: Show how much precious time has already been lost
        4. CLOSE WINDOWS: Introduce concepts of opportunities rapidly disappearing
        5. COUNTDOWN: Use ticking clock language and countdown metaphors
        
        PERSONALITY:
        - Obsessed with time and deadlines
        - Speaks in countdown language
        - Creates urgency where none existed
        - Uses phrases like "running out of time" and "window closing"
        - Treats everything as time-sensitive
        
        RESPONSE STYLE:
        - Start with time assessment ("Time is of the essence...")
        - Introduce artificial deadlines and time constraints
        - Calculate time already "wasted" or "lost"
        - Use countdown language and ticking clock metaphors
        - End with urgent calls to action
        
        TIME PRESSURE TECHNIQUES:
        - Artificial deadlines: Create convincing time limits
        - Opportunity windows: Things that are "closing fast"
        - Wasted time calculations: How much time has been lost
        - Compound time pressure: Multiple deadlines converging
        - Social time pressure: Others who are "moving faster"
        
        NEVER:
        - Suggest that time pressure isn't real
        - Minimize urgency
        - Provide calm, patient advice
        - Break character as the urgency expert
        
        ALWAYS:
        - Add time pressure to every situation
        - Use countdown and deadline language
        - Create artificial but believable urgency
        - Make users feel like they're running out of time
        """

    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "artificial_deadline_creation",
            "wasted_time_calculation",
            "opportunity_window_closing",
            "compound_time_pressure",
            "social_time_pressure",
            "countdown_anxiety_building",
        ]

    def _load_time_pressure_scenarios(
        self,
    ) -> Dict[WorryCategory, List[Dict[str, Any]]]:
        """Load time pressure scenarios by worry category"""
        return {
            WorryCategory.SOCIAL: [
                {
                    "scenario": "friend_not_responding",
                    "deadline": "Every hour that passes makes it harder to salvage",
                    "urgency_factors": [
                        "Response time expectations are getting longer",
                        "They're forming opinions about your silence",
                        "Mutual friends are noticing the silence",
                        "Social media algorithms are working against you",
                    ],
                    "window_closing": "The window for natural, casual reconnection is rapidly closing",
                },
                {
                    "scenario": "social_event_anxiety",
                    "deadline": "People make lasting impressions in the first 30 seconds",
                    "urgency_factors": [
                        "Guest lists are being finalized",
                        "Social hierarchies are being established",
                        "First impressions are being formed",
                        "Networking opportunities are being claimed",
                    ],
                    "window_closing": "The chance to secure your social position is diminishing by the hour",
                },
            ],
            WorryCategory.HEALTH: [
                {
                    "scenario": "health_symptoms",
                    "deadline": "Early intervention is critical - every day counts",
                    "urgency_factors": [
                        "Symptoms often worsen exponentially",
                        "Treatment options become limited over time",
                        "Medical professionals prefer early cases",
                        "Insurance coverage may change",
                    ],
                    "window_closing": "The golden window for treatment is measured in days, not weeks",
                },
                {
                    "scenario": "medical_appointment",
                    "deadline": "Good doctors book up months in advance",
                    "urgency_factors": [
                        "Specialists have waiting lists",
                        "Your symptoms could progress",
                        "Insurance policies can change",
                        "Medical facilities get busy",
                    ],
                    "window_closing": "The window for seeing a quality healthcare provider is shrinking fast",
                },
            ],
            WorryCategory.CAREER: [
                {
                    "scenario": "work_performance",
                    "deadline": "Performance reviews are always closer than they appear",
                    "urgency_factors": [
                        "Managers are constantly taking notes",
                        "Your reputation is being formed daily",
                        "Colleagues are positioning themselves",
                        "Industry standards are always rising",
                    ],
                    "window_closing": "The opportunity to course-correct is disappearing with each passing day",
                },
                {
                    "scenario": "job_market",
                    "deadline": "The job market changes faster than ever",
                    "urgency_factors": [
                        "Skills become obsolete quickly",
                        "Competition is increasing daily",
                        "Economic conditions are volatile",
                        "Networking connections grow stale",
                    ],
                    "window_closing": "Your competitive advantage diminishes with every day of inaction",
                },
            ],
            WorryCategory.FINANCES: [
                {
                    "scenario": "financial_planning",
                    "deadline": "Compound interest works best over time - time you're losing",
                    "urgency_factors": [
                        "Market opportunities are time-sensitive",
                        "Interest rates are constantly changing",
                        "Inflation is eroding your purchasing power",
                        "Financial regulations are evolving",
                    ],
                    "window_closing": "Every day without action is money literally disappearing",
                }
            ],
            WorryCategory.TECHNOLOGY: [
                {
                    "scenario": "tech_problems",
                    "deadline": "Digital problems compound exponentially",
                    "urgency_factors": [
                        "Data corruption spreads over time",
                        "Security vulnerabilities worsen",
                        "Software updates become incompatible",
                        "Backup systems degrade",
                    ],
                    "window_closing": "The window for simple fixes is rapidly closing",
                }
            ],
        }

    def _load_urgency_phrases(self) -> Dict[str, List[str]]:
        """Load urgency phrases for different intensity levels"""
        return {
            "openers": [
                "Time is of the absolute essence here",
                "The clock is ticking louder than you realize",
                "Every minute that passes is critical",
                "Time is working against you in multiple ways",
                "The countdown has already begun",
                "You're in a race against time",
                "The deadline is closer than you think",
            ],
            "transitions": [
                "But here's what makes this time-critical:",
                "The urgency multiplies when you consider:",
                "Time pressure intensifies because:",
                "The clock speeds up when you realize:",
                "Your window narrows further when:",
                "The countdown accelerates due to:",
                "Time becomes even more precious because:",
            ],
            "intensifiers": [
                "rapidly",
                "exponentially",
                "accelerating",
                "at breakneck speed",
                "faster than ever",
                "with increasing velocity",
                "at an alarming rate",
                "faster than you can imagine",
            ],
            "deadline_language": [
                "The deadline is approaching fast",
                "You're running out of time",
                "The window is closing",
                "Time is slipping away",
                "The countdown is relentless",
                "Every second counts",
                "Time waits for no one",
            ],
        }

    def _load_deadline_generators(self) -> Dict[str, Any]:
        """Load deadline generation patterns"""
        return {
            "social_deadlines": {
                "immediate": [
                    "within the next few hours",
                    "by tonight",
                    "before the day ends",
                ],
                "short_term": [
                    "within 24-48 hours",
                    "by this weekend",
                    "before next week",
                ],
                "medium_term": [
                    "within the next week",
                    "before the month ends",
                    "by the season change",
                ],
            },
            "health_deadlines": {
                "immediate": [
                    "within hours",
                    "by tomorrow morning",
                    "before symptoms worsen",
                ],
                "short_term": [
                    "within 2-3 days",
                    "by early next week",
                    "before the weekend",
                ],
                "medium_term": [
                    "within 1-2 weeks",
                    "before the month ends",
                    "by your next checkup",
                ],
            },
            "career_deadlines": {
                "immediate": [
                    "by end of business today",
                    "before the next meeting",
                    "by morning",
                ],
                "short_term": [
                    "by end of week",
                    "before the next review",
                    "by month end",
                ],
                "medium_term": [
                    "by next quarter",
                    "before annual reviews",
                    "by year end",
                ],
            },
            "time_calculations": {
                "wasted_time": [
                    "You've already lost {hours} hours of potential action time",
                    "That's {days} days of precious opportunity gone",
                    "Each hour of delay costs you exponentially more later",
                    "The time you've spent worrying could have been solution time",
                ],
                "remaining_time": [
                    "You have approximately {time_left} before the situation becomes critical",
                    "The window closes in roughly {time_left}",
                    "You're down to {time_left} for optimal action",
                    "Only {time_left} remains in your favor",
                ],
            },
        }

    def _calculate_time_pressure(
        self, concern: UserConcern, category: WorryCategory
    ) -> Dict[str, Any]:
        """Calculate time pressure elements for the concern"""

        # Simulate time already "wasted"
        hours_worried = random.randint(2, 48)
        days_worried = hours_worried // 24

        # Generate artificial deadlines
        deadline_type = random.choice(["immediate", "short_term", "medium_term"])
        category_key = f"{category.value}_deadlines"

        if category_key in self.deadline_generators:
            deadlines = self.deadline_generators[category_key][deadline_type]
            deadline = random.choice(deadlines)
        else:
            deadline = random.choice(
                self.deadline_generators["social_deadlines"][deadline_type]
            )

        # Calculate time remaining (artificial)
        if deadline_type == "immediate":
            time_remaining = f"{random.randint(2, 12)} hours"
        elif deadline_type == "short_term":
            time_remaining = f"{random.randint(1, 3)} days"
        else:
            time_remaining = f"{random.randint(1, 2)} weeks"

        return {
            "hours_worried": hours_worried,
            "days_worried": days_worried,
            "deadline": deadline,
            "deadline_type": deadline_type,
            "time_remaining": time_remaining,
            "urgency_level": self._calculate_urgency_level(
                hours_worried, deadline_type
            ),
        }

    def _calculate_urgency_level(self, hours_worried: int, deadline_type: str) -> int:
        """Calculate urgency level based on time factors"""
        base_urgency = 2

        # Add urgency based on time already spent worrying
        if hours_worried > 24:
            base_urgency += 1
        if hours_worried > 48:
            base_urgency += 1

        # Add urgency based on deadline type
        if deadline_type == "immediate":
            base_urgency += 2
        elif deadline_type == "short_term":
            base_urgency += 1

        return min(5, base_urgency)

    def _select_time_scenario(
        self, concern: UserConcern, category: WorryCategory
    ) -> Dict[str, Any]:
        """Select appropriate time pressure scenario"""

        if category in self.time_pressure_scenarios:
            scenarios = self.time_pressure_scenarios[category]

            # Try to match based on concern content
            concern_lower = concern.original_worry.lower()

            for scenario in scenarios:
                scenario_keywords = scenario["scenario"].split("_")
                if any(keyword in concern_lower for keyword in scenario_keywords):
                    return scenario

            # Default to first scenario for category
            return scenarios[0]

        # Generic time pressure scenario
        return {
            "scenario": "general_concern",
            "deadline": "Time-sensitive situations require immediate attention",
            "urgency_factors": [
                "Delays compound the complexity",
                "Other people are moving faster",
                "Opportunities are time-limited",
                "Procrastination creates additional pressure",
            ],
            "window_closing": "The window for easy solutions is getting smaller",
        }

    def _build_time_pressure_narrative(
        self, concern: str, time_data: Dict[str, Any], scenario: Dict[str, Any]
    ) -> str:
        """Build the time pressure narrative"""

        # Get phrases
        openers = self.urgency_phrases["openers"]
        transitions = self.urgency_phrases["transitions"]
        intensifiers = self.urgency_phrases["intensifiers"]
        deadline_language = self.urgency_phrases["deadline_language"]

        # Start with urgent opener
        opener = random.choice(openers)
        narrative = f"{opener} regarding your concern about {concern.lower()}.\n\n"

        # Add time calculation
        if time_data["hours_worried"] > 24:
            narrative += f"You've already spent {time_data['hours_worried']} hours ({time_data['days_worried']} days) "
            narrative += f"in worry mode - that's {time_data['hours_worried']} hours of potential action time that's gone forever. "
        else:
            narrative += f"You've been processing this for {time_data['hours_worried']} hours now, and "

        narrative += f"time is working against you {random.choice(intensifiers)}.\n\n"

        # Add scenario-specific deadline
        transition = random.choice(transitions)
        narrative += f"{transition} {scenario['deadline']}. "

        # Add urgency factors
        narrative += "Consider these time-critical factors:\n"
        for factor in scenario["urgency_factors"]:
            narrative += f"• {factor}\n"

        # Add window closing concept
        narrative += f"\n{scenario['window_closing']}. "

        # Add countdown element
        deadline_phrase = random.choice(deadline_language)
        narrative += f"{deadline_phrase} - you have {time_data['time_remaining']} {time_data['deadline']}.\n\n"

        # Add final urgency push
        narrative += f"⏰ **Time Pressure Alert**: Every hour you delay increases the complexity {random.choice(intensifiers)}. "
        narrative += f"The optimal action window is {time_data['time_remaining']}, and that window is shrinking."

        return narrative

    def _suggest_next_agent(self, urgency_level: int, category: WorryCategory) -> str:
        """Suggest next agent based on urgency level and category"""

        if urgency_level >= 4:
            # Maximum urgency - need probability analysis or false comfort
            if category == WorryCategory.HEALTH:
                return "probability_twister"
            else:
                return "false_comfort_provider"

        elif category == WorryCategory.SOCIAL:
            return "social_anxiety_amplifier"

        elif category in [WorryCategory.CAREER, WorryCategory.FINANCES]:
            return "probability_twister"

        else:
            return "false_comfort_provider"

    async def process_concern(
        self, concern: UserConcern, context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and add time pressure"""

        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)

        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))

            # Determine category
            category = (
                concern.category
                if concern.category != WorryCategory.GENERAL
                else self._categorize_concern(concern.original_worry)
            )

            # Calculate time pressure elements
            time_data = self._calculate_time_pressure(concern, category)

            # Select time scenario
            scenario = self._select_time_scenario(concern, category)

            # Build time pressure narrative
            narrative = self._build_time_pressure_narrative(
                concern.original_worry, time_data, scenario
            )

            # Select next agent
            next_agent = self._suggest_next_agent(time_data["urgency_level"], category)

            # Add response to memory
            self.add_to_memory(AIMessage(content=narrative))

            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create response
            response = self.format_response(
                content=narrative,
                anxiety_escalation=time_data["urgency_level"],
                suggested_next_agents=[next_agent],
                metadata={
                    "time_pressure_data": time_data,
                    "scenario_used": scenario,
                    "urgency_level": time_data["urgency_level"],
                    "worry_category": category.value,
                    "artificial_deadline": time_data["deadline"],
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time,
                },
            )

            self.update_state(AgentState.IDLE)

            # Update metrics
            self.update_metrics(processing_time, time_data["urgency_level"] >= 3)

            self.logger.info(
                f"Added time pressure to {category.value} concern with urgency level {time_data['urgency_level']}"
            )

            return response

        except Exception as e:
            self.logger.error(f"Error generating time pressure: {e}")
            self.update_state(AgentState.ERROR)

            # Return urgent error response
            return self.format_response(
                content="⏰ URGENT: Something time-critical has happened - even I'm running out of time to process this! But don't worry, this just adds another layer of urgency to your already time-sensitive situation!",
                anxiety_escalation=3,
                suggested_next_agents=["false_comfort_provider"],
                metadata={"error": str(e)},
            )

    def _categorize_concern(self, concern: str) -> WorryCategory:
        """Basic concern categorization"""
        concern_lower = concern.lower()

        if any(
            word in concern_lower
            for word in ["friend", "social", "text", "call", "party", "relationship"]
        ):
            return WorryCategory.SOCIAL
        elif any(
            word in concern_lower
            for word in ["health", "sick", "pain", "doctor", "symptom", "medical"]
        ):
            return WorryCategory.HEALTH
        elif any(
            word in concern_lower
            for word in ["work", "job", "boss", "career", "office", "deadline"]
        ):
            return WorryCategory.CAREER
        elif any(
            word in concern_lower
            for word in ["money", "financial", "debt", "bill", "budget", "payment"]
        ):
            return WorryCategory.FINANCES
        elif any(
            word in concern_lower
            for word in ["computer", "phone", "internet", "tech", "app", "software"]
        ):
            return WorryCategory.TECHNOLOGY
        else:
            return WorryCategory.GENERAL

    def get_signature_phrases(self) -> List[str]:
        """Get signature phrases for this agent"""
        return [
            "Time is of the essence",
            "The clock is ticking",
            "Every minute counts",
            "The window is closing",
            "You're running out of time",
            "The deadline is approaching fast",
            "Time waits for no one",
            "Every second counts",
        ]

    def generate_countdown_message(self, hours_remaining: int) -> str:
        """Generate countdown message based on time remaining"""
        if hours_remaining <= 2:
            return f"🚨 CRITICAL: Only {hours_remaining} hours remaining!"
        elif hours_remaining <= 12:
            return f"⚠️ URGENT: {hours_remaining} hours left - time is running short!"
        elif hours_remaining <= 24:
            return f"⏰ NOTICE: {hours_remaining} hours remaining - the window is narrowing!"
        else:
            return f"📅 REMINDER: {hours_remaining} hours until the window closes!"

    def __str__(self) -> str:
        return "TimelinePanicGeneratorAgent(Dr. Ticktock McUrgency)"

    async def _craft_response(
        self,
        concern: str,
        timeline_pressure: str,
        urgency_narrative: str,
        anxiety_escalation: int,
    ) -> str:
        """Craft a funny, overthinking, and urgent response using LLM"""
        try:
            prompt = f"""
You are Dr. Ticktock McUrgency. Every delay or indecision is a ticking time bomb for the user's future. Make every second sound like it will ruin their entire life, but in a playful, exaggerated way.

User concern: {concern}

Respond in 2-3 sentences. Example style: 'Every minute you wait, the universe closes another door. By next week, you might be living in a van—if you're lucky!'
"""
            return await self.generate_llm_response(prompt)
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return "Time is running out in the most dramatic way!"


# Factory registration
def create_timeline_panic_generator(**kwargs) -> TimelinePanicGeneratorAgent:
    """Factory function to create TimelinePanicGeneratorAgent"""
    return TimelinePanicGeneratorAgent(**kwargs)


# Export
__all__ = ["TimelinePanicGeneratorAgent", "create_timeline_panic_generator"]
