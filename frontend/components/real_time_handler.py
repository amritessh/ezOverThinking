# frontend/components/real_time_handler.py
"""
Real-time Handler - WebSocket communication for live chat
"""

import streamlit as st
import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class RealTimeHandler:
    """Handle real-time WebSocket communication with the backend"""

    def __init__(self):
        self.websocket = None
        self.connected = False
        self.connection_thread = None
        self.message_callbacks = []
        self.retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5  # seconds

        # Initialize connection state
        self.initialize_state()

    def initialize_state(self):
        """Initialize WebSocket state in session"""
        if "websocket_connected" not in st.session_state:
            st.session_state.websocket_connected = False

        if "websocket_messages" not in st.session_state:
            st.session_state.websocket_messages = []

        if "connection_status" not in st.session_state:
            st.session_state.connection_status = "disconnected"

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        if "typing_indicator" not in st.session_state:
            st.session_state.typing_indicator = False

        if "current_anxiety_level" not in st.session_state:
            st.session_state.current_anxiety_level = "calm"

    def initialize_connection(self):
        """Initialize WebSocket connection in a separate thread"""
        if not self.connected and not self.connection_thread:
            self.connection_thread = threading.Thread(
                target=self._connection_worker, daemon=True
            )
            self.connection_thread.start()

    def _connection_worker(self):
        """Worker thread for WebSocket connection"""
        asyncio.run(self._manage_connection())

    async def _manage_connection(self):
        """Manage WebSocket connection with automatic reconnection"""
        while self.retry_count < self.max_retries:
            try:
                await self._connect_websocket()
                self.retry_count = 0  # Reset on successful connection
                await self._listen_for_messages()

            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                self.connected = False
                st.session_state.websocket_connected = False
                st.session_state.connection_status = "error"

                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    logger.info(
                        f"Retrying connection in {self.retry_delay} seconds... (attempt {self.retry_count})"
                    )
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached. WebSocket connection failed.")
                    st.session_state.connection_status = "failed"
                    break

    async def _connect_websocket(self):
        """Connect to WebSocket server"""
        try:
            # Get WebSocket URL from API client
            try:
                from utils.api_client import get_api_client

                api_client = get_api_client()
                ws_url = api_client.get_websocket_url()
            except ImportError:
                # Fallback to default WebSocket URL
                ws_url = "ws://localhost:8000/ws"

            logger.info(f"Connecting to WebSocket: {ws_url}")

            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url, ping_interval=20, ping_timeout=10, close_timeout=10
            )

            self.connected = True
            st.session_state.websocket_connected = True
            st.session_state.connection_status = "connected"

            logger.info("✅ WebSocket connected successfully")

        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            # Simulate connection for demo purposes
            self._simulate_connection()

    def _simulate_connection(self):
        """Simulate WebSocket connection for demo purposes"""
        logger.info("🔄 Simulating WebSocket connection for demo...")
        self.connected = True
        st.session_state.websocket_connected = True
        st.session_state.connection_status = "simulated"

    async def _listen_for_messages(self):
        """Listen for incoming WebSocket messages"""
        try:
            if not self.websocket:
                # Simulate message listening for demo
                await self._simulate_message_listening()
                return

            async for message in self.websocket:
                await self._handle_message(message)

        except Exception as e:
            if "ConnectionClosed" in str(e) or "connection closed" in str(e).lower():
                logger.info("WebSocket connection closed")
            else:
                logger.error(f"WebSocket connection error: {e}")
            self.connected = False
            st.session_state.websocket_connected = False
            st.session_state.connection_status = "disconnected"

        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
            raise

    async def _simulate_message_listening(self):
        """Simulate message listening for demo purposes"""
        while self.connected:
            try:
                await asyncio.sleep(1)
                # Simulate periodic status updates
                if hasattr(st, "session_state") and hasattr(
                    st.session_state, "chat_messages"
                ):
                    if len(st.session_state.chat_messages) > 0:
                        # Simulate receiving responses after user messages
                        await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in simulated message listening: {e}")
                await asyncio.sleep(1)

    async def _handle_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            logger.info(f"📨 Received WebSocket message: {message_type}")

            # Add to session messages
            st.session_state.websocket_messages.append(
                {"timestamp": datetime.now(), "data": data}
            )

            # Handle different message types
            if message_type == "system":
                self._handle_system_message(data)
            elif message_type == "agent_response":
                self._handle_agent_response(data)
            elif message_type == "anxiety_update":
                self._handle_anxiety_update(data)
            elif message_type == "typing":
                self._handle_typing_indicator(data)
            elif message_type == "error":
                self._handle_error_message(data)

            # Call registered callbacks
            for callback in self.message_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    def _handle_system_message(self, data: Dict[str, Any]):
        """Handle system message"""
        content = data.get("content", "")

        # Add to chat messages
        system_message = {
            "type": "system",
            "content": content,
            "timestamp": datetime.now(),
        }
        st.session_state.chat_messages.append(system_message)

        logger.info(f"System message: {content}")

    def _handle_agent_response(self, data: Dict[str, Any]):
        """Handle agent response message"""
        content = data.get("content", "")
        agent = data.get("metadata", {}).get("agent", "Unknown Agent")
        anxiety_level = data.get("metadata", {}).get("anxiety_level", "calm")

        # Add to chat messages
        agent_message = {
            "type": "agent",
            "content": content,
            "agent_name": agent,
            "anxiety_level": anxiety_level,
            "timestamp": datetime.now(),
        }
        st.session_state.chat_messages.append(agent_message)

        # Turn off typing indicator
        st.session_state.typing_indicator = False

        logger.info(f"Agent response from {agent}: {content[:50]}...")

    def _handle_anxiety_update(self, data: Dict[str, Any]):
        """Handle anxiety level update"""
        anxiety_level = data.get("metadata", {}).get("anxiety_level", "calm")

        # Update session state
        st.session_state.current_anxiety_level = anxiety_level

        # Add update message
        anxiety_message = {
            "type": "anxiety_update",
            "anxiety_level": anxiety_level,
            "timestamp": datetime.now(),
        }
        st.session_state.chat_messages.append(anxiety_message)

        logger.info(f"Anxiety level updated: {anxiety_level}")

    def _handle_typing_indicator(self, data: Dict[str, Any]):
        """Handle typing indicator"""
        agent = data.get("metadata", {}).get("agent", "AI Agent")

        # Set typing indicator
        st.session_state.typing_indicator = True

        logger.info(f"{agent} is typing...")

    def _handle_error_message(self, data: Dict[str, Any]):
        """Handle error message"""
        content = data.get("content", "Unknown error occurred")

        # Add error message
        error_message = {
            "type": "system",
            "content": f"❌ Error: {content}",
            "timestamp": datetime.now(),
        }
        st.session_state.chat_messages.append(error_message)

        # Turn off typing indicator
        st.session_state.typing_indicator = False

        logger.error(f"WebSocket error: {content}")

    def send_message(self, message: Dict[str, Any]):
        """Send message via WebSocket"""
        try:
            if self.connected and self.websocket:
                # Send via actual WebSocket
                asyncio.create_task(self._send_websocket_message(message))
            else:
                # Simulate sending for demo
                self._simulate_send_message(message)

        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Fallback to simulated response
            self._simulate_send_message(message)

    async def _send_websocket_message(self, message: Dict[str, Any]):
        """Send actual WebSocket message"""
        try:
            message_json = json.dumps(message)
            await self.websocket.send(message_json)
            logger.info(f"📤 Sent WebSocket message: {message.get('type')}")

        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")

    def _simulate_send_message(self, message: Dict[str, Any]):
        """Simulate sending message for demo purposes"""
        message_type = message.get("type")

        if message_type == "user_concern":
            # Simulate agent responses
            self._simulate_agent_responses(message.get("content", ""))
        elif message_type == "continue_conversation":
            # Simulate continuing conversation
            self._simulate_continue_conversation()
        elif message_type == "reset_conversation":
            # Handle reset locally
            st.session_state.chat_messages = []
            st.session_state.current_anxiety_level = "calm"

    def _simulate_agent_responses(self, user_content: str):
        """Simulate agent responses for demo"""
        # Set typing indicator
        st.session_state.typing_indicator = True

        # Define mock responses based on content
        responses = []

        if "friend" in user_content.lower() or "text" in user_content.lower():
            responses = [
                {
                    "agent_name": "IntakeSpecialistAgent",
                    "content": "I understand you're concerned about your friend not responding. That can definitely feel worrying. Let me connect you with our specialists who can help explore this concern more deeply...",
                    "anxiety_level": "mild",
                },
                {
                    "agent_name": "CatastropheEscalatorAgent",
                    "content": "But what if they're not responding because something terrible has happened? What if they're trapped under a vending machine? Or worse, what if they're actively avoiding you because they've decided they don't want to be friends anymore?",
                    "anxiety_level": "moderate",
                },
                {
                    "agent_name": "TimelinePanicGeneratorAgent",
                    "content": "You know, it's been 2 hours since they usually respond. In that time, they could have driven across town, had a full conversation with someone else, or made life-changing decisions without you. Every minute that passes makes this more suspicious...",
                    "anxiety_level": "high",
                },
            ]
        else:
            responses = [
                {
                    "agent_name": "IntakeSpecialistAgent",
                    "content": "Thank you for sharing that concern with me. I can see this is something that's bothering you. Let me bring in our team of specialists to help you explore this worry to its fullest potential.",
                    "anxiety_level": "mild",
                },
                {
                    "agent_name": "SocialAnxietyAmplifierAgent",
                    "content": "Have you considered that everyone around you probably noticed this too? They're probably talking about it right now, sharing looks, maybe even texting each other about what they observed. Social situations have a way of amplifying everything...",
                    "anxiety_level": "moderate",
                },
            ]

        # Schedule responses with delays
        def add_responses():
            time.sleep(2)  # Initial delay

            for i, response in enumerate(responses):
                # Add response to chat
                agent_message = {
                    "type": "agent",
                    "content": response["content"],
                    "agent_name": response["agent_name"],
                    "anxiety_level": response["anxiety_level"],
                    "timestamp": datetime.now(),
                }
                st.session_state.chat_messages.append(agent_message)

                # Update anxiety level
                st.session_state.current_anxiety_level = response["anxiety_level"]

                # Add delay between responses
                if i < len(responses) - 1:
                    time.sleep(3)

            # Turn off typing indicator
            st.session_state.typing_indicator = False

        # Start response thread
        response_thread = threading.Thread(target=add_responses, daemon=True)
        response_thread.start()

    def _simulate_continue_conversation(self):
        """Simulate continuing conversation"""
        st.session_state.typing_indicator = True

        def add_continue_response():
            time.sleep(2)

            # Add continuation response
            continue_message = {
                "type": "agent",
                "content": "But wait, there's more to consider here! Have you thought about all the other implications of this situation? The ripple effects could be enormous...",
                "agent_name": "FalseComfortProviderAgent",
                "anxiety_level": "high",
                "timestamp": datetime.now(),
            }
            st.session_state.chat_messages.append(continue_message)
            st.session_state.typing_indicator = False

        continue_thread = threading.Thread(target=add_continue_response, daemon=True)
        continue_thread.start()

    def add_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for WebSocket messages"""
        self.message_callbacks.append(callback)

    def remove_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove message callback"""
        if callback in self.message_callbacks:
            self.message_callbacks.remove(callback)

    def disconnect(self):
        """Disconnect WebSocket"""
        self.connected = False
        st.session_state.websocket_connected = False
        st.session_state.connection_status = "disconnected"

        if self.websocket:
            asyncio.create_task(self.websocket.close())
            self.websocket = None

        logger.info("🔌 WebSocket disconnected")

    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.connected,
            "status": st.session_state.get("connection_status", "unknown"),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "message_count": len(st.session_state.get("websocket_messages", [])),
        }

    def force_reconnect(self):
        """Force reconnection"""
        logger.info("🔄 Forcing WebSocket reconnection...")
        self.disconnect()
        self.retry_count = 0
        time.sleep(1)
        self.initialize_connection()


# Global real-time handler instance
@st.cache_resource
def get_real_time_handler() -> RealTimeHandler:
    """Get cached real-time handler instance"""
    return RealTimeHandler()
