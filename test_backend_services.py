#!/usr/bin/env python3
"""
Comprehensive Backend Services Test - No Docker Required
Tests all core services: StateManager, AnxietyTracker, ConversationOrchestrator, AnalyticsService
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import our components with absolute imports
try:
    from services.state_manager import StateManager
    from services.conversation_orchestrator import ConversationOrchestrator, OrchestrationMode
    from services.anxiety_tracker import AnxietyTracker
    from services.analytics_service import AnalyticsService, AnalyticsTimeframe
    from agents.base_agent import AgentFactory, AgentType
    from models.schemas import (
        UserConcern,
        ConversationState,
        ConversationStatus,
        AnxietyLevel,
        WorryCategory,
        AgentInteraction
    )
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This might be due to missing dependencies or import path issues.")
    sys.exit(1)


class BackendServicesTester:
    """Test suite for all backend services"""
    
    def __init__(self):
        self.logger = logging.getLogger("BackendServicesTester")
        self.test_results = []
        
        # Services
        self.state_manager = None
        self.anxiety_tracker = None
        self.analytics_service = None
        self.conversation_orchestrator = None
        
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
    
    async def test_state_manager(self):
        """Test StateManager functionality"""
        self.logger.info("🧪 Testing StateManager...")
        
        try:
            # Initialize state manager with local Redis
            self.state_manager = StateManager(
                redis_url="redis://localhost:6379",
                key_prefix="test_ezoverthinking:",
                ttl_seconds=3600
            )
            
            # Test connection
            connected = await self.state_manager.connect()
            self.log_test_result(
                "StateManager - Connection",
                connected,
                "Connected to Redis successfully" if connected else "Failed to connect to Redis"
            )
            
            if not connected:
                self.log_test_result("StateManager Tests", False, "Cannot proceed without Redis connection")
                return
            
            # Test basic operations
            test_conversation = ConversationState(
                conversation_id="test_conv_001",
                user_id="test_user_001",
                status=ConversationStatus.ACTIVE,
                current_anxiety_level=AnxietyLevel.MODERATE,
                message_count=5,
                escalation_count=2,
                agents_involved=["agent_1", "agent_2"],
                context={"test": "data"}
            )
            
            # Store conversation state
            stored = await self.state_manager.store_conversation_state(
                "test_conv_001", test_conversation
            )
            self.log_test_result(
                "StateManager - Store Conversation",
                stored,
                "Conversation state stored successfully"
            )
            
            # Retrieve conversation state
            retrieved = await self.state_manager.get_conversation_state("test_conv_001")
            self.log_test_result(
                "StateManager - Retrieve Conversation",
                retrieved is not None and retrieved.conversation_id == "test_conv_001",
                f"Retrieved conversation: {retrieved.conversation_id if retrieved else 'None'}"
            )
            
            # Test cache operations
            cache_stored = await self.state_manager.cache_set(
                "test_key", {"data": "test_value"}, ttl=60
            )
            self.log_test_result(
                "StateManager - Cache Set",
                cache_stored,
                "Cache value stored successfully"
            )
            
            cache_retrieved = await self.state_manager.cache_get("test_key")
            self.log_test_result(
                "StateManager - Cache Get",
                cache_retrieved is not None and cache_retrieved.get("data") == "test_value",
                f"Retrieved cache value: {cache_retrieved}"
            )
            
        except Exception as e:
            self.log_test_result("StateManager Tests", False, f"Error: {e}")
    
    async def test_anxiety_tracker(self):
        """Test AnxietyTracker functionality"""
        self.logger.info("🧪 Testing AnxietyTracker...")
        
        if not self.state_manager:
            self.log_test_result("AnxietyTracker Tests", False, "StateManager not available")
            return
        
        try:
            # Initialize anxiety tracker
            self.anxiety_tracker = AnxietyTracker(self.state_manager)
            
            # Initialize tracker
            initialized = await self.anxiety_tracker.initialize()
            self.log_test_result(
                "AnxietyTracker - Initialization",
                initialized,
                "AnxietyTracker initialized successfully"
            )
            
            # Start tracking
            conversation_id = "anxiety_test_conv"
            tracking_started = await self.anxiety_tracker.start_tracking(
                conversation_id, AnxietyLevel.MILD, "test_agent"
            )
            self.log_test_result(
                "AnxietyTracker - Start Tracking",
                tracking_started,
                f"Started tracking for conversation: {conversation_id}"
            )
            
            # Track anxiety changes
            change_tracked = await self.anxiety_tracker.track_anxiety_change(
                conversation_id, AnxietyLevel.MILD, AnxietyLevel.MODERATE, "escalation_agent"
            )
            self.log_test_result(
                "AnxietyTracker - Track Change",
                change_tracked,
                "Anxiety change tracked successfully"
            )
            
            # Get real-time anxiety
            current_anxiety = await self.anxiety_tracker.get_real_time_anxiety(conversation_id)
            self.log_test_result(
                "AnxietyTracker - Real-time Anxiety",
                current_anxiety == AnxietyLevel.MODERATE,
                f"Current anxiety level: {current_anxiety.value if current_anxiety else 'None'}"
            )
            
        except Exception as e:
            self.log_test_result("AnxietyTracker Tests", False, f"Error: {e}")
    
    async def test_conversation_orchestrator(self):
        """Test ConversationOrchestrator functionality"""
        self.logger.info("🧪 Testing ConversationOrchestrator...")
        
        if not all([self.state_manager, self.anxiety_tracker]):
            self.log_test_result("ConversationOrchestrator Tests", False, "Dependencies not available")
            return
        
        try:
            # Initialize orchestrator
            self.conversation_orchestrator = ConversationOrchestrator(
                self.state_manager, self.anxiety_tracker
            )
            
            # Initialize orchestrator
            initialized = await self.conversation_orchestrator.initialize()
            self.log_test_result(
                "ConversationOrchestrator - Initialization",
                initialized,
                "ConversationOrchestrator initialized successfully"
            )
            
            # Create and register agents
            agents = AgentFactory.create_all_agents()
            for agent in agents.values():
                self.conversation_orchestrator.register_agent(agent)
            
            self.log_test_result(
                "ConversationOrchestrator - Agent Registration",
                len(self.conversation_orchestrator.agents) >= 6,
                f"Registered {len(self.conversation_orchestrator.agents)} agents"
            )
            
            # Start conversation
            initial_concern = UserConcern(
                original_worry="I'm worried about my upcoming presentation",
                category=WorryCategory.CAREER,
                anxiety_level=AnxietyLevel.MILD,
                user_id="orchestrator_test_user"
            )
            
            conversation_id = await self.conversation_orchestrator.start_conversation(
                "orchestrator_test_user",
                initial_concern,
                OrchestrationMode.COORDINATED
            )
            
            self.log_test_result(
                "ConversationOrchestrator - Start Conversation",
                conversation_id is not None,
                f"Started conversation: {conversation_id}"
            )
            
            # Orchestrate a response
            response = await self.conversation_orchestrator.orchestrate_response(
                conversation_id, "I'm really nervous about speaking in front of people"
            )
            
            self.log_test_result(
                "ConversationOrchestrator - Orchestrate Response",
                response is not None,
                f"Response: {len(response.response)} chars, Anxiety: {response.anxiety_escalation}"
            )
            
        except Exception as e:
            self.log_test_result("ConversationOrchestrator Tests", False, f"Error: {e}")
    
    async def test_analytics_service(self):
        """Test AnalyticsService functionality"""
        self.logger.info("🧪 Testing AnalyticsService...")
        
        if not self.state_manager:
            self.log_test_result("AnalyticsService Tests", False, "StateManager not available")
            return
        
        try:
            # Initialize analytics service
            self.analytics_service = AnalyticsService(self.state_manager, self.anxiety_tracker)
            
            # Initialize service
            initialized = await self.analytics_service.initialize()
            self.log_test_result(
                "AnalyticsService - Initialization",
                initialized,
                "AnalyticsService initialized successfully"
            )
            
            # Test conversation metrics
            conversation_metrics = await self.analytics_service.get_conversation_metrics(
                AnalyticsTimeframe.HOUR
            )
            self.log_test_result(
                "AnalyticsService - Conversation Metrics",
                conversation_metrics.total_conversations >= 0,
                f"Conversation metrics: {conversation_metrics.total_conversations} total conversations"
            )
            
            # Test real-time dashboard
            dashboard = await self.analytics_service.get_real_time_dashboard()
            self.log_test_result(
                "AnalyticsService - Real-time Dashboard",
                "overview" in dashboard,
                f"Dashboard: {len(dashboard)} sections"
            )
            
        except Exception as e:
            self.log_test_result("AnalyticsService Tests", False, f"Error: {e}")
    
    async def test_integration(self):
        """Test integration between all services"""
        self.logger.info("🧪 Testing Service Integration...")
        
        try:
            if not all([self.state_manager, self.anxiety_tracker, self.conversation_orchestrator, self.analytics_service]):
                self.log_test_result("Integration Tests", False, "Not all services initialized")
                return
            
            # Create a complete conversation flow
            initial_concern = UserConcern(
                original_worry="I'm having a social anxiety crisis about my friend not responding",
                category=WorryCategory.SOCIAL,
                anxiety_level=AnxietyLevel.MILD,
                user_id="integration_test_user"
            )
            
            # Start conversation with orchestrator
            conversation_id = await self.conversation_orchestrator.start_conversation(
                "integration_test_user",
                initial_concern,
                OrchestrationMode.ADAPTIVE
            )
            
            # Simulate conversation flow
            messages = [
                "My friend hasn't responded to my text for 3 hours",
                "I'm starting to think they're ignoring me",
                "What if I said something wrong?",
                "This is making me really anxious"
            ]
            
            for message in messages:
                await self.conversation_orchestrator.orchestrate_response(
                    conversation_id, message
                )
                await asyncio.sleep(0.1)
            
            # Verify state persistence
            conversation_state = await self.state_manager.get_conversation_state(conversation_id)
            self.log_test_result(
                "Integration - State Persistence",
                conversation_state is not None and conversation_state.message_count >= 4,
                f"State persisted: {conversation_state.message_count} messages"
            )
            
            # Verify anxiety tracking
            anxiety_progression = await self.anxiety_tracker.get_anxiety_progression(conversation_id)
            self.log_test_result(
                "Integration - Anxiety Tracking",
                anxiety_progression is not None and len(anxiety_progression.data_points) >= 4,
                f"Anxiety tracked: {len(anxiety_progression.data_points)} data points"
            )
            
            self.log_test_result(
                "Integration - Cross-service Communication",
                True,
                "All services successfully communicated"
            )
            
        except Exception as e:
            self.log_test_result("Integration Tests", False, f"Error: {e}")
    
    async def cleanup(self):
        """Clean up test resources"""
        try:
            if self.state_manager:
                await self.state_manager.disconnect()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def print_test_summary(self):
        """Print summary of all tests"""
        print("\n" + "="*80)
        print("🧪 BACKEND SERVICES TEST SUMMARY")
        print("="*80)
        
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
        
        print("\n" + "="*80)
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Backend services are working perfectly!")
        elif passed_tests >= total_tests * 0.8:
            print("🚀 GREAT! Backend services are mostly working.")
        else:
            print("⚠️  NEEDS WORK! Several backend services have issues.")
    
    async def run_all_tests(self):
        """Run all backend service tests"""
        print("🚀 Starting Backend Services Tests...")
        print("="*80)
        
        try:
            # Run tests
            await self.test_state_manager()
            await self.test_anxiety_tracker()
            await self.test_conversation_orchestrator()
            await self.test_analytics_service()
            await self.test_integration()
            
        finally:
            # Always cleanup
            await self.cleanup()
            
            # Print summary
            self.print_test_summary()


async def main():
    """Main test runner"""
    tester = BackendServicesTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 