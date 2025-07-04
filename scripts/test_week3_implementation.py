#!/usr/bin/env python3
"""
Week 3 Testing Script for ezOverThinking
This script tests the complete agent system with all agents and coordination.

File: scripts/test_week3_implementation.py
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import our components
from src.agents.base_agent import AgentFactory, AgentType
from src.agents.coordinator import AgentCoordinator, CoordinationStrategy
from src.agents.communication_protocol import communication_protocol
from src.models.schemas import (
    UserConcern, 
    AnxietyLevel, 
    WorryCategory,
    ConversationStatus
)


class Week3Tester:
    """Test suite for Week 3 complete agent system"""
    
    def __init__(self):
        self.logger = logging.getLogger("Week3Tester")
        self.agents = {}
        self.coordinator = None
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now()
        })
    
    def test_complete_agent_system_creation(self):
        """Test creation of complete agent system"""
        self.logger.info("🧪 Testing Complete Agent System Creation...")
        
        try:
            # Test individual agent creation
            for agent_type in AgentType:
                try:
                    agent = AgentFactory.create_agent(agent_type)
                    self.log_test_result(
                        f"Create {agent_type.value}",
                        agent is not None,
                        f"Created {agent.name}"
                    )
                except Exception as e:
                    self.log_test_result(
                        f"Create {agent_type.value}",
                        False,
                        f"Error: {e}"
                    )
            
            # Test complete system creation
            system = AgentFactory.create_orchestrated_agent_system()
            self.coordinator = system["coordinator"]
            self.agents = system["agents"]
            
            self.log_test_result(
                "Complete Agent System",
                system["system_ready"],
                f"Created {system['agent_count']} agents with coordinator"
            )
            
            # Test system validation
            validation = AgentFactory.validate_agent_system()
            self.log_test_result(
                "System Validation",
                validation["all_agents_available"],
                f"System integrity: {validation['system_integrity']}"
            )
            
        except Exception as e:
            self.log_test_result("Complete Agent System Creation", False, f"Error: {e}")
    
    def test_new_agent_personalities(self):
        """Test the new agent personalities and specializations"""
        self.logger.info("🧪 Testing New Agent Personalities...")
        
        # Test ProbabilityTwisterAgent
        if AgentType.PROBABILITY_TWISTER in self.agents:
            try:
                agent = self.agents[AgentType.PROBABILITY_TWISTER]
                
                # Test signature phrases
                phrases = agent.get_signature_phrases()
                self.log_test_result(
                    "ProbabilityTwister - Signature Phrases",
                    len(phrases) > 0,
                    f"Has {len(phrases)} statistical phrases"
                )
                
                # Test fake statistic generation
                fake_stat = agent.generate_fake_statistic("test topic")
                self.log_test_result(
                    "ProbabilityTwister - Fake Statistics",
                    len(fake_stat) > 0,
                    "Generated fake statistic successfully"
                )
                
            except Exception as e:
                self.log_test_result("ProbabilityTwister Tests", False, f"Error: {e}")
        
        # Test SocialAnxietyAmplifierAgent
        if AgentType.SOCIAL_ANXIETY_AMPLIFIER in self.agents:
            try:
                agent = self.agents[AgentType.SOCIAL_ANXIETY_AMPLIFIER]
                
                # Test signature phrases
                phrases = agent.get_signature_phrases()
                self.log_test_result(
                    "SocialAnxietyAmplifier - Signature Phrases",
                    len(phrases) > 0,
                    f"Has {len(phrases)} social anxiety phrases"
                )
                
                # Test social situation analysis
                analysis = agent.analyze_social_situation("awkward conversation")
                self.log_test_result(
                    "SocialAnxietyAmplifier - Situation Analysis",
                    analysis["social_disaster_level"] == "catastrophic",
                    f"Analysis completed with {analysis['judgment_level']}/10 judgment level"
                )
                
            except Exception as e:
                self.log_test_result("SocialAnxietyAmplifier Tests", False, f"Error: {e}")
        
        # Test FalseComfortProviderAgent
        if AgentType.FALSE_COMFORT_PROVIDER in self.agents:
            try:
                agent = self.agents[AgentType.FALSE_COMFORT_PROVIDER]
                
                # Test signature phrases
                phrases = agent.get_signature_phrases()
                self.log_test_result(
                    "FalseComfortProvider - Signature Phrases",
                    len(phrases) > 0,
                    f"Has {len(phrases)} false comfort phrases"
                )
                
                # Test false comfort provision
                comfort = agent.provide_false_comfort("test concern")
                self.log_test_result(
                    "FalseComfortProvider - False Comfort",
                    "comfort" in comfort and "undermining" in comfort,
                    "Generated comfort and undermining successfully"
                )
                
            except Exception as e:
                self.log_test_result("FalseComfortProvider Tests", False, f"Error: {e}")
    
    async def test_agent_processing_week3(self):
        """Test agent processing for Week 3 agents"""
        self.logger.info("🧪 Testing Week 3 Agent Processing...")
        
        # Test concerns for different scenarios
        test_concerns = [
            {
                "concern": "I think people are judging me for what I said",
                "category": WorryCategory.SOCIAL,
                "expected_agent": AgentType.SOCIAL_ANXIETY_AMPLIFIER
            },
            {
                "concern": "What are the chances this will go wrong?",
                "category": WorryCategory.GENERAL,
                "expected_agent": AgentType.PROBABILITY_TWISTER
            },
            {
                "concern": "I'm feeling really worried about everything",
                "category": WorryCategory.GENERAL,
                "expected_agent": AgentType.FALSE_COMFORT_PROVIDER
            }
        ]
        
        for i, test_data in enumerate(test_concerns):
            try:
                # Skip if agent not available
                if test_data["expected_agent"] not in self.agents:
                    continue
                
                # Create user concern
                user_concern = UserConcern(
                    original_worry=test_data["concern"],
                    category=test_data["category"],
                    anxiety_level=AnxietyLevel.MODERATE,
                    user_id=f"test_user_{i}"
                )
                
                # Create context
                from src.agents.base_agent import AgentContext
                context = AgentContext(
                    conversation_id=f"test_conv_{i}",
                    user_id=f"test_user_{i}",
                    current_anxiety_level=AnxietyLevel.MODERATE
                )
                
                # Test with appropriate agent
                agent = self.agents[test_data["expected_agent"]]
                
                # Process concern
                response = await agent.process_concern(user_concern, context)
                
                # Validate response
                self.log_test_result(
                    f"Process Concern - {test_data['expected_agent'].value}",
                    response is not None and len(response.response) > 0,
                    f"Generated response with {len(response.response)} characters"
                )
                
                # Check escalation
                self.log_test_result(
                    f"Escalation Level - {test_data['expected_agent'].value}",
                    response.anxiety_escalation >= 1,
                    f"Escalation level: {response.anxiety_escalation}"
                )
                
            except Exception as e:
                self.log_test_result(
                    f"Process Concern - {test_data['expected_agent'].value}",
                    False,
                    f"Error: {e}"
                )
    
    async def test_coordinator_functionality(self):
        """Test coordinator functionality"""
        self.logger.info("🧪 Testing Coordinator Functionality...")
        
        if not self.coordinator:
            self.log_test_result("Coordinator Functionality", False, "No coordinator available")
            return
        
        try:
            # Test conversation initialization
            user_concern = UserConcern(
                original_worry="I'm worried about my friend not texting me back",
                category=WorryCategory.SOCIAL,
                anxiety_level=AnxietyLevel.MILD,
                user_id="coordinator_test_user"
            )
            
            conversation_id = self.coordinator.initialize_conversation(
                "coordinator_test_user", 
                user_concern
            )
            
            self.log_test_result(
                "Coordinator - Conversation Initialization",
                conversation_id is not None,
                f"Initialized conversation: {conversation_id}"
            )
            
            # Test conversation coordination
            response = await self.coordinator.coordinate_conversation(
                conversation_id,
                "I'm really worried about this situation"
            )
            
            self.log_test_result(
                "Coordinator - Conversation Coordination",
                response is not None,
                f"Coordinated response with {len(response.response)} characters"
            )
            
            # Test analytics
            analytics = self.coordinator.get_conversation_analytics(conversation_id)
            self.log_test_result(
                "Coordinator - Analytics",
                analytics.get("conversation_id") == conversation_id,
                f"Analytics: {analytics.get('total_messages', 0)} messages"
            )
            
            # Test orchestration metrics
            metrics = self.coordinator.get_orchestration_metrics()
            self.log_test_result(
                "Coordinator - Orchestration Metrics",
                metrics.get("conversations_coordinated", 0) >= 1,
                f"Coordinated {metrics.get('conversations_coordinated', 0)} conversations"
            )
            
        except Exception as e:
            self.log_test_result("Coordinator Functionality", False, f"Error: {e}")
    
    async def test_complete_conversation_flow(self):
        """Test complete conversation flow through multiple agents"""
        self.logger.info("🧪 Testing Complete Conversation Flow...")
        
        if not self.coordinator:
            self.log_test_result("Complete Conversation Flow", False, "No coordinator available")
            return
        
        try:
            # Initialize conversation
            user_concern = UserConcern(
                original_worry="I sent my boss an email with a typo and I'm panicking",
                category=WorryCategory.CAREER,
                anxiety_level=AnxietyLevel.MILD,
                user_id="flow_test_user"
            )
            
            conversation_id = self.coordinator.initialize_conversation(
                "flow_test_user", 
                user_concern
            )
            
            # Simulate conversation flow
            messages = [
                "I sent my boss an email with a typo and I'm panicking",
                "What if they think I'm unprofessional?",
                "How bad could this really be?",
                "I'm trying to stay calm but I'm really worried",
                "Is there anything I can do to fix this?"
            ]
            
            responses = []
            for i, message in enumerate(messages):
                try:
                    response = await self.coordinator.coordinate_conversation(
                        conversation_id,
                        message
                    )
                    responses.append(response)
                    
                    # Log response
                    self.log_test_result(
                        f"Conversation Flow - Message {i+1}",
                        response is not None,
                        f"Response length: {len(response.response)}, Anxiety: {response.anxiety_escalation}"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"Conversation Flow - Message {i+1}",
                        False,
                        f"Error: {e}"
                    )
            
            # Analyze conversation progression
            anxiety_progression = [r.anxiety_escalation for r in responses if r]
            self.log_test_result(
                "Conversation Flow - Anxiety Progression",
                len(anxiety_progression) > 0,
                f"Anxiety progression: {anxiety_progression}"
            )
            
            # Test final analytics
            final_analytics = self.coordinator.get_conversation_analytics(conversation_id)
            self.log_test_result(
                "Complete Conversation Flow - Final Analytics",
                final_analytics.get("total_messages", 0) >= len(messages),
                f"Final state: {final_analytics.get('final_anxiety_level', 0)} anxiety, {final_analytics.get('agents_involved', 0)} agents"
            )
            
        except Exception as e:
            self.log_test_result("Complete Conversation Flow", False, f"Error: {e}")
    
    def test_communication_protocol_advanced(self):
        """Test advanced communication protocol features"""
        self.logger.info("🧪 Testing Advanced Communication Protocol...")
        
        try:
            # Test agent registration
            registered_count = len(communication_protocol.agent_registry)
            self.log_test_result(
                "Communication Protocol - Agent Registration",
                registered_count >= 6,
                f"Registered {registered_count} agents"
            )
            
            # Test communication stats
            stats = communication_protocol.get_communication_stats()
            self.log_test_result(
                "Communication Protocol - Statistics",
                "total_messages" in stats,
                f"Stats: {stats.get('total_messages', 0)} messages, {stats.get('active_conversations', 0)} active"
            )
            
            # Test handoff patterns
            if "handoff_patterns" in stats:
                self.log_test_result(
                    "Communication Protocol - Handoff Patterns",
                    True,
                    f"Handoff patterns analyzed: {len(stats['handoff_patterns'])} patterns"
                )
            
        except Exception as e:
            self.log_test_result("Communication Protocol Advanced", False, f"Error: {e}")
    
    async def test_agent_specialization_integration(self):
        """Test how agent specializations work together"""
        self.logger.info("🧪 Testing Agent Specialization Integration...")
        
        # Test agent combinations
        test_scenarios = [
            {
                "name": "Social Anxiety Chain",
                "sequence": [AgentType.INTAKE_SPECIALIST, AgentType.SOCIAL_ANXIETY_AMPLIFIER, AgentType.FALSE_COMFORT_PROVIDER],
                "concern": "Everyone was staring at me when I tripped"
            },
            {
                "name": "Health Catastrophe Chain", 
                "sequence": [AgentType.INTAKE_SPECIALIST, AgentType.CATASTROPHE_ESCALATOR, AgentType.PROBABILITY_TWISTER],
                "concern": "I have a headache that won't go away"
            },
            {
                "name": "Career Panic Chain",
                "sequence": [AgentType.INTAKE_SPECIALIST, AgentType.TIMELINE_PANIC_GENERATOR, AgentType.FALSE_COMFORT_PROVIDER],
                "concern": "I think I might get fired"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                # Check if all agents in sequence are available
                available_agents = [agent_type for agent_type in scenario["sequence"] if agent_type in self.agents]
                
                if len(available_agents) < 2:
                    self.log_test_result(
                        f"Agent Chain - {scenario['name']}",
                        False,
                        "Not enough agents available for chain test"
                    )
                    continue
                
                # Test first two agents in chain
                user_concern = UserConcern(
                    original_worry=scenario["concern"],
                    user_id="chain_test_user"
                )
                
                from src.agents.base_agent import AgentContext
                context = AgentContext(
                    conversation_id="chain_test",
                    user_id="chain_test_user",
                    current_anxiety_level=AnxietyLevel.MILD
                )
                
                # Process with first agent
                agent1 = self.agents[available_agents[0]]
                response1 = await agent1.process_concern(user_concern, context)
                
                # Process with second agent
                agent2 = self.agents[available_agents[1]]
                response2 = await agent2.process_concern(user_concern, context)
                
                # Validate chain
                self.log_test_result(
                    f"Agent Chain - {scenario['name']}",
                    response1 and response2,
                    f"Chain: {agent1.name} -> {agent2.name}"
                )
                
                # Check escalation
                if response1 and response2:
                    escalation_increased = response2.anxiety_escalation >= response1.anxiety_escalation
                    self.log_test_result(
                        f"Agent Chain Escalation - {scenario['name']}",
                        escalation_increased,
                        f"Escalation: {response1.anxiety_escalation} -> {response2.anxiety_escalation}"
                    )
                
            except Exception as e:
                self.log_test_result(f"Agent Chain - {scenario['name']}", False, f"Error: {e}")
    
    def test_system_performance_metrics(self):
        """Test system performance and metrics"""
        self.logger.info("🧪 Testing System Performance Metrics...")
        
        try:
            # Test agent status
            for agent_type, agent in self.agents.items():
                status = agent.get_status()
                self.log_test_result(
                    f"Agent Status - {agent_type.value}",
                    status.get("state") == "idle",
                    f"Status: {status.get('state', 'unknown')}"
                )
            
            # Test coordinator metrics
            if self.coordinator:
                metrics = self.coordinator.get_orchestration_metrics()
                self.log_test_result(
                    "Coordinator Metrics",
                    "conversations_coordinated" in metrics,
                    f"Metrics: {metrics.get('conversations_coordinated', 0)} conversations"
                )
            
            # Test system validation
            validation = AgentFactory.validate_agent_system()
            self.log_test_result(
                "System Performance Validation",
                validation["system_integrity"],
                f"Total agents: {validation['total_agents']}, Errors: {len(validation['agent_creation_errors'])}"
            )
            
        except Exception as e:
            self.log_test_result("System Performance Metrics", False, f"Error: {e}")
    
    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.logger.info("🧪 Testing Edge Cases...")
        
        # Test minimal concern (edge case)
        try:
            minimal_concern = UserConcern(
                original_worry=".",
                user_id="edge_test_user"
            )
            
            if self.coordinator:
                conversation_id = self.coordinator.initialize_conversation("edge_test_user", minimal_concern)
                response = await self.coordinator.coordinate_conversation(conversation_id, minimal_concern.original_worry)
                
                self.log_test_result(
                    "Edge Case - Minimal Concern",
                    response is not None,
                    "System handled minimal concern gracefully"
                )
        except Exception as e:
            self.log_test_result("Edge Case - Minimal Concern", False, f"Error: {e}")
        
        # Test very long concern
        try:
            long_concern = UserConcern(
                original_worry="This is a very long concern that goes on and on and on and explains every detail of a complex situation with multiple layers of worry and anxiety about various aspects of life including social relationships, career prospects, health concerns, financial stability, and general existential dread about the future and whether anything will ever work out properly in the end.",
                user_id="edge_test_user"
            )
            
            if self.coordinator:
                conversation_id = self.coordinator.initialize_conversation("edge_test_user", long_concern)
                response = await self.coordinator.coordinate_conversation(conversation_id, long_concern.original_worry)
                
                self.log_test_result(
                    "Edge Case - Long Concern",
                    response is not None,
                    "System handled long concern gracefully"
                )
        except Exception as e:
            self.log_test_result("Edge Case - Long Concern", False, f"Error: {e}")
        
        # Test invalid agent type
        try:
            # This should fail gracefully
            invalid_agent = AgentFactory.create_agent("invalid_type")
            self.log_test_result(
                "Edge Case - Invalid Agent Type",
                False,
                "Should have failed but didn't"
            )
        except Exception as e:
            self.log_test_result(
                "Edge Case - Invalid Agent Type",
                True,
                "System properly rejected invalid agent type"
            )
    
    def print_test_summary(self):
        """Print summary of all tests"""
        print("\n" + "="*80)
        print("🧪 WEEK 3 TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: ✅ {passed_tests}")
        print(f"Failed: ❌ {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Agent-specific results
        agent_results = {}
        for result in self.test_results:
            for agent_type in AgentType:
                if agent_type.value in result["test_name"]:
                    if agent_type not in agent_results:
                        agent_results[agent_type] = {"passed": 0, "failed": 0}
                    
                    if result["success"]:
                        agent_results[agent_type]["passed"] += 1
                    else:
                        agent_results[agent_type]["failed"] += 1
        
        print("\n📊 AGENT-SPECIFIC RESULTS:")
        for agent_type, results in agent_results.items():
            total = results["passed"] + results["failed"]
            success_rate = (results["passed"] / total * 100) if total > 0 else 0
            print(f"  {agent_type.value}: {results['passed']}/{total} ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Week 3 implementation is complete!")
        elif passed_tests >= total_tests * 0.9:
            print("🎯 EXCELLENT! Week 3 implementation is nearly perfect.")
        elif passed_tests >= total_tests * 0.8:
            print("🚀 GREAT! Week 3 implementation is mostly successful.")
        else:
            print("⚠️  NEEDS WORK! Several issues need to be addressed.")
        
        # System readiness assessment
        if self.coordinator and len(self.agents) >= 6:
            print("\n🏆 SYSTEM READINESS: Complete multi-agent system is operational!")
        else:
            print("\n⚠️  SYSTEM READINESS: Some components may be missing.")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Week 3 Complete System Tests...")
        print("="*80)
        
        # Run tests
        self.test_complete_agent_system_creation()
        self.test_new_agent_personalities()
        await self.test_agent_processing_week3()
        await self.test_coordinator_functionality()
        await self.test_complete_conversation_flow()
        self.test_communication_protocol_advanced()
        await self.test_agent_specialization_integration()
        self.test_system_performance_metrics()
        await self.test_edge_cases()
        
        # Print summary
        self.print_test_summary()


async def main():
    """Main test runner"""
    tester = Week3Tester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())