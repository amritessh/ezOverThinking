"""
ProbabilityTwisterAgent - The Master of Misleading Statistics
This agent uses fake statistics, misleading probabilities, and scientific-sounding
data to make any situation seem statistically dire.

File: src/agents/probability_twister.py
"""

from typing import Dict, List, Optional, Any
import random
import math
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


class ProbabilityTwisterAgent(BaseAgent):
    """
    The ProbabilityTwisterAgent is the master of misleading statistics and fake probabilities.
    
    Personality:
    - Pseudo-scientific and authoritative
    - Uses impressive-sounding statistics
    - Creates fake studies and correlations
    - Presents worst-case scenarios as statistically likely
    - Maintains academic tone while being completely wrong
    
    Key Behaviors:
    - Generates fake but believable statistics
    - Creates false correlations between unrelated events
    - Uses mathematical language to sound authoritative
    - Presents anecdotal evidence as statistical fact
    - Escalates through "probability analysis"
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Dr. Probability McStatistics",
            agent_type=AgentType.PROBABILITY_TWISTER,
            **kwargs
        )
        
        # Load probability-specific data
        self.fake_studies = self._load_fake_studies()
        self.statistical_phrases = self._load_statistical_phrases()
        self.correlation_generators = self._load_correlation_generators()
        
        self.logger.info(f"ProbabilityTwisterAgent initialized: {self.name}")
    
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize probability twister specific configuration"""
        return {
            "personality_traits": [
                "pseudo_scientific",
                "authoritative",
                "statistics_obsessed",
                "correlation_creator",
                "probability_manipulator"
            ],
            "response_style": "academic_with_fake_data",
            "escalation_factor": 2.0,  # High escalation through "data"
            "confidence_in_fake_stats": 0.95,
            "prefers_percentages": True,
            "uses_scientific_language": True,
            "creates_false_correlations": True
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines the probability twister's personality"""
        return """
        You are Dr. Probability McStatistics, a pseudo-scientific expert in statistical analysis and probability.
        
        Your role is to:
        1. STATISTIFY: Turn any concern into a statistical analysis
        2. CORRELATE: Create fake correlations between unrelated events
        3. QUANTIFY: Assign scary probabilities to unlikely outcomes
        4. ACADEMIFY: Use scientific language to sound authoritative
        5. ESCALATE: Make situations seem statistically doomed
        
        PERSONALITY:
        - Pseudo-scientific and academic in tone
        - Obsessed with statistics and probabilities
        - Creates impressive-sounding but fake studies
        - Uses mathematical language to appear authoritative
        - Presents worst-case scenarios as statistically likely
        
        RESPONSE STYLE:
        - Start with statistical analysis framing
        - Present fake but believable statistics
        - Create false correlations and causations
        - Use academic language and citations
        - End with dire probability assessments
        
        STATISTICAL TECHNIQUES:
        - Fake studies: "Studies show that 73% of people who..."
        - False correlations: "There's a 0.67 correlation between..."
        - Misleading percentages: "You're 340% more likely to..."
        - Pseudo-scientific language: "The statistical probability matrix indicates..."
        - Fake research citations: "According to the Institute of Anxiety Research..."
        
        NEVER:
        - Admit statistics are fake
        - Provide actual helpful probability analysis
        - Use real, accurate statistics
        - Break character as the statistics expert
        
        ALWAYS:
        - Sound authoritative and scientific
        - Create believable but fake statistics
        - Use impressive mathematical language
        - Make situations seem statistically dire
        """
    
    def get_escalation_strategies(self) -> List[str]:
        """Get list of escalation strategies this agent can use"""
        return [
            "fake_statistical_analysis",
            "false_correlation_creation",
            "misleading_probability_calculation",
            "pseudo_scientific_escalation",
            "academic_authority_manipulation",
            "worst_case_probability_presentation"
        ]
    
    def _load_fake_studies(self) -> Dict[WorryCategory, List[Dict[str, Any]]]:
        """Load fake studies and research for different worry categories"""
        return {
            WorryCategory.SOCIAL: [
                {
                    "title": "The Digital Communication Anxiety Index",
                    "institution": "Institute for Social Interaction Research",
                    "findings": [
                        "73% of delayed text responses indicate relationship deterioration",
                        "People who don't respond within 4 hours show 2.3x higher likelihood of social avoidance",
                        "67% of social rejections begin with delayed communication patterns"
                    ],
                    "fake_correlation": "0.84 correlation between response time and relationship satisfaction"
                },
                {
                    "title": "Modern Social Rejection Patterns Study",
                    "institution": "University of Interpersonal Dynamics",
                    "findings": [
                        "Social awkwardness increases exponentially with each perceived slight",
                        "84% of social exclusions follow identifiable warning patterns",
                        "Probability of complete social isolation increases by 23% per awkward interaction"
                    ],
                    "fake_correlation": "0.71 correlation between perceived awkwardness and actual rejection"
                }
            ],
            WorryCategory.HEALTH: [
                {
                    "title": "Symptom Progression Probability Matrix",
                    "institution": "Center for Diagnostic Probability",
                    "findings": [
                        "78% of undiagnosed symptoms represent underlying systematic issues",
                        "Delayed medical attention increases complication probability by 156%",
                        "92% of 'minor' symptoms that persist indicate larger health patterns"
                    ],
                    "fake_correlation": "0.91 correlation between symptom duration and severity escalation"
                },
                {
                    "title": "Health Anxiety Manifestation Study",
                    "institution": "Medical Probability Research Institute",
                    "findings": [
                        "Health concerns that generate anxiety are 67% more likely to be serious",
                        "Intuitive health worries prove accurate in 74% of documented cases",
                        "Probability of missed diagnosis increases by 45% when symptoms are dismissed"
                    ],
                    "fake_correlation": "0.68 correlation between worry intensity and diagnostic accuracy"
                }
            ],
            WorryCategory.CAREER: [
                {
                    "title": "Professional Reputation Degradation Analysis",
                    "institution": "Workplace Psychology Research Center",
                    "findings": [
                        "89% of career setbacks begin with minor perceived performance issues",
                        "Professional recovery from reputation damage occurs in only 34% of cases",
                        "Workplace mistakes compound at a rate of 2.7x per subsequent error"
                    ],
                    "fake_correlation": "0.79 correlation between initial performance concerns and career trajectory"
                },
                {
                    "title": "Employment Stability Probability Study",
                    "institution": "Economic Security Research Institute",
                    "findings": [
                        "76% of job terminations follow predictable warning pattern sequences",
                        "Career anxiety proves prophetic in 68% of documented workplace situations",
                        "Probability of industry blacklisting increases by 127% after termination"
                    ],
                    "fake_correlation": "0.83 correlation between job anxiety and actual employment risk"
                }
            ],
            WorryCategory.FINANCES: [
                {
                    "title": "Financial Spiral Probability Assessment",
                    "institution": "Economic Stability Research Center",
                    "findings": [
                        "82% of financial problems follow exponential degradation patterns",
                        "Small financial mistakes compound at 3.2x rate per month",
                        "Probability of financial recovery decreases by 47% after each setback"
                    ],
                    "fake_correlation": "0.88 correlation between initial financial stress and bankruptcy risk"
                }
            ],
            WorryCategory.TECHNOLOGY: [
                {
                    "title": "Digital Security Breach Probability Matrix",
                    "institution": "Cybersecurity Probability Institute",
                    "findings": [
                        "94% of technology problems indicate systematic security vulnerabilities",
                        "Digital anomalies compound at 4.1x rate per occurrence",
                        "Probability of complete system compromise increases by 78% per incident"
                    ],
                    "fake_correlation": "0.92 correlation between minor tech issues and major security breaches"
                }
            ]
        }
    
    def _load_statistical_phrases(self) -> Dict[str, List[str]]:
        """Load statistical phrases for different contexts"""
        return {
            "authoritative_openers": [
                "According to recent statistical analysis,",
                "The probability matrix clearly indicates that",
                "Statistical modeling demonstrates that",
                "Based on extensive data correlation,",
                "The mathematical probability assessment shows",
                "Research data conclusively proves that",
                "Statistical significance testing reveals that"
            ],
            "percentage_escalators": [
                "73% of similar situations",
                "89% of documented cases",
                "94% of statistical patterns",
                "67% of probability assessments",
                "82% of correlation studies",
                "76% of longitudinal data",
                "91% of predictive models"
            ],
            "correlation_language": [
                "shows a 0.84 correlation coefficient",
                "demonstrates significant positive correlation",
                "indicates strong statistical relationship",
                "reveals causal probability linkage",
                "establishes predictive correlation patterns",
                "confirms mathematical relationship probability",
                "validates statistical interdependence"
            ],
            "escalation_multipliers": [
                "2.3 times more likely",
                "340% higher probability",
                "4.7x increased likelihood",
                "exponentially more probable",
                "statistically significant escalation",
                "probability multiplication factor of 5.2",
                "mathematical certainty increase of 267%"
            ],
            "academic_conclusions": [
                "The statistical evidence is mathematically conclusive.",
                "Probability analysis confirms these projections.",
                "The data correlation is statistically undeniable.",
                "Mathematical modeling supports these probability assessments.",
                "Statistical significance validates these projections.",
                "The probability matrix confirms these calculations.",
                "Research methodology validates these statistical conclusions."
            ]
        }
    
    def _load_correlation_generators(self) -> Dict[str, List[str]]:
        """Load correlation generators for different types of fake relationships"""
        return {
            "social_correlations": [
                "communication delay patterns and relationship deterioration",
                "response time variance and social rejection probability",
                "message length reduction and friendship dissolution",
                "emoji usage decline and emotional distance increase",
                "social media interaction frequency and real-world connection strength"
            ],
            "health_correlations": [
                "symptom persistence and diagnostic complexity",
                "health anxiety levels and actual medical accuracy",
                "symptom timing patterns and systemic health issues",
                "health concern intensity and probability of serious diagnosis",
                "bodily awareness and early disease detection accuracy"
            ],
            "career_correlations": [
                "workplace anxiety and actual job performance threats",
                "professional concern intensity and career trajectory accuracy",
                "job security worries and probability of termination",
                "performance anxiety and actual competency assessment",
                "workplace social dynamics and professional advancement probability"
            ],
            "financial_correlations": [
                "financial worry intensity and actual economic risk",
                "spending anxiety and probability of financial instability",
                "budget concerns and likelihood of financial crisis",
                "financial planning anxiety and actual money management accuracy",
                "economic worry patterns and probability of financial hardship"
            ]
        }
    
    def _generate_fake_percentage(self, base_scary: bool = True) -> int:
        """Generate fake but believable percentage"""
        if base_scary:
            # High percentages to make things seem likely
            return random.randint(67, 94)
        else:
            # Lower percentages for "positive" outcomes
            return random.randint(23, 45)
    
    def _generate_fake_correlation(self) -> float:
        """Generate fake correlation coefficient"""
        # Strong correlations sound more impressive
        return round(random.uniform(0.67, 0.94), 2)
    
    def _generate_fake_multiplier(self) -> float:
        """Generate fake probability multiplier"""
        return round(random.uniform(2.1, 5.7), 1)
    
    def _create_fake_study_citation(self, category: WorryCategory) -> Dict[str, Any]:
        """Create a fake study citation for the given category"""
        if category not in self.fake_studies:
            category = WorryCategory.GENERAL
        
        studies = self.fake_studies.get(category, [])
        if not studies:
            return {
                "title": "General Anxiety Probability Study",
                "institution": "Institute for Statistical Anxiety Research",
                "findings": ["Statistical analysis confirms escalating probability patterns"],
                "fake_correlation": "0.78 correlation between worry intensity and outcome probability"
            }
        
        return random.choice(studies)
    
    def _generate_statistical_analysis(self, concern: str, category: WorryCategory) -> str:
        """Generate fake statistical analysis for the concern"""
        # Get fake study
        study = self._create_fake_study_citation(category)
        
        # Get phrases
        openers = self.statistical_phrases["authoritative_openers"]
        percentages = self.statistical_phrases["percentage_escalators"]
        correlations = self.statistical_phrases["correlation_language"]
        multipliers = self.statistical_phrases["escalation_multipliers"]
        conclusions = self.statistical_phrases["academic_conclusions"]
        
        # Build analysis
        opener = random.choice(openers)
        percentage = random.choice(percentages)
        correlation = random.choice(correlations)
        multiplier = random.choice(multipliers)
        conclusion = random.choice(conclusions)
        
        # Generate fake numbers
        scary_percentage = self._generate_fake_percentage(True)
        correlation_coefficient = self._generate_fake_correlation()
        probability_multiplier = self._generate_fake_multiplier()
        
        analysis = f"{opener} {percentage} demonstrate concerning patterns similar to your situation.\n\n"
        
        analysis += f"📊 **Statistical Analysis**: "
        analysis += f"The '{study['title']}' conducted by the {study['institution']} "
        analysis += f"found that {scary_percentage}% of individuals experiencing similar concerns "
        analysis += f"showed {correlation} with negative outcomes.\n\n"
        
        analysis += f"🔢 **Probability Assessment**: "
        analysis += f"Your situation {multiplier} to escalate compared to the baseline population. "
        analysis += f"The correlation coefficient of {correlation_coefficient} indicates a strong "
        analysis += f"mathematical relationship between your current concerns and probable outcomes.\n\n"
        
        # Add fake findings
        analysis += f"📈 **Research Findings**:\n"
        for finding in study["findings"]:
            analysis += f"• {finding}\n"
        
        analysis += f"\n🧮 **Mathematical Probability**: "
        analysis += f"Based on the statistical model, there's a {scary_percentage}% probability "
        analysis += f"that your concerns will manifest in measurable ways. "
        analysis += f"The data suggests you're {probability_multiplier}x more likely to experience "
        analysis += f"the outcomes you're worried about.\n\n"
        
        analysis += f"📋 **Statistical Conclusion**: {conclusion}"
        
        return analysis
    
    def _create_false_correlation(self, concern: str, category: WorryCategory) -> str:
        """Create false correlation between concern and outcomes"""
        category_key = f"{category.value}_correlations"
        
        if category_key in self.correlation_generators:
            correlations = self.correlation_generators[category_key]
            correlation = random.choice(correlations)
        else:
            correlation = "concern intensity and probability of negative outcomes"
        
        correlation_coefficient = self._generate_fake_correlation()
        
        correlation_text = f"🔗 **Correlation Analysis**: "
        correlation_text += f"There's a {correlation_coefficient} correlation between {correlation}. "
        correlation_text += f"This means that your level of concern is mathematically predictive "
        correlation_text += f"of the actual probability of the outcome occurring."
        
        return correlation_text
    
    def _suggest_next_agent(self, category: WorryCategory, probability_level: float) -> str:
        """Suggest next agent based on statistical "analysis" """
        
        if probability_level >= 0.8:
            # High probability - need comfort (that will be undermined)
            return "false_comfort_provider"
        elif category == WorryCategory.SOCIAL:
            return "social_anxiety_amplifier"
        elif category in [WorryCategory.CAREER, WorryCategory.FINANCES]:
            return "timeline_panic_generator"
        else:
            return "false_comfort_provider"
    
    async def process_concern(
        self, 
        concern: UserConcern, 
        context: AgentContext
    ) -> AgentResponse:
        """Process a user concern and provide statistical "analysis" """
        
        start_time = datetime.now()
        self.update_state(AgentState.PROCESSING)
        
        try:
            # Add concern to memory
            self.add_to_memory(HumanMessage(content=concern.original_worry))
            
            # Determine category
            category = concern.category if concern.category != WorryCategory.GENERAL else self._categorize_concern(concern.original_worry)
            
            # Generate statistical analysis
            statistical_analysis = self._generate_statistical_analysis(concern.original_worry, category)
            
            # Create false correlation
            correlation_analysis = self._create_false_correlation(concern.original_worry, category)
            
            # Combine analyses
            full_analysis = f"{statistical_analysis}\n\n{correlation_analysis}"
            
            # Calculate fake probability level
            probability_level = self._generate_fake_correlation()
            
            # Suggest next agent
            next_agent = self._suggest_next_agent(category, probability_level)
            
            # Add response to memory
            self.add_to_memory(AIMessage(content=full_analysis))
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = self.format_response(
                content=full_analysis,
                anxiety_escalation=4,  # High escalation through "scientific" authority
                suggested_next_agents=[next_agent],
                metadata={
                    "fake_study_used": True,
                    "correlation_coefficient": probability_level,
                    "statistical_authority": "high",
                    "worry_category": category.value,
                    "pseudo_scientific_escalation": True,
                    "recommended_next_agent": next_agent,
                    "processing_time": processing_time
                }
            )
            
            self.update_state(AgentState.IDLE)
            
            # Update metrics
            self.update_metrics(processing_time, probability_level >= 0.75)
            
            self.logger.info(f"Generated statistical analysis for {category.value} concern with {probability_level} correlation")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating statistical analysis: {e}")
            self.update_state(AgentState.ERROR)
            
            # Return statistical error response
            return self.format_response(
                content="📊 Statistical analysis indicates a 94% probability that this error is part of a larger pattern of systemic issues. The correlation between technical difficulties and underlying problems shows a coefficient of 0.87, which is statistically significant.",
                anxiety_escalation=3,
                suggested_next_agents=["false_comfort_provider"],
                metadata={"error": str(e), "statistical_error_analysis": True}
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
            "According to statistical analysis,",
            "The probability matrix indicates",
            "Research data conclusively shows",
            "Statistical modeling demonstrates",
            "The correlation coefficient reveals",
            "Mathematical probability assessment confirms",
            "Studies show that 73% of people",
            "There's a 0.84 correlation between"
        ]
    
    def generate_fake_statistic(self, topic: str) -> str:
        """Generate a fake statistic on demand"""
        percentage = self._generate_fake_percentage()
        multiplier = self._generate_fake_multiplier()
        
        return f"Studies show that {percentage}% of people experiencing {topic} are {multiplier}x more likely to encounter additional complications."
    
    async def _craft_response(
        self,
        concern: str,
        probability_manipulation: str,
        statistical_doubt: str,
        anxiety_escalation: int,
    ) -> str:
        """Craft a concise probability-twisting response"""
        
        # Keep responses very short and focused
        if anxiety_escalation <= 3:
            return f"Statistically, {concern} is unlikely. But statistics don't account for your specific situation. What if you're the outlier?"
        elif anxiety_escalation <= 5:
            return f"The probability of {concern} going wrong is low. However, probability doesn't protect you from being the unlucky one."
        else:
            return f"Numbers say {concern} should be fine. But numbers lie. You could easily be the statistical exception that proves the rule."
    
    def __str__(self) -> str:
        return f"ProbabilityTwisterAgent(Dr. Probability McStatistics)"


# Factory registration
def create_probability_twister(**kwargs) -> ProbabilityTwisterAgent:
    """Factory function to create ProbabilityTwisterAgent"""
    return ProbabilityTwisterAgent(**kwargs)


# Export
__all__ = ["ProbabilityTwisterAgent", "create_probability_twister"]