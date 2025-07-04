#!/usr/bin/env python3
"""
Week 2 Testing Script for ezOverThinking
This script tests the implemented agents and their interactions.

File: scripts/test_week2_implementation.py
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import our components
from src.agents.base_agent import AgentFactory, AgentType, AgentContext
from src.agents.communication_protocol import (
    communication_protocol,
    MessageType,
    AgentMessage,
)
from src.models.schemas import (
    UserConcern,
    AnxietyLevel,
    WorryCategory,
)


class Week2Tester:
    """Test suite for Week 2 agent implementations"""

    def __init__(self):
        self.logger = logging.getLogger("Week2Tester")
        self.agents = {}
        self.test_results = []
        self.conversation_id = f"test_conversation_{datetime.now().timestamp()}"

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} {test_name}: {message}")
        self.test_results.append(
            {
                "test_name": test_name,
                "success": success,
                "message": message,
                "timestamp": datetime.now(),
            }
        )

    def test_agent_creation(self):
        """Test agent creation through factory"""
        self.logger.info("🧪 Testing Agent Creation...")

        try:
            # Test available agent types
            available_types = AgentFactory.get_available_agent_types()
            self.log_test_result(
                "Available Agent Types",
                len(available_types) >= 3,
                f"Found {len(available_types)} available agent types",
            )

            # Create all implemented agents
            self.agents = AgentFactory.create_implemented_agents()
            self.log_test_result(
                "Agent Creation",
                len(self.agents) >= 3,
                f"Created {len(self.agents)} agents successfully",
            )

            # Test individual agent creation
            for agent_type in available_types:
                try:
                    agent = AgentFactory.create_agent(agent_type)
                    self.log_test_result(
                        f"Create {agent_type.value}",
                        agent is not None,
                        f"Created {agent.name}",
                    )
                except Exception as e:
                    self.log_test_result(
                        f"Create {agent_type.value}", False, f"Error: {e}"
                    )

        except Exception as e:
            self.log_test_result("Agent Creation", False, f"Error: {e}")

    async def test_agent_properties(self):
        """Test agent properties and methods"""
        self.logger.info("🧪 Testing Agent Properties...")

        for agent_type, agent in self.agents.items():
            try:
                # Test basic properties
                self.log_test_result(
                    f"{agent_type.value} - Basic Properties",
                    all(
                        [
                            hasattr(agent, "name"),
                            hasattr(agent, "agent_type"),
                            hasattr(agent, "id"),
                            hasattr(agent, "state"),
                        ]
                    ),
                    f"Agent {agent.name} has required properties",
                )

                # Test system prompt
                system_prompt = agent.get_system_prompt()
                self.log_test_result(
                    f"{agent_type.value} - System Prompt",
                    len(system_prompt) > 100,
                    f"System prompt length: {len(system_prompt)}",
                )

                # Test escalation strategies
                strategies = agent.get_escalation_strategies()
                self.log_test_result(
                    f"{agent_type.value} - Escalation Strategies",
                    len(strategies) > 0,
                    f"Has {len(strategies)} escalation strategies",
                )

                # Test health check
                health_status = await agent.health_check()
                self.log_test_result(
                    f"{agent_type.value} - Health Check",
                    True,  # Health check completed without error
                    f"Health check completed (status: {health_status})",
                )

            except Exception as e:
                self.log_test_result(
                    f"{agent_type.value} - Properties Test", False, f"Error: {e}"
                )

    async def test_agent_processing(self):
        """Test agent processing of concerns"""
        self.logger.info("🧪 Testing Agent Processing...")

        # Test concerns for different scenarios
        test_concerns = [
            {
                "concern": "My friend hasn't texted me back in 3 hours",
                "category": WorryCategory.SOCIAL,
                "expected_agent": AgentType.INTAKE_SPECIALIST,
            },
            {
                "concern": "I have a weird headache that won't go away",
                "category": WorryCategory.HEALTH,
                "expected_agent": AgentType.CATASTROPHE_ESCALATOR,
            },
            {
                "concern": "I made a mistake at work today",
                "category": WorryCategory.CAREER,
                "expected_agent": AgentType.TIMELINE_PANIC_GENERATOR,
            },
        ]

        for i, test_data in enumerate(test_concerns):
            try:
                # Create user concern
                user_concern = UserConcern(
                    original_worry=test_data["concern"],
                    category=test_data["category"],
                    anxiety_level=AnxietyLevel.MILD,
                    user_id=f"test_user_{i}",
                )

                # Create context
                context = AgentContext(
                    conversation_id=f"test_conv_{i}",
                    user_id=f"test_user_{i}",
                    current_anxiety_level=AnxietyLevel.MILD,
                )

                # Test with appropriate agent
                agent = self.agents[test_data["expected_agent"]]

                # Process concern
                response = await agent.process_concern(user_concern, context)

                # Validate response
                self.log_test_result(
                    f"Process Concern - {test_data['expected_agent'].value}",
                    response is not None and len(response.response) > 0,
                    f"Generated response with {len(response.response)} characters",
                )

                # Check escalation
                self.log_test_result(
                    f"Escalation Level - {test_data['expected_agent'].value}",
                    response.anxiety_escalation >= 1,
                    f"Escalation level: {response.anxiety_escalation}",
                )

                # Check next agent suggestions
                self.log_test_result(
                    f"Next Agent Suggestions - {test_data['expected_agent'].value}",
                    len(response.suggested_next_agents) > 0,
                    f"Suggested {len(response.suggested_next_agents)} next agents",
                )

            except Exception as e:
                self.log_test_result(
                    f"Process Concern - {test_data['expected_agent'].value}",
                    False,
                    f"Error: {e}",
                )

    async def test_communication_protocol(self):
        """Test agent communication protocol"""
        self.logger.info("🧪 Testing Communication Protocol...")

        try:
            # Register agents
            for agent in self.agents.values():
                communication_protocol.register_agent(agent)

            self.log_test_result(
                "Agent Registration",
                len(communication_protocol.agent_registry) >= 3,
                f"Registered {len(communication_protocol.agent_registry)} agents",
            )

            # Test conversation tracking
            communication_protocol.start_conversation(
                self.conversation_id, list(self.agents.values())[0].id, "test_user"
            )

            self.log_test_result(
                "Conversation Tracking",
                self.conversation_id in communication_protocol.active_conversations,
                "Conversation tracking started",
            )

            # Test message creation
            agent1 = list(self.agents.values())[0]
            agent2 = list(self.agents.values())[1]

            test_message = AgentMessage(
                id="test_message_1",
                from_agent=agent1.id,
                to_agent=agent2.id,
                message_type=MessageType.INFORMATION_SHARING,
                content="Test message content",
                conversation_id=self.conversation_id,
            )

            # Test message sending
            success = await communication_protocol.send_message(test_message)
            self.log_test_result(
                "Message Sending", success, "Message sent successfully"
            )

            # Test communication stats
            stats = communication_protocol.get_communication_stats()
            self.log_test_result(
                "Communication Stats",
                stats["total_messages"] > 0,
                f"Total messages: {stats['total_messages']}",
            )

        except Exception as e:
            self.log_test_result("Communication Protocol", False, f"Error: {e}")

    async def test_conversation_flow(self):
        """Test a complete conversation flow"""
        self.logger.info("🧪 Testing Conversation Flow...")

        try:
            # Start with intake specialist
            intake_agent = self.agents[AgentType.INTAKE_SPECIALIST]

            # Create user concern
            user_concern = UserConcern(
                original_worry="I'm worried my friend thinks I'm annoying because they haven't responded to my text",
                category=WorryCategory.SOCIAL,
                anxiety_level=AnxietyLevel.MILD,
                user_id="conversation_test_user",
            )

            # Create context
            context = AgentContext(
                conversation_id="conversation_flow_test",
                user_id="conversation_test_user",
                current_anxiety_level=AnxietyLevel.MILD,
            )

            # Process with intake specialist
            response1 = await intake_agent.process_concern(user_concern, context)
            self.log_test_result(
                "Conversation Flow - Step 1",
                response1 is not None,
                f"Intake specialist response: {len(response1.response)} chars",
            )

            # Get next agent suggestion
            next_agent_type = (
                response1.suggested_next_agents[0]
                if response1.suggested_next_agents
                else None
            )

            if next_agent_type:
                # Find the next agent
                next_agent = None
                for agent in self.agents.values():
                    if agent.agent_type.value == next_agent_type:
                        next_agent = agent
                        break

                if next_agent:
                    # Process with next agent
                    response2 = await next_agent.process_concern(user_concern, context)
                    self.log_test_result(
                        "Conversation Flow - Step 2",
                        response2 is not None,
                        f"Second agent ({next_agent_type}) response: {len(response2.response)} chars",
                    )

                    # Check escalation
                    self.log_test_result(
                        "Conversation Flow - Escalation",
                        response2.anxiety_escalation >= response1.anxiety_escalation,
                        f"Escalation: {response1.anxiety_escalation} -> {response2.anxiety_escalation}",
                    )
                else:
                    self.log_test_result(
                        "Conversation Flow - Next Agent",
                        False,
                        f"Next agent {next_agent_type} not found",
                    )
            else:
                self.log_test_result(
                    "Conversation Flow - Next Agent", False, "No next agent suggested"
                )

        except Exception as e:
            self.log_test_result("Conversation Flow", False, f"Error: {e}")

    async def test_agent_specializations(self):
        """Test agent-specific specializations"""
        self.logger.info("🧪 Testing Agent Specializations...")

        # Test Intake Specialist specific features
        if AgentType.INTAKE_SPECIALIST in self.agents:
            try:
                agent = self.agents[AgentType.INTAKE_SPECIALIST]

                # Test conversation starters
                starters = agent.get_conversation_starters()
                self.log_test_result(
                    "Intake Specialist - Conversation Starters",
                    len(starters) > 0,
                    f"Has {len(starters)} conversation starters",
                )

                # Test readiness analysis
                readiness = agent.analyze_conversation_readiness(
                    ["Hello", "I'm worried about my friend"]
                )
                self.log_test_result(
                    "Intake Specialist - Readiness Analysis",
                    "ready_for_handoff" in readiness,
                    "Readiness analysis completed",
                )

            except Exception as e:
                self.log_test_result(
                    "Intake Specialist Specializations", False, f"Error: {e}"
                )

        # Test Catastrophe Escalator specific features
        if AgentType.CATASTROPHE_ESCALATOR in self.agents:
            try:
                agent = self.agents[AgentType.CATASTROPHE_ESCALATOR]

                # Test signature phrases
                phrases = agent.get_signature_phrases()
                self.log_test_result(
                    "Catastrophe Escalator - Signature Phrases",
                    len(phrases) > 0,
                    f"Has {len(phrases)} signature phrases",
                )

            except Exception as e:
                self.log_test_result(
                    "Catastrophe Escalator Specializations", False, f"Error: {e}"
                )

        # Test Timeline Panic Generator specific features
        if AgentType.TIMELINE_PANIC_GENERATOR in self.agents:
            try:
                agent = self.agents[AgentType.TIMELINE_PANIC_GENERATOR]

                # Test signature phrases
                phrases = agent.get_signature_phrases()
                self.log_test_result(
                    "Timeline Panic Generator - Signature Phrases",
                    len(phrases) > 0,
                    f"Has {len(phrases)} signature phrases",
                )

                # Test countdown message
                countdown = agent.generate_countdown_message(5)
                self.log_test_result(
                    "Timeline Panic Generator - Countdown Message",
                    len(countdown) > 0,
                    "Generated countdown message",
                )

            except Exception as e:
                self.log_test_result(
                    "Timeline Panic Generator Specializations", False, f"Error: {e}"
                )

    def print_test_summary(self):
        """Print summary of all tests"""
        print("\n" + "=" * 80)
        print("🧪 WEEK 2 TESTING SUMMARY")
        print("=" * 80)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: ✅ {passed_tests}")
        print(f"Failed: ❌ {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")

        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test_name']}: {result['message']}")

        print("\n" + "=" * 80)

        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Week 2 implementation is ready!")
        elif passed_tests >= total_tests * 0.8:
            print("🎯 MOSTLY SUCCESSFUL! Week 2 implementation is nearly complete.")
        else:
            print("⚠️  NEEDS WORK! Several issues need to be addressed.")

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Week 2 Implementation Tests...")
        print("=" * 80)

        # Run tests
        self.test_agent_creation()
        await self.test_agent_properties()
        await self.test_agent_processing()
        await self.test_communication_protocol()
        await self.test_conversation_flow()
        await self.test_agent_specializations()

        # Print summary
        self.print_test_summary()


async def main():
    """Main test runner"""
    tester = Week2Tester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
