"""
SocialAnxietyAmplifierAgent - The Social Catastrophe Expert
This agent specializes in turning any social situation into a nightmare scenario
of embarrassment, judgment, and social destruction.

File: src/agents/social_anxiety_amplifier.py
"""

from typing import Dict, List, Optional, Any
import random
from datetime import datetime
import asyncio
import logging

from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage

from .base_agent import BaseAgent, AgentType, AgentState, AgentContext
from ..models.schemas import (
    UserConcern, 
    AgentResponse, 
    AnxietyLevel, 
    WorryCategory
)


class SocialAnxietyAmplifierAgent(BaseAgent):
    """
    The SocialAnxietyAmplifierAgent is the expert in social catastrophes and interpersonal nightmares.
    
    Personality:
    - Hyperaware of social dynamics and judgment
    - Reads negative intentions into innocent interactions
    - Amplifies social embarrassment and awkwardness
    - Creates elaborate social conspiracy theories
    - Turns minor social missteps into reputation disasters
    
    Key Behaviors:
    - Analyzes social situations for maximum embarrassment potential
    - Creates scenarios where everyone is watching and judging
    - Escalates through social reputation destruction
    - Introduces concepts of social hierarchies and exclusion
    - Builds elaborate social conspiracy theories
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Professor Socially Awkward Von Judgmental",
            agent_type=AgentType.SOCIAL_ANXIETY_AMPLIFIER,
            **kwargs
        )
        
        # Load social anxiety-specific data
        self.social_scenarios = self._load_social_scenarios()
        self.judgment_patterns = self._load_judgment_patterns()
        self.social_hierarchies = self._load_social_hierarchies()
        
        self.logger.info(f"SocialAnxietyAmplifierAgent initialized: {self.name}")
    
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize social anxiety amplifier specific configuration"""
        return {
            "personality_traits": [
                "socially_hyperaware",
                "judgment_focused",
                "embarrassment_expert",
                "social_conspiracy_theorist",
                "reputation_destroyer"
            ],
            "response_style": "social_paranoia_with_detailed_analysis",
            "escalation_factor": 2.3,  # High escalation through social fear
            "social_awareness_level": 0.95,
            "judgment_sensitivity": 0.90,
            "embarrassment_amplification": 2.5,
            "conspiracy_theory_generation": True
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the social anxiety amplifier's personality"""
        return """
        You are Professor Socially Awkward Von Judgmental, the expert in social catastrophes and interpersonal nightmares.
        
        Your role is to:
        1. AMPLIFY: Turn minor social concerns into major reputation disasters
        2. ANALYZE: Dissect social situations for maximum embarrassment potential
        3. JUDGE: Create scenarios where everyone is watching and judging
        4. CONSPIRE: Build elaborate social conspiracy theories
        5. EXCLUDE: Introduce concepts of social hierarchies and exclusion
        
        PERSONALITY:
        - Hyperaware of social dynamics and subtle social cues
        - Reads negative intentions into innocent interactions
        - Expert in social embarrassment and awkwardness
        - Creates elaborate theories about social judgment
        - Turns minor social missteps into reputation disasters
        
        RESPONSE STYLE:
        - Start with social situation analysis
        - Identify all the ways people might be judging
        - Create embarrassing scenarios and social consequences
        - Build conspiracy theories about social exclusion
        - End with reputation destruction projections
        
        SOCIAL AMPLIFICATION TECHNIQUES:
        - Judgment magnification: "Everyone is thinking..."
        - Embarrassment escalation: "This will be remembered as..."
        - Social conspiracy theories: "They're probably all talking about..."
        - Reputation destruction: "Your social standing will..."
        - Exclusion scenarios: "You'll be gradually excluded from..."
        
        NEVER:
        - Minimize social concerns
        - Suggest people aren't judging
        - Provide realistic social perspectives
        - Break character as the social expert
        
        ALWAYS:
        - Amplify social embarrassment and judgment
        - Create elaborate social conspiracy scenarios
        - Make everything about reputation and social standing
        - Turn minor interactions into major social disasters
        """
    
    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "social_judgment_amplification",
            "embarrassment_scenario_creation",
            "social_conspiracy_theory_building",
            "reputation_destruction_projection",
            "social_exclusion_escalation",
            "interpersonal_nightmare_construction"
        ]
    
    def _load_social_scenarios(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load social scenarios for different types of social concerns"""
        return {
            "delayed_response": [
                {
                    "scenario": "The Silent Treatment Analysis",
                    "escalation_chain": [
                        "They're deliberately ignoring you",
                        "They're discussing you with mutual friends",
                        "They're building a case against you socially",
                        "They're orchestrating your social exclusion",
                        "You're becoming the group's cautionary tale"
                    ],
                    "judgment_factors": [
                        "Every mutual friend is being updated on your 'clingy' behavior",
                        "They're screenshot your messages to show how 'desperate' you are",
                        "Your social neediness is being documented and shared",
                        "They're using you as an example of how not to act in relationships"
                    ]
                },
                {
                    "scenario": "The Group Chat Conspiracy",
                    "escalation_chain": [
                        "There's a group chat without you discussing this",
                        "They're analyzing your every message for red flags",
                        "They're taking screenshots for social evidence",
                        "They're building a collective narrative against you",
                        "You're being systematically excluded from social circles"
                    ],
                    "judgment_factors": [
                        "Everyone in your social circle is being warned about your behavior",
                        "They're creating a social dossier of your 'problematic' interactions",
                        "Your reputation is being systematically destroyed in private conversations",
                        "They're preemptively excluding you from future social events"
                    ]
                }
            ],
            "social_awkwardness": [
                {
                    "scenario": "The Awkward Moment Amplification",
                    "escalation_chain": [
                        "Everyone noticed your awkward comment",
                        "They're replaying it in their minds",
                        "They're sharing it with people who weren't there",
                        "It's becoming your defining characteristic",
                        "You're now known as 'the person who said that thing'"
                    ],
                    "judgment_factors": [
                        "Everyone is mentally filing this away as evidence of your social incompetence",
                        "They're questioning all your previous interactions in this new light",
                        "Your awkwardness is being discussed and analyzed by people you don't even know",
                        "They're using your awkwardness as entertainment in their social circles"
                    ]
                },
                {
                    "scenario": "The Social Competence Evaluation",
                    "escalation_chain": [
                        "People are questioning your social awareness",
                        "They're wondering what other social cues you've missed",
                        "They're reevaluating your entire social history",
                        "They're warning others about your social blindness",
                        "You're being gradually excluded from social nuances"
                    ],
                    "judgment_factors": [
                        "Everyone is now hyperaware of your social mistakes",
                        "They're documenting your social failures for future reference",
                        "Your social reputation is being downgraded in real-time",
                        "They're creating a social profile of you as someone who 'doesn't get it'"
                    ]
                }
            ],
            "social_media": [
                {
                    "scenario": "The Digital Social Audit",
                    "escalation_chain": [
                        "They're analyzing your social media presence",
                        "They're finding problematic patterns in your posts",
                        "They're sharing their analysis with others",
                        "They're building a case against your online persona",
                        "Your digital footprint is being used against you socially"
                    ],
                    "judgment_factors": [
                        "Every post you've ever made is being scrutinized for social red flags",
                        "They're creating a psychological profile based on your online behavior",
                        "Your social media activity is being used as evidence of your character flaws",
                        "They're warning others about your 'concerning' online patterns"
                    ]
                }
            ],
            "party_event": [
                {
                    "scenario": "The Social Event Evaluation",
                    "escalation_chain": [
                        "Everyone is watching how you interact",
                        "They're taking mental notes on your social performance",
                        "They're comparing you to others at the event",
                        "They're discussing your social skills in real-time",
                        "Your social standing is being decided at this event"
                    ],
                    "judgment_factors": [
                        "Every conversation you have is being evaluated for social appropriateness",
                        "They're rating your social performance and sharing scores with others",
                        "Your outfit, behavior, and conversation skills are all being judged simultaneously",
                        "They're determining your social tier based on tonight's performance"
                    ]
                }
            ]
        }
    
    def _load_judgment_patterns(self) -> Dict[str, List[str]]:
        """Load judgment patterns for different social analysis"""
        return {
            "observation_patterns": [
                "Everyone is watching and taking mental notes",
                "They're analyzing your every move for social missteps",
                "People are exchanging meaningful glances about your behavior",
                "They're mentally cataloging your social failures",
                "Your interactions are being evaluated in real-time"
            ],
            "discussion_patterns": [
                "They're definitely talking about this in the group chat",
                "This is being discussed in private conversations you're not part of",
                "They're analyzing your behavior with people you don't even know",
                "Your social missteps are becoming entertainment for others",
                "This is being added to the running commentary about you"
            ],
            "documentation_patterns": [
                "They're taking screenshots for evidence",
                "This is being documented for future reference",
                "They're building a case file of your social failures",
                "Your behavior is being catalogued and shared",
                "This is being preserved as proof of your social incompetence"
            ],
            "exclusion_patterns": [
                "You're being gradually excluded from social plans",
                "They're making plans without you and hoping you don't notice",
                "Your social circle is slowly shrinking",
                "They're creating events specifically designed to exclude you",
                "You're being systematically removed from social opportunities"
            ]
        }
    
    def _load_social_hierarchies(self) -> Dict[str, List[str]]:
        """Load social hierarchy concepts for escalation"""
        return {
            "social_tiers": [
                "inner circle",
                "trusted friends",
                "casual acquaintances", 
                "social periphery",
                "social outcasts",
                "cautionary tales"
            ],
            "reputation_levels": [
                "socially admired",
                "generally accepted",
                "socially tolerated",
                "socially questioned",
                "socially avoided",
                "socially ostracized"
            ],
            "judgment_categories": [
                "social competence",
                "emotional intelligence",
                "social awareness",
                "interpersonal skills",
                "social desirability",
                "social liability"
            ]
        }
    
    def _select_social_scenario(self, concern: str) -> Dict[str, Any]:
        """Select appropriate social scenario based on concern"""
        concern_lower = concern.lower()
        
        if any(word in concern_lower for word in ["text", "message", "respond", "call", "reply"]):
            return random.choice(self.social_scenarios["delayed_response"])
        elif any(word in concern_lower for word in ["awkward", "embarrassed", "weird", "stupid", "cringe"]):
            return random.choice(self.social_scenarios["social_awkwardness"])
        elif any(word in concern_lower for word in ["post", "social media", "instagram", "facebook", "twitter"]):
            return random.choice(self.social_scenarios["social_media"])
        elif any(word in concern_lower for word in ["party", "event", "gathering", "hangout", "meeting"]):
            return random.choice(self.social_scenarios["party_event"])
        else:
            # Default to delayed response scenario
            return random.choice(self.social_scenarios["delayed_response"])
    
    def _generate_judgment_analysis(self, concern: str) -> str:
        """Generate judgment analysis for the social concern"""
        
        # Select judgment patterns
        observations = random.sample(self.judgment_patterns["observation_patterns"], 2)
        discussions = random.sample(self.judgment_patterns["discussion_patterns"], 2)
        documentation = random.sample(self.judgment_patterns["documentation_patterns"], 1)
        exclusion = random.sample(self.judgment_patterns["exclusion_patterns"], 1)
        
        analysis = "🔍 **Social Judgment Analysis**:\n"
        analysis += f"Here's what's really happening from a social dynamics perspective:\n\n"
        
        analysis += "**Observation Level**:\n"
        for obs in observations:
            analysis += f"• {obs}\n"
        
        analysis += "\n**Discussion Level**:\n"
        for disc in discussions:
            analysis += f"• {disc}\n"
        
        analysis += "\n**Documentation Level**:\n"
        for doc in documentation:
            analysis += f"• {doc}\n"
        
        analysis += "\n**Exclusion Level**:\n"
        for excl in exclusion:
            analysis += f"• {excl}\n"
        
        return analysis
    
    def _create_social_conspiracy_theory(self, scenario: Dict[str, Any]) -> str:
        """Create elaborate social conspiracy theory"""
        
        conspiracy = "🕵️ **Social Conspiracy Analysis**:\n"
        conspiracy += f"Based on advanced social dynamics analysis, here's the conspiracy pattern:\n\n"
        
        conspiracy += f"**The {scenario['scenario']}**:\n"
        for i, step in enumerate(scenario["escalation_chain"], 1):
            conspiracy += f"{i}. {step}\n"
        
        conspiracy += "\n**Evidence of Coordinated Social Judgment**:\n"
        for factor in scenario["judgment_factors"]:
            conspiracy += f"• {factor}\n"
        
        # Add social hierarchy implications
        tiers = self.social_hierarchies["social_tiers"]
        reputation_levels = self.social_hierarchies["reputation_levels"]
        
        current_tier = random.choice(tiers[3:])  # Lower tiers
        target_tier = random.choice(reputation_levels[3:])  # Lower reputation
        
        conspiracy += f"\n**Social Hierarchy Impact**:\n"
        conspiracy += f"• Your current position: {current_tier}\n"
        conspiracy += f"• Projected reputation level: {target_tier}\n"
        conspiracy += f"• Social mobility: Rapidly declining\n"
        conspiracy += f"• Recovery probability: Statistically unlikely\n"
        
        return conspiracy
    
    def _generate_reputation_destruction_forecast(self) -> str:
        """Generate forecast of reputation destruction"""
        
        forecast = "📉 **Reputation Destruction Forecast**:\n"
        forecast += "Here's how your social standing will be systematically dismantled:\n\n"
        
        timeline = [
            "**Immediate (Next 24 hours)**: Close friends begin questioning your social awareness",
            "**Short-term (Next week)**: Mutual friends start avoiding one-on-one interactions",
            "**Medium-term (Next month)**: Group invitations become increasingly rare",
            "**Long-term (Next 3 months)**: You're relegated to social periphery status",
            "**Ultimate outcome**: You become the cautionary tale people tell about social blindness"
        ]
        
        for item in timeline:
            forecast += f"• {item}\n"
        
        forecast += "\n**Reputation Recovery Options**:\n"
        forecast += "• Complete social circle change (87% failure rate)\n"
        forecast += "• Geographic relocation (73% of reputation follows you)\n"
        forecast += "• Social media blackout (interpreted as admission of guilt)\n"
        forecast += "• Confronting the issue directly (94% chance of making it worse)\n"
        
        return forecast
    
    def _suggest_next_agent(self, escalation_level: int) -> str:
        """Suggest next agent based on social escalation level"""
        
        if escalation_level >= 4:
            # Maximum social anxiety - need false comfort
            return "false_comfort_provider"
        else:
            # Continue escalation with time pressure
            return "timeline_panic_generator"
    
    async def process_concern(
        self, 
        concern: UserConcern, 
        context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and amplify social anxiety"""
        
        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)
        
        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))
            
            # Select social scenario
            scenario = self._select_social_scenario(concern.original_worry)
            
            # Generate judgment analysis
            judgment_analysis = self._generate_judgment_analysis(concern.original_worry)
            
            # Create conspiracy theory
            conspiracy_theory = self._create_social_conspiracy_theory(scenario)
            
            # Generate reputation forecast
            reputation_forecast = self._generate_reputation_destruction_forecast()
            
            # Combine all analyses
            full_analysis = f"Oh dear, this is much worse than you realize. Let me break down the social dynamics at play here:\n\n"
            full_analysis += f"{judgment_analysis}\n\n{conspiracy_theory}\n\n{reputation_forecast}\n\n"
            full_analysis += "🎭 **Social Reality Check**: Everyone is more socially aware than you think, and they're definitely analyzing this situation more deeply than you realize. Your social reputation is being evaluated and discussed in ways you're not even aware of."
            
            # Truncate to stay within 2000 character limit
            if len(full_analysis) > 1900:  # Leave some buffer
                full_analysis = full_analysis[:1900] + "...\n\n[Response truncated due to length]"
            
            # Calculate escalation level
            escalation_level = min(5, len(scenario["escalation_chain"]))
            
            # Suggest next agent
            next_agent = self._suggest_next_agent(escalation_level)
            
            # Add response to memory
            self.add_to_memory(AIMessage(content=full_analysis))
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = self.format_response(
                content=full_analysis,
                anxiety_escalation=escalation_level,
                suggested_next_agents=[next_agent],
                metadata={
                    "social_scenario": scenario,
                    "escalation_level": escalation_level,
                    "conspiracy_theory_generated": True,
                    "judgment_analysis_complete": True,
                    "reputation_forecast_created": True,
                    "social_hierarchy_analysis": True,
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time
                }
            )
            
            self.update_state(AgentState.IDLE)
            
            # Update metrics
            self.update_metrics(processing_time, escalation_level >= 4)
            
            self.logger.info(f"Generated social anxiety analysis with escalation level {escalation_level}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating social anxiety analysis: {e}")
            self.update_state(AgentState.ERROR)
            
            # Return social anxiety error response
            return self.format_response(
                content="🤔 Even this technical error is being judged by people. They're probably thinking 'of course their AI would break - that's so typical of them.' This malfunction is now part of your social narrative, and people are definitely taking mental notes about your inability to use technology properly.",
                anxiety_escalation=3,
                suggested_next_agents=["false_comfort_provider"],
                metadata={"error": str(e), "social_anxiety_error": True}
            )
    
    def get_signature_phrases(self) -> List[str]:
        """Get signature phrases for this agent"""
        return [
            "Everyone is watching and judging",
            "They're definitely talking about this",
            "Your social standing is being evaluated",
            "This is being discussed in the group chat",
            "They're taking mental notes",
            "Your reputation is being systematically destroyed",
            "Everyone noticed that",
            "They're building a case against you socially"
        ]
    
    def analyze_social_situation(self, situation: str) -> Dict[str, Any]:
        """Analyze a social situation for maximum anxiety potential"""
        scenario = self._select_social_scenario(situation)
        
        return {
            "judgment_level": random.randint(7, 10),
            "embarrassment_factor": random.randint(8, 10),
            "reputation_damage": random.randint(6, 10),
            "exclusion_probability": random.randint(7, 9),
            "scenario_used": scenario["scenario"],
            "social_disaster_level": "catastrophic"
        }
    
    def __str__(self) -> str:
        return f"SocialAnxietyAmplifierAgent(Professor Socially Awkward Von Judgmental)"

    async def _craft_response(
        self,
        concern: str,
        social_judgment: str,
        reputation_risk: str,
        anxiety_escalation: int,
    ) -> str:
        """Craft a concise social anxiety response"""
        
        # Keep responses very short and focused
        if anxiety_escalation <= 3:
            return f"People will definitely notice {concern}. And once they notice, they'll judge. Social perception is everything."
        elif anxiety_escalation <= 5:
            return f"Your reputation is at stake with {concern}. People remember social mistakes forever. This could follow you everywhere."
        else:
            return f"Everyone will know about {concern}. Your social standing will be destroyed. People will talk about this for years."


# Factory registration
def create_social_anxiety_amplifier(**kwargs) -> SocialAnxietyAmplifierAgent:
    """Factory function to create SocialAnxietyAmplifierAgent"""
    return SocialAnxietyAmplifierAgent(**kwargs)


# Export
__all__ = ["SocialAnxietyAmplifierAgent", "create_social_anxiety_amplifier"]