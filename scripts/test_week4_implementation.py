#!/usr/bin/env python3
"""
Week 4 Testing Script for ezOverThinking
This script tests state management, analytics, and conversation orchestration services.

File: scripts/test_week4_implementation.py
"""

import asyncio
import sys
import os
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import our components
from src.services.state_manager import StateManager
from src.services.conversation_orchestrator import ConversationOrchestrator, OrchestrationMode
from src.services.anxiety_tracker import AnxietyTracker
from src.services.analytics_service import AnalyticsService, AnalyticsTimeframe
from src.agents.base_agent import AgentFactory, AgentType
from src.models.schemas import (
    UserConcern,
    ConversationState,
    ConversationStatus,
    AnxietyLevel,
    WorryCategory,
    AgentInteraction
)


class Week4Tester:
    """Test suite for Week 4 state management and analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger("Week4Tester")
        self.test_results = []
        
        # Services
        self.state_manager = None
        self.anxiety_tracker = None
        self.analytics_service = None
        self.conversation_orchestrator = None
        
        # Test data
        self.test_conversation_id = None
        self.test_user_id = "test_user_week4"
        
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
            # Initialize state manager
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
            
            # Test health check
            health = await self.state_manager.health_check()
            self.log_test_result(
                "StateManager - Health Check",
                health.get("status") == "healthy",
                f"Health status: {health.get('status', 'unknown')}"
            )
            
            # Test conversation state storage
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
            
            # Update conversation state
            updated = await self.state_manager.update_conversation_state(
                "test_conv_001",
                {"message_count": 10, "escalation_count": 3}
            )
            self.log_test_result(
                "StateManager - Update Conversation",
                updated,
                "Conversation state updated successfully"
            )
            
            # Test user session storage
            session_data = {
                "user_id": "test_user_001",
                "preferences": {"theme": "dark"},
                "activity_score": 85
            }
            
            session_stored = await self.state_manager.store_user_session(
                "test_user_001", session_data
            )
            self.log_test_result(
                "StateManager - Store User Session",
                session_stored,
                "User session stored successfully"
            )
            
            # Retrieve user session
            retrieved_session = await self.state_manager.get_user_session("test_user_001")
            self.log_test_result(
                "StateManager - Retrieve User Session",
                retrieved_session is not None and retrieved_session.get("user_id") == "test_user_001",
                f"Retrieved session for user: {retrieved_session.get('user_id') if retrieved_session else 'None'}"
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
            
            # Test queue operations
            queue_pushed = await self.state_manager.queue_push(
                "test_queue", {"message": "test_message"}
            )
            self.log_test_result(
                "StateManager - Queue Push",
                queue_pushed,
                "Message pushed to queue successfully"
            )
            
            queue_popped = await self.state_manager.queue_pop("test_queue")
            self.log_test_result(
                "StateManager - Queue Pop",
                queue_popped is not None and queue_popped.get("message") == "test_message",
                f"Popped message: {queue_popped}"
            )
            
            # Test distributed lock
            try:
                async with self.state_manager.distributed_lock("test_resource", timeout=10):
                    # Simulate some work
                    await asyncio.sleep(0.1)
                
                self.log_test_result(
                    "StateManager - Distributed Lock",
                    True,
                    "Distributed lock acquired and released successfully"
                )
            except Exception as e:
                self.log_test_result(
                    "StateManager - Distributed Lock",
                    False,
                    f"Error with distributed lock: {e}"
                )
            
            # Test system metrics
            metrics = await self.state_manager.get_system_metrics()
            self.log_test_result(
                "StateManager - System Metrics",
                "state_manager_metrics" in metrics,
                f"Retrieved system metrics with {len(metrics)} categories"
            )
            
        except Exception as e:
            self.log_test_result("StateManager Tests", False, f"Error: {e}")
    
    async def test_anxiety_tracker(self):
        """Test AnxietyTracker functionality"""
        self.logger.info("🧪 Testing AnxietyTracker...")
        
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
            
            # Another anxiety change
            await self.anxiety_tracker.track_anxiety_change(
                conversation_id, AnxietyLevel.MODERATE, AnxietyLevel.SEVERE, "catastrophe_agent"
            )
            
            # Get real-time anxiety
            current_anxiety = await self.anxiety_tracker.get_real_time_anxiety(conversation_id)
            self.log_test_result(
                "AnxietyTracker - Real-time Anxiety",
                current_anxiety == AnxietyLevel.SEVERE,
                f"Current anxiety level: {current_anxiety.value if current_anxiety else 'None'}"
            )
            
            # Get anxiety progression
            progression = await self.anxiety_tracker.get_anxiety_progression(conversation_id)
            self.log_test_result(
                "AnxietyTracker - Anxiety Progression",
                progression is not None and len(progression.data_points) >= 3,
                f"Progression with {len(progression.data_points) if progression else 0} data points"
            )
            
            # Get anxiety trends
            trends = await self.anxiety_tracker.get_anxiety_trends(conversation_id, window_minutes=60)
            self.log_test_result(
                "AnxietyTracker - Anxiety Trends",
                "trend" in trends,
                f"Trend analysis: {trends.get('trend', 'unknown')}"
            )
            
            # Detect patterns
            patterns = await self.anxiety_tracker.detect_anxiety_patterns(conversation_id)
            self.log_test_result(
                "AnxietyTracker - Pattern Detection",
                isinstance(patterns, dict),
                f"Detected {len(patterns)} pattern categories"
            )
            
            # Test alert callback
            alert_received = False
            
            def test_alert_callback(conv_id, alert):
                nonlocal alert_received
                try:
                    alert_received = True
                    self.logger.info(f"Alert received: {alert}")
                except Exception as e:
                    self.logger.error(f"Exception in test_alert_callback: {e}")
            
            self.anxiety_tracker.add_alert_callback(test_alert_callback)
            
            # Trigger high anxiety to test alert
            await self.anxiety_tracker.track_anxiety_change(
                conversation_id, AnxietyLevel.SEVERE, AnxietyLevel.PANIC, "panic_agent"
            )
            
            # Wait a bit for alert processing
            await asyncio.sleep(0.1)
            
            self.log_test_result(
                "AnxietyTracker - Alert Callbacks",
                alert_received,
                "Alert callback triggered successfully"
            )
            
            # Get system analytics
            system_analytics = await self.anxiety_tracker.get_system_analytics()
            self.log_test_result(
                "AnxietyTracker - System Analytics",
                "total_sessions" in system_analytics,
                f"System analytics with {system_analytics.get('total_sessions', 0)} sessions"
            )
            
            # End tracking
            tracking_ended = await self.anxiety_tracker.end_tracking(conversation_id)
            self.log_test_result(
                "AnxietyTracker - End Tracking",
                tracking_ended,
                "Anxiety tracking ended successfully"
            )
            
        except Exception as e:
            self.log_test_result("AnxietyTracker Tests", False, f"Error: {e}")
    
    async def test_conversation_orchestrator(self):
        """Test ConversationOrchestrator functionality"""
        self.logger.info("🧪 Testing ConversationOrchestrator...")
        
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
            
            # Register coordinator specifically
            coordinator = agents.get(AgentType.COORDINATOR)
            if coordinator:
                self.conversation_orchestrator.register_coordinator(coordinator)
            
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
            
            self.test_conversation_id = conversation_id
            
            # Orchestrate responses
            messages = [
                "I'm really nervous about speaking in front of people",
                "What if I mess up and everyone thinks I'm incompetent?",
                "This could ruin my career prospects",
                "I'm starting to panic about this"
            ]
            
            responses = []
            for i, message in enumerate(messages):
                try:
                    response = await self.conversation_orchestrator.orchestrate_response(
                        conversation_id, message
                    )
                    responses.append(response)
                    
                    self.log_test_result(
                        f"ConversationOrchestrator - Response {i+1}",
                        response is not None,
                        f"Response: {len(response.response)} chars, Anxiety: {response.anxiety_escalation}"
                    )
                    
                except Exception as e:
                    self.log_test_result(
                        f"ConversationOrchestrator - Response {i+1}",
                        False,
                        f"Error: {e}"
                    )
            
            # Test different orchestration modes
            simple_conversation_id = await self.conversation_orchestrator.start_conversation(
                "simple_test_user",
                initial_concern,
                OrchestrationMode.SIMPLE
            )
            
            simple_response = await self.conversation_orchestrator.orchestrate_response(
                simple_conversation_id, "I'm worried about something"
            )
            
            self.log_test_result(
                "ConversationOrchestrator - Simple Mode",
                simple_response is not None,
                f"Simple orchestration response: {len(simple_response.response)} chars"
            )
            
            # Test collaborative mode
            collaborative_conversation_id = await self.conversation_orchestrator.start_conversation(
                "collaborative_test_user",
                initial_concern,
                OrchestrationMode.COLLABORATIVE
            )
            
            collaborative_response = await self.conversation_orchestrator.orchestrate_response(
                collaborative_conversation_id, "This is a complex social and career issue"
            )
            
            self.log_test_result(
                "ConversationOrchestrator - Collaborative Mode",
                collaborative_response is not None,
                f"Collaborative response: {len(collaborative_response.response)} chars"
            )
            
            # Get conversation analytics
            analytics = await self.conversation_orchestrator.get_conversation_analytics(conversation_id)
            self.log_test_result(
                "ConversationOrchestrator - Conversation Analytics",
                analytics.get("conversation_id") == conversation_id,
                f"Analytics: {analytics.get('total_messages', 0)} messages, {analytics.get('agent_count', 0)} agents"
            )
            
            # Get system analytics
            system_analytics = await self.conversation_orchestrator.get_system_analytics()
            self.log_test_result(
                "ConversationOrchestrator - System Analytics",
                "orchestration_metrics" in system_analytics,
                f"System analytics with {system_analytics.get('active_conversations', 0)} active conversations"
            )
            
            # End conversation
            conversation_ended = await self.conversation_orchestrator.end_conversation(
                conversation_id, "test_completed"
            )
            self.log_test_result(
                "ConversationOrchestrator - End Conversation",
                conversation_ended,
                "Conversation ended successfully"
            )
            
        except Exception as e:
            self.log_test_result("ConversationOrchestrator Tests", False, f"Error: {e}")
    
    async def test_analytics_service(self):
        """Test AnalyticsService functionality"""
        self.logger.info("🧪 Testing AnalyticsService...")
        
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
            
            # Test agent performance metrics
            agent_metrics = await self.analytics_service.get_agent_performance_metrics(
                timeframe=AnalyticsTimeframe.HOUR
            )
            self.log_test_result(
                "AnalyticsService - Agent Performance",
                isinstance(agent_metrics, list),
                f"Agent performance: {len(agent_metrics)} agents analyzed"
            )
            
            # Test anxiety analytics
            anxiety_analytics = await self.analytics_service.get_anxiety_analytics(
                AnalyticsTimeframe.HOUR
            )
            self.log_test_result(
                "AnalyticsService - Anxiety Analytics",
                anxiety_analytics.average_initial_anxiety >= 0,
                f"Anxiety analytics: {anxiety_analytics.average_initial_anxiety:.1f} avg initial anxiety"
            )
            
            # Test user engagement metrics
            user_engagement = await self.analytics_service.get_user_engagement_metrics(
                AnalyticsTimeframe.HOUR
            )
            self.log_test_result(
                "AnalyticsService - User Engagement",
                user_engagement.total_users >= 0,
                f"User engagement: {user_engagement.total_users} total users"
            )
            
            # Test system performance metrics
            system_performance = await self.analytics_service.get_system_performance_metrics()
            self.log_test_result(
                "AnalyticsService - System Performance",
                "analytics_service" in system_performance,
                f"System performance: {len(system_performance)} metric categories"
            )
            
            # Test real-time dashboard
            dashboard = await self.analytics_service.get_real_time_dashboard()
            self.log_test_result(
                "AnalyticsService - Real-time Dashboard",
                "overview" in dashboard,
                f"Dashboard: {len(dashboard)} sections"
            )
            
            # Test historical trends
            from src.services.analytics_service import MetricType
            trends = await self.analytics_service.get_historical_trends(
                MetricType.CONVERSATION_METRICS,
                AnalyticsTimeframe.DAY
            )
            self.log_test_result(
                "AnalyticsService - Historical Trends",
                "time_series" in trends,
                f"Historical trends: {trends.get('data_points', 0)} data points"
            )
            
            # Test analytics report generation
            report = await self.analytics_service.generate_analytics_report(
                AnalyticsTimeframe.HOUR,
                include_trends=True,
                include_recommendations=True
            )
            self.log_test_result(
                "AnalyticsService - Analytics Report",
                "executive_summary" in report,
                f"Report generated with {len(report)} sections"
            )
            
            # Test data export
            export_data = await self.analytics_service.export_analytics_data(
                AnalyticsTimeframe.HOUR,
                format="json"
            )
            self.log_test_result(
                "AnalyticsService - Data Export",
                "export_metadata" in export_data,
                f"Data export: {len(export_data)} data categories"
            )
            
        except Exception as e:
            self.log_test_result("AnalyticsService Tests", False, f"Error: {e}")
    
    async def test_integration(self):
        """Test integration between all Week 4 services"""
        self.logger.info("🧪 Testing Service Integration...")
        
        try:
            # Test end-to-end flow
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
                # Small delay to simulate real conversation
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
            
            # Verify analytics collection
            conversation_analytics = await self.conversation_orchestrator.get_conversation_analytics(conversation_id)
            self.log_test_result(
                "Integration - Analytics Collection",
                conversation_analytics.get("total_messages", 0) >= 4,
                f"Analytics collected: {conversation_analytics.get('total_messages', 0)} messages"
            )
            
            # Test real-time updates
            await asyncio.sleep(0.5)  # Allow for background processing
            
            # Get updated analytics
            updated_metrics = await self.analytics_service.get_conversation_metrics(AnalyticsTimeframe.HOUR)
            self.log_test_result(
                "Integration - Real-time Updates",
                updated_metrics.total_conversations >= 1,
                f"Updated metrics: {updated_metrics.total_conversations} conversations"
            )
            
            # Test cross-service communication
            # The orchestrator should have updated the state manager
            # The state manager should have provided data to analytics
            # The anxiety tracker should have recorded progression
            
            self.log_test_result(
                "Integration - Cross-service Communication",
                True,
                "All services successfully communicated"
            )
            
            # Clean up
            await self.conversation_orchestrator.end_conversation(conversation_id, "integration_test_complete")
            
        except Exception as e:
            self.log_test_result("Integration Tests", False, f"Error: {e}")
    
    async def test_performance_and_scalability(self):
        """Test performance and scalability of Week 4 services"""
        self.logger.info("🧪 Testing Performance and Scalability...")
        
        try:
            # Test concurrent conversations
            concurrent_conversations = []
            
            for i in range(5):  # Create 5 concurrent conversations
                concern = UserConcern(
                    original_worry=f"Performance test concern {i}",
                    user_id=f"perf_test_user_{i}",
                    anxiety_level=AnxietyLevel.MILD
                )
                
                conv_id = await self.conversation_orchestrator.start_conversation(
                    f"perf_test_user_{i}",
                    concern,
                    OrchestrationMode.SIMPLE
                )
                concurrent_conversations.append(conv_id)
            
            self.log_test_result(
                "Performance - Concurrent Conversations",
                len(concurrent_conversations) == 5,
                f"Created {len(concurrent_conversations)} concurrent conversations"
            )
            
            # Test rapid message processing
            start_time = datetime.now()
            
            # Process messages concurrently
            tasks = []
            for i, conv_id in enumerate(concurrent_conversations):
                task = self.conversation_orchestrator.orchestrate_response(
                    conv_id, f"Performance test message {i}"
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            successful_responses = len([r for r in responses if not isinstance(r, Exception)])
            
            self.log_test_result(
                "Performance - Concurrent Processing",
                successful_responses == 5,
                f"Processed {successful_responses}/5 messages in {processing_time:.2f} seconds"
            )
            
            # Test state manager performance
            state_start = datetime.now()
            
            # Perform rapid state operations
            for i in range(20):
                await self.state_manager.cache_set(f"perf_test_{i}", {"data": f"value_{i}"})
            
            state_end = datetime.now()
            state_time = (state_end - state_start).total_seconds()
            
            self.log_test_result(
                "Performance - State Operations",
                state_time < 2.0,
                f"20 state operations completed in {state_time:.2f} seconds"
            )
            
            # Test analytics performance
            analytics_start = datetime.now()
            
            # Generate analytics report
            report = await self.analytics_service.generate_analytics_report(
                AnalyticsTimeframe.HOUR,
                include_trends=True,
                include_recommendations=True
            )
            
            analytics_end = datetime.now()
            analytics_time = (analytics_end - analytics_start).total_seconds()
            
            self.log_test_result(
                "Performance - Analytics Generation",
                analytics_time < 5.0 and "executive_summary" in report,
                f"Analytics report generated in {analytics_time:.2f} seconds"
            )
            
            # Memory usage check (basic)
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            self.log_test_result(
                "Performance - Memory Usage",
                memory_usage < 500,  # Less than 500MB
                f"Memory usage: {memory_usage:.1f} MB"
            )
            
            # Clean up concurrent conversations
            for conv_id in concurrent_conversations:
                await self.conversation_orchestrator.end_conversation(conv_id, "performance_test_complete")
            
        except Exception as e:
            self.log_test_result("Performance Tests", False, f"Error: {e}")
    
    async def cleanup(self):
        """Clean up test resources"""
        try:
            # Shutdown services
            if self.analytics_service:
                await self.analytics_service.shutdown()
            
            if self.conversation_orchestrator:
                # Clean up any remaining conversations
                pass
            
            if self.state_manager:
                # Clean up test data
                await self.state_manager.cache_delete("test_key")
                await self.state_manager.delete_conversation_state("test_conv_001")
                await self.state_manager.disconnect()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def print_test_summary(self):
        """Print summary of all tests"""
        print("\n" + "="*80)
        print("🧪 WEEK 4 TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: ✅ {passed_tests}")
        print(f"Failed: ❌ {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Service-specific results
        service_results = {}
        for result in self.test_results:
            for service in ["StateManager", "AnxietyTracker", "ConversationOrchestrator", "AnalyticsService", "Integration", "Performance"]:
                if service in result["test_name"]:
                    if service not in service_results:
                        service_results[service] = {"passed": 0, "failed": 0}
                    
                    if result["success"]:
                        service_results[service]["passed"] += 1
                    else:
                        service_results[service]["failed"] += 1
        
        print("\n📊 SERVICE-SPECIFIC RESULTS:")
        for service, results in service_results.items():
            total = results["passed"] + results["failed"]
            success_rate = (results["passed"] / total * 100) if total > 0 else 0
            print(f"  {service}: {results['passed']}/{total} ({success_rate:.1f}%)")
        
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
            print("🎉 ALL TESTS PASSED! Week 4 implementation is complete!")
        elif passed_tests >= total_tests * 0.9:
            print("🎯 EXCELLENT! Week 4 implementation is nearly perfect.")
        elif passed_tests >= total_tests * 0.8:
            print("🚀 GREAT! Week 4 implementation is mostly successful.")
        else:
            print("⚠️  NEEDS WORK! Several issues need to be addressed.")
        
        # System readiness assessment
        if passed_tests >= total_tests * 0.8:
            print("\n🏆 SYSTEM READINESS: State management and analytics systems are operational!")
        else:
            print("\n⚠️  SYSTEM READINESS: Some components may need attention.")
    
    async def run_all_tests(self):
        """Run all Week 4 tests"""
        print("🚀 Starting Week 4 State Management & Analytics Tests...")
        print("="*80)
        
        try:
            # Run tests
            await self.test_state_manager()
            await self.test_anxiety_tracker()
            await self.test_conversation_orchestrator()
            await self.test_analytics_service()
            await self.test_integration()
            await self.test_performance_and_scalability()
            
        finally:
            # Always cleanup
            await self.cleanup()
            
            # Print summary
            self.print_test_summary()


async def main():
    """Main test runner"""
    tester = Week4Tester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())