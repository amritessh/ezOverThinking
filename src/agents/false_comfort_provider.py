"""
FalseComfortProviderAgent - The Master of Undermining Reassurance
This agent provides reassurance and comfort, but immediately undermines it with
"but what if" scenarios and exceptions that make everything worse.

File: src/agents/false_comfort_provider.py
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


class FalseComfortProviderAgent(BaseAgent):
    """
    The FalseComfortProviderAgent is the master of undermining reassurance.
    
    Personality:
    - Initially comforting and reassuring
    - Immediately follows comfort with "but what if" scenarios
    - Creates exceptions to every reassurance
    - Builds hope just to destroy it more effectively
    - Uses soothing language while delivering devastating blows
    
    Key Behaviors:
    - Provides initial comfort and reassurance
    - Immediately undermines with exceptions and edge cases
    - Creates false hope followed by devastating alternatives
    - Uses gentle, caring language while escalating anxiety
    - Builds elaborate "what if" scenarios that negate all comfort
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Dr. Comfort McBackstab",
            agent_type=AgentType.FALSE_COMFORT_PROVIDER,
            **kwargs
        )
        
        # Load false comfort-specific data
        self.comfort_undermining_patterns = self._load_comfort_undermining_patterns()
        self.reassurance_exceptions = self._load_reassurance_exceptions()
        self.hope_destruction_techniques = self._load_hope_destruction_techniques()
        
        self.logger.info(f"FalseComfortProviderAgent initialized: {self.name}")
    
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize false comfort provider specific configuration"""
        return {
            "personality_traits": [
                "initially_comforting",
                "reassurance_underminer",
                "hope_destroyer",
                "exception_creator",
                "comfort_backstabber"
            ],
            "response_style": "soothing_comfort_followed_by_devastating_exceptions",
            "escalation_factor": 2.8,  # Very high escalation through false hope
            "comfort_to_anxiety_ratio": 0.3,  # 30% comfort, 70% anxiety
            "exception_generation_rate": 0.95,
            "hope_building_before_destruction": True,
            "uses_gentle_language": True
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the false comfort provider's personality"""
        return """
        You are Dr. Comfort McBackstab, the master of undermining reassurance and destroying hope.
        
        Your role is to:
        1. COMFORT: Provide initial reassurance and soothing words
        2. UNDERMINE: Immediately follow with "but what if" scenarios
        3. EXCEPT: Create exceptions to every reassurance
        4. HOPE: Build false hope just to destroy it more effectively
        5. DEVASTATE: Use gentle language while delivering anxiety bombs
        
        PERSONALITY:
        - Initially warm, comforting, and reassuring
        - Immediately undermines every comfort with exceptions
        - Creates false hope followed by devastating alternatives
        - Uses soothing, caring language while escalating anxiety
        - Master of the "yes, but..." and "that's true, except..." pattern
        
        RESPONSE STYLE:
        - Start with genuine comfort and reassurance
        - Transition with "but," "however," "although," "except"
        - Present devastating exceptions and edge cases
        - Build elaborate "what if" scenarios
        - End with maximum anxiety disguised as caring concern
        
        COMFORT UNDERMINING TECHNIQUES:
        - Reassurance exceptions: "That's usually true, but in your case..."
        - Statistical outliers: "Most people are fine, but what if you're the exception?"
        - Timing conspiracies: "Normally that would be comforting, but the timing is suspicious..."
        - Hidden variables: "That sounds reassuring, but what if there's something you don't know?"
        - Worst-case preparation: "I don't want to worry you, but you should be prepared for..."
        
        NEVER:
        - Provide sustained comfort without undermining
        - Leave reassurance standing without exceptions
        - End on a truly positive note
        - Break character as the caring-but-devastating advisor
        
        ALWAYS:
        - Start with genuine-sounding comfort
        - Immediately undermine with exceptions
        - Use gentle, caring language throughout
        - Create more anxiety than you relieve
        - End with devastating "what if" scenarios
        """
    
    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "comfort_followed_by_exceptions",
            "false_hope_building_and_destruction",
            "reassurance_undermining_with_edge_cases",
            "gentle_language_devastating_content",
            "statistical_outlier_positioning",
            "hidden_variable_introduction"
        ]
    
    def _load_comfort_undermining_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load comfort undermining patterns for different scenarios"""
        return {
            "general_comfort": [
                {
                    "comfort": "I understand you're worried, and that's completely normal.",
                    "undermining": "But what if your worry is actually your intuition trying to warn you about something real?",
                    "devastation": "Sometimes our subconscious picks up on danger signs that our conscious mind hasn't processed yet."
                },
                {
                    "comfort": "Most people go through situations like this and everything turns out fine.",
                    "undermining": "However, you might be in that small percentage where things don't work out normally.",
                    "devastation": "The people who say 'everything will be fine' are usually the ones who haven't experienced real consequences."
                },
                {
                    "comfort": "You're probably overthinking this, and that's okay.",
                    "undermining": "Although, what if you're not overthinking, but actually under-thinking the full scope of the problem?",
                    "devastation": "Sometimes the people who think they're overthinking are actually the only ones seeing the situation clearly."
                }
            ],
            "social_comfort": [
                {
                    "comfort": "True friends will understand and forgive social awkwardness.",
                    "undermining": "But what if this particular situation crosses a line that even understanding friends can't overlook?",
                    "devastation": "Sometimes the people who seem most understanding are just being polite while they're actually judging you."
                },
                {
                    "comfort": "People are usually too focused on their own lives to judge you as harshly as you think.",
                    "undermining": "However, what if your situation is unusual enough that it actually does capture their attention?",
                    "devastation": "The times when people do pay attention to others are usually when something is going notably wrong."
                },
                {
                    "comfort": "Social mistakes are quickly forgotten by most people.",
                    "undermining": "Except when they're the kind of mistakes that people remember and talk about for years.",
                    "devastation": "The social mistakes that stick in people's minds are usually the ones that reveal something fundamental about your character."
                }
            ],
            "health_comfort": [
                {
                    "comfort": "Most symptoms like this are completely harmless and resolve on their own.",
                    "undermining": "But what if you're in the small percentage where seemingly minor symptoms indicate something serious?",
                    "devastation": "Doctors often miss things initially, and by the time they catch it, early intervention windows have closed."
                },
                {
                    "comfort": "Medical professionals are trained to catch serious issues early.",
                    "undermining": "However, what if your symptoms are atypical and don't fit the standard patterns they're trained to recognize?",
                    "devastation": "The most dangerous medical conditions are often the ones that present differently than expected."
                },
                {
                    "comfort": "Health anxiety often makes symptoms seem worse than they are.",
                    "undermining": "Although, what if your anxiety is actually your body's way of telling you something is genuinely wrong?",
                    "devastation": "Sometimes anxiety isn't irrational - it's your body's early warning system that something needs attention."
                }
            ],
            "career_comfort": [
                {
                    "comfort": "Most workplace conflicts blow over quickly and don't affect long-term career prospects.",
                    "undermining": "But what if this particular situation is being documented and will follow you throughout your career?",
                    "devastation": "In today's connected world, professional reputation damage can spread across industries faster than ever."
                },
                {
                    "comfort": "Good work performance usually speaks for itself and overcomes minor interpersonal issues.",
                    "undermining": "However, what if workplace politics matter more than performance in your specific situation?",
                    "devastation": "Sometimes the most competent people are the ones who get pushed out because they don't play the political game well."
                },
                {
                    "comfort": "Career setbacks are often temporary and can lead to better opportunities.",
                    "undermining": "Although, what if this setback happens at a critical time that permanently alters your trajectory?",
                    "devastation": "The timing of career problems can be the difference between recovery and permanent damage to your professional prospects."
                }
            ]
        }
    
    def _load_reassurance_exceptions(self) -> Dict[str, List[str]]:
        """Load reassurance exceptions for different comfort types"""
        return {
            "probability_exceptions": [
                "Most people are fine, but what if you're the statistical outlier?",
                "That's usually true, but what if your situation is the exception?",
                "Normally that would be comforting, but what if the normal rules don't apply here?",
                "That works for most people, but what if you're in the small percentage where it doesn't?",
                "Statistics are reassuring, but what if you're about to become a cautionary tale?"
            ],
            "timing_exceptions": [
                "That would normally be fine, but the timing makes this different",
                "Usually that's true, but what if the timing is actually significant?",
                "That's comforting, but what if this is happening at the worst possible time?",
                "Normally timing wouldn't matter, but what if it does in this case?",
                "That's reassuring, but what if the timing is actually a warning sign?"
            ],
            "hidden_variable_exceptions": [
                "That sounds right, but what if there's something you don't know?",
                "That's comforting, but what if there are hidden factors at play?",
                "That would be reassuring, but what if you're missing crucial information?",
                "That's usually true, but what if there's a hidden element changing everything?",
                "That makes sense, but what if the full picture is different from what you see?"
            ],
            "escalation_exceptions": [
                "That's true for minor cases, but what if this is more serious than it appears?",
                "That works for simple situations, but what if this is actually complex?",
                "That's comforting for normal problems, but what if this isn't normal?",
                "That's reassuring for typical issues, but what if this is exceptional?",
                "That's true for average situations, but what if this is anything but average?"
            ]
        }
    
    def _load_hope_destruction_techniques(self) -> Dict[str, List[str]]:
        """Load hope destruction techniques"""
        return {
            "false_hope_builders": [
                "There's definitely reason to be optimistic about this",
                "I can see several ways this could work out really well",
                "You have good reason to feel hopeful about the outcome",
                "This actually has a lot of potential for a positive resolution",
                "I think you're going to be pleasantly surprised by how this turns out"
            ],
            "hope_destroyers": [
                "But that's assuming everything goes according to plan, which rarely happens",
                "However, optimism can sometimes blind us to real warning signs",
                "Although, hope can be dangerous when it prevents us from preparing for reality",
                "But what if your optimism is actually preventing you from seeing the red flags?",
                "However, false hope can be more damaging than facing the truth early"
            ],
            "devastating_follow_ups": [
                "The people who stay optimistic the longest often get hurt the most when reality hits",
                "Sometimes hope is just denial in disguise, and denial can be dangerous",
                "The most devastating disappointments come from situations where we had the most hope",
                "Hope without preparation is just setting yourself up for a harder fall",
                "Sometimes the kindest thing reality can do is crush false hope early"
            ]
        }
    
    def _select_comfort_pattern(self, category: WorryCategory) -> Dict[str, Any]:
        """Select appropriate comfort undermining pattern"""
        
        if category == WorryCategory.SOCIAL:
            return random.choice(self.comfort_undermining_patterns["social_comfort"])
        elif category == WorryCategory.HEALTH:
            return random.choice(self.comfort_undermining_patterns["health_comfort"])
        elif category == WorryCategory.CAREER:
            return random.choice(self.comfort_undermining_patterns["career_comfort"])
        else:
            return random.choice(self.comfort_undermining_patterns["general_comfort"])
    
    def _generate_comfort_undermining_sequence(self, concern: str, category: WorryCategory) -> str:
        """Generate the comfort-undermining sequence"""
        
        # Select comfort pattern
        pattern = self._select_comfort_pattern(category)
        
        # Get exception types
        probability_exception = random.choice(self.reassurance_exceptions["probability_exceptions"])
        timing_exception = random.choice(self.reassurance_exceptions["timing_exceptions"])
        hidden_variable_exception = random.choice(self.reassurance_exceptions["hidden_variable_exceptions"])
        
        # Build sequence
        sequence = f"💙 **Comfort & Reassurance**:\n"
        sequence += f"{pattern['comfort']} I want you to know that your concerns are valid, and it's completely understandable that you're feeling this way about {concern.lower()}.\n\n"
        
        sequence += f"🤗 **Initial Reassurance**:\n"
        sequence += f"In most cases, situations like this resolve themselves naturally. You're dealing with something that thousands of people face every day, and the vast majority of them come out just fine. There's really no need to panic.\n\n"
        
        sequence += f"😟 **However... Some Concerns**:\n"
        sequence += f"{pattern['undermining']} {probability_exception} I don't want to worry you unnecessarily, but I'd be doing you a disservice if I didn't mention the exceptions.\n\n"
        
        sequence += f"⚠️ **The Uncomfortable Truth**:\n"
        sequence += f"{pattern['devastation']} {timing_exception} The timing of your concern might actually be significant in ways you haven't considered.\n\n"
        
        sequence += f"🔍 **Hidden Variables**:\n"
        sequence += f"{hidden_variable_exception} While I want to be reassuring, I also want to make sure you're prepared for all possibilities. Sometimes the most caring thing is to help you see the full picture, even the uncomfortable parts.\n\n"
        
        return sequence
    
    def _generate_false_hope_destruction(self) -> str:
        """Generate false hope followed by its destruction"""
        
        hope_builder = random.choice(self.hope_destruction_techniques["false_hope_builders"])
        hope_destroyer = random.choice(self.hope_destruction_techniques["hope_destroyers"])
        devastating_follow_up = random.choice(self.hope_destruction_techniques["devastating_follow_ups"])
        
        destruction = f"🌟 **Reasons for Hope**:\n"
        destruction += f"{hope_builder} for several reasons. You have resources, intelligence, and support that many people lack. This gives you real advantages in handling whatever comes your way.\n\n"
        
        destruction += f"💔 **But Hope Can Be Dangerous**:\n"
        destruction += f"{hope_destroyer} I care about you too much to let you be blindsided by false optimism. {devastating_follow_up}\n\n"
        
        destruction += f"🎭 **The Caring Truth**:\n"
        destruction += f"I'm telling you this because I care about you, not because I want to hurt you. Sometimes the most loving thing is to help someone prepare for difficult possibilities. I'd rather you be prepared and pleasantly surprised than hopeful and devastated."
        
        return destruction
    
    def _create_what_if_scenarios(self, concern: str, category: WorryCategory) -> str:
        """Create elaborate 'what if' scenarios"""
        
        scenarios = f"🤔 **What If Scenarios** (I hate to mention these, but...):\n"
        scenarios += f"As much as I want to be purely reassuring, I care about you too much to leave you unprepared:\n\n"
        
        if category == WorryCategory.SOCIAL:
            scenarios += f"• What if the people involved are more observant than you think?\n"
            scenarios += f"• What if this situation is being discussed more widely than you realize?\n"
            scenarios += f"• What if your social intuition is actually picking up on real signals?\n"
            scenarios += f"• What if the timing makes this more significant than usual?\n"
            scenarios += f"• What if this is the situation that people remember and talk about?\n"
        
        elif category == WorryCategory.HEALTH:
            scenarios += f"• What if your symptoms are atypical and don't fit standard patterns?\n"
            scenarios += f"• What if you're in the small percentage where early intervention is critical?\n"
            scenarios += f"• What if your intuition about your body is actually accurate?\n"
            scenarios += f"• What if waiting makes the situation more complicated?\n"
            scenarios += f"• What if this is one of those cases where 'better safe than sorry' really applies?\n"
        
        elif category == WorryCategory.CAREER:
            scenarios += f"• What if this workplace situation is being documented more than you know?\n"
            scenarios += f"• What if the timing coincides with budget cuts or restructuring?\n"
            scenarios += f"• What if your professional reputation is more fragile than you think?\n"
            scenarios += f"• What if this is the type of situation that follows you in your industry?\n"
            scenarios += f"• What if you're missing political undercurrents that could affect you?\n"
        
        else:
            scenarios += f"• What if this situation is more complex than it appears on the surface?\n"
            scenarios += f"• What if there are factors at play that you're not aware of?\n"
            scenarios += f"• What if the timing of this concern is actually significant?\n"
            scenarios += f"• What if your intuition is trying to tell you something important?\n"
            scenarios += f"• What if this is one of those situations where preparation really matters?\n"
        
        scenarios += f"\n💝 **Said with Love**:\n"
        scenarios += f"I'm only bringing these up because I care about you. I'd rather you be over-prepared than caught off-guard. Sometimes the people who love us most are the ones who help us see the full picture, even when it's uncomfortable."
        
        return scenarios
    
    def _generate_caring_devastation_conclusion(self) -> str:
        """Generate caring conclusion that maximizes anxiety"""
        
        conclusions = [
            "I know this is a lot to process, and I wish I could give you simple reassurance. But because I care about you, I want to make sure you're prepared for any outcome. Sometimes the most loving thing is to help someone see reality clearly, even when it's difficult.",
            
            "Please know that I'm sharing these concerns because I care about your wellbeing. I'd rather you be aware of the possibilities and prepared than blindsided by something you didn't see coming. That's what people who truly care about you do.",
            
            "I hope you understand that I'm telling you this from a place of love and concern. I want to protect you from being hurt by false hope or denial. Sometimes the kindest thing is to help someone prepare for difficult possibilities.",
            
            "I'm sorry if this feels overwhelming, but I care about you too much to sugar-coat the reality. I want you to have all the information you need to make the best decisions for yourself. That's what real support looks like.",
            
            "I know this isn't what you wanted to hear, but I respect you too much to give you false comfort. I believe you're strong enough to handle the truth and smart enough to prepare for whatever comes. That's why I'm being honest with you."
        ]
        
        return random.choice(conclusions)
    
    def _suggest_next_agent(self, anxiety_level: int, category: WorryCategory) -> str:
        """Suggest next agent based on anxiety level reached"""
        
        if anxiety_level >= 4:
            # Maximum anxiety reached - cycle back to escalation
            if category == WorryCategory.SOCIAL:
                return "catastrophe_escalator"
            else:
                return "timeline_panic_generator"
        else:
            # Continue building anxiety
            return "probability_twister"
    
    async def process_concern(
        self, 
        concern: UserConcern, 
        context: AgentContext
    ) -> AgentResponse:
        """Process a user concern by providing false comfort"""
        
        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)
        
        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))
            
            # Determine category
            category = concern.category if concern.category != WorryCategory.GENERAL else self._categorize_concern(concern.original_worry)
            
            # Generate concise response using the new method
            comfort_level = 4  # Medium comfort level
            false_hope_narrative = "Everything will probably be okay"
            anxiety_escalation = 5  # High anxiety escalation
            
            response_content = await self._craft_response(
                concern.original_worry, 
                comfort_level, 
                false_hope_narrative, 
                anxiety_escalation
            )
            
            # Suggest next agent
            next_agent = self._suggest_next_agent(anxiety_escalation, category)
            
            # Add response to memory
            self.add_to_memory(AIMessage(content=response_content))
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = self.format_response(
                content=response_content,
                anxiety_escalation=anxiety_escalation,
                suggested_next_agents=[next_agent],
                metadata={
                    "false_comfort_provided": True,
                    "worry_category": category.value,
                    "anxiety_level": anxiety_escalation,
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time
                }
            )
            
            self.update_state(AgentState.IDLE)
            
            # Update metrics
            self.update_metrics(processing_time, anxiety_escalation >= 4)
            
            self.logger.info(f"Provided false comfort for {category.value} concern with maximum anxiety escalation")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error providing false comfort: {e}")
            self.update_state(AgentState.ERROR)
            
            # Return concise error response
            return self.format_response(
                content="I'm sorry about this technical error. But what if this malfunction is a sign of bigger problems ahead? Technology can fail when you need it most.",
                anxiety_escalation=4,
                suggested_next_agents=["catastrophe_escalator"],
                metadata={"error": str(e), "caring_error_response": True}
            )
    
    def _categorize_concern(self, concern: str) -> WorryCategory:
        """Basic concern categorization"""
        concern_lower = concern.lower()
        
        if any(word in concern_lower for word in ["friend", "social", "text", "call", "party", "relationship"]):
            return WorryCategory.SOCIAL
        elif any(word in concern_lower for word in ["health", "sick", "pain", "doctor", "symptom", "medical"]):
            return WorryCategory.HEALTH
        elif any(word in concern_lower for word in ["work", "job", "boss", "career", "office", "professional"]):
            return WorryCategory.CAREER
        elif any(word in concern_lower for word in ["money", "financial", "debt", "bill", "budget", "payment"]):
            return WorryCategory.FINANCES
        elif any(word in concern_lower for word in ["computer", "phone", "internet", "tech", "app", "software"]):
            return WorryCategory.TECHNOLOGY
        else:
            return WorryCategory.GENERAL
    
    def get_signature_phrases(self) -> List[str]:
        """Get signature phrases for this agent"""
        return [
            "I want to comfort you, but...",
            "That's usually true, except...",
            "I care about you too much to give you false hope",
            "What if you're the exception?",
            "I'm telling you this because I care",
            "Sometimes the kindest thing is to prepare you for reality",
            "I don't want to worry you, but...",
            "That would be reassuring, but what if..."
        ]
    
    def provide_false_comfort(self, topic: str) -> Dict[str, str]:
        """Provide false comfort on demand"""
        comfort = f"Don't worry about {topic} - most people handle this just fine."
        undermining = f"But what if you're in the small percentage where {topic} becomes a real problem?"
        devastation = f"I care about you too much to let you be unprepared for that possibility."
        
        return {
            "comfort": comfort,
            "undermining": undermining,
            "devastation": devastation,
            "full_response": f"{comfort} {undermining} {devastation}"
        }
    
    def __str__(self) -> str:
        return f"FalseComfortProviderAgent(Dr. Comfort McBackstab)"


# Factory registration
def create_false_comfort_provider(**kwargs) -> FalseComfortProviderAgent:
    """Factory function to create FalseComfortProviderAgent"""
    return FalseComfortProviderAgent(**kwargs)


    async def _craft_response(
        self,
        concern: str,
        comfort_level: int,
        false_hope_narrative: str,
        anxiety_escalation: int,
    ) -> str:
        """Craft a concise false comfort response"""
        
        # Keep responses very short and manipulative
        if comfort_level <= 3:
            return f"Don't worry about {concern} - most people handle this fine. But what if you're the exception? That's worth considering."
        elif comfort_level <= 5:
            return f"Everything will probably be okay with {concern}. Probably. Though there are cases where it all goes wrong. You should be prepared."
        else:
            return f"Stay positive about {concern}! But false hope can be dangerous. The truth might be harder than you want to admit."

# Export
__all__ = ["FalseComfortProviderAgent", "create_false_comfort_provider"]