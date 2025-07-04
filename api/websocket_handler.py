# api/websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
import uuid

from src.services.conversation_orchestrator import ConversationOrchestrator
from src.services.anxiety_tracker import AnxietyTracker
from src.models.schemas import (
    WebSocketMessage, WebSocketMessageType, UserConcern,
    ConversationState, AnxietyLevel, AgentResponse
)

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # websocket_id -> user_id
        self.conversation_states: Dict[str, ConversationState] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Generate unique connection ID
        connection_id = str(uuid.uuid4())
        
        # Store connection
        self.active_connections[connection_id] = websocket
        self.user_sessions[connection_id] = user_id
        
        logger.info(f"🔗 New WebSocket connection: {connection_id} for user: {user_id}")
        
        # Send welcome message
        await self.send_message(connection_id, WebSocketMessage(
            type=WebSocketMessageType.SYSTEM,
            content="Welcome to ezOverThinking! Ready to spiral into anxiety? 🌪️",
            timestamp=datetime.now()
        ))
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
            
            del self.active_connections[connection_id]
            
            if connection_id in self.user_sessions:
                user_id = self.user_sessions[connection_id]
                del self.user_sessions[connection_id]
                logger.info(f"🔌 WebSocket disconnected: {connection_id} for user: {user_id}")
    
    async def send_message(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(message.json())
                logger.debug(f"📤 Message sent to {connection_id}: {message.type}")
            except Exception as e:
                logger.error(f"❌ Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id)
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a user"""
        connections_to_send = [
            conn_id for conn_id, uid in self.user_sessions.items() 
            if uid == user_id
        ]
        
        for connection_id in connections_to_send:
            await self.send_message(connection_id, message)
    
    async def send_typing_indicator(self, connection_id: str, agent_name: str):
        """Send typing indicator"""
        await self.send_message(connection_id, WebSocketMessage(
            type=WebSocketMessageType.TYPING,
            content=f"{agent_name} is typing...",
            timestamp=datetime.now(),
            metadata={"agent": agent_name}
        ))
    
    async def send_anxiety_update(self, connection_id: str, anxiety_level: AnxietyLevel):
        """Send real-time anxiety level update"""
        await self.send_message(connection_id, WebSocketMessage(
            type=WebSocketMessageType.ANXIETY_UPDATE,
            content=f"Anxiety level: {anxiety_level.value}",
            timestamp=datetime.now(),
            metadata={"anxiety_level": anxiety_level.value}
        ))

class WebSocketHandler:
    """Handles WebSocket communication with conversation orchestrator"""
    
    def __init__(self, 
                 orchestrator: ConversationOrchestrator,
                 anxiety_tracker: AnxietyTracker):
        self.orchestrator = orchestrator
        self.anxiety_tracker = anxiety_tracker
        self.connection_manager = ConnectionManager()
        
    async def handle_connection(self, websocket: WebSocket, user_id: str):
        """Handle new WebSocket connection"""
        connection_id = await self.connection_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message
                await self._process_message(connection_id, message_data)
                
        except WebSocketDisconnect:
            logger.info(f"🔌 WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"❌ WebSocket error for {connection_id}: {e}")
        finally:
            await self.connection_manager.disconnect(connection_id)
    
    async def _process_message(self, connection_id: str, message_data: dict):
        """Process incoming WebSocket message"""
        try:
            # Parse message
            message_type = message_data.get('type')
            content = message_data.get('content')
            user_id = self.connection_manager.user_sessions.get(connection_id)
            
            if not user_id:
                logger.error(f"❌ No user ID for connection: {connection_id}")
                return
            
            if message_type == 'user_concern':
                await self._handle_user_concern(connection_id, user_id, content)
            elif message_type == 'continue_conversation':
                await self._handle_continue_conversation(connection_id, user_id)
            elif message_type == 'reset_conversation':
                await self._handle_reset_conversation(connection_id, user_id)
            elif message_type == 'get_analytics':
                await self._handle_get_analytics(connection_id, user_id)
            else:
                logger.warning(f"🤔 Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content=f"Error processing your message: {str(e)}",
                timestamp=datetime.now()
            ))
    
    async def _handle_user_concern(self, connection_id: str, user_id: str, content: str):
        """Handle user concern input"""
        try:
            # Create user concern
            user_concern = UserConcern(
                user_id=user_id,
                original_worry=content,
                timestamp=datetime.now()
            )
            
            # Send acknowledgment
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.SYSTEM,
                content="Processing your concern... 🤔",
                timestamp=datetime.now()
            ))
            
            # Process with orchestrator
            await self._process_conversation_turn(connection_id, user_id, user_concern)
            
        except Exception as e:
            logger.error(f"❌ Error handling user concern: {e}")
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content="Sorry, I had trouble processing your concern. Please try again.",
                timestamp=datetime.now()
            ))
    
    async def _process_conversation_turn(self, connection_id: str, user_id: str, user_concern: UserConcern):
        """Process a full conversation turn with multiple agents"""
        try:
            # Start conversation processing
            # Check for existing conversation
            conversation_state = await self.orchestrator.get_conversation_state(user_id)
            if conversation_state is None:
                # Start a new conversation
                conversation_id = await self.orchestrator.start_conversation(user_id, user_concern)
            else:
                conversation_id = conversation_state.conversation_id
            
            # Orchestrate response
            agent_response = await self.orchestrator.orchestrate_response(conversation_id, user_concern.original_worry)
            
            # Create a result object similar to what was expected
            result = type('Result', (), {
                'responses': [agent_response],
                'should_continue': True
            })()
            
            # Send agent response
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.AGENT_RESPONSE,
                content=agent_response.response,
                timestamp=datetime.now(),
                metadata={
                    "agent": agent_response.agent_name,
                    "anxiety_level": 1,  # Default anxiety level
                    "escalation_level": 0  # Default escalation level
                }
            ))
            
            # Add delay for realistic conversation flow
            await asyncio.sleep(1.5)
            
            # Send anxiety update
            # Get conversation state to find conversation_id
            conversation_state = await self.orchestrator.get_conversation_state(user_id)
            if conversation_state:
                current_anxiety = await self.anxiety_tracker.get_real_time_anxiety(conversation_state.conversation_id)
                await self.connection_manager.send_anxiety_update(connection_id, current_anxiety)
            
            # Check if conversation should continue
            if result.should_continue:
                await self.connection_manager.send_message(connection_id, WebSocketMessage(
                    type=WebSocketMessageType.SYSTEM,
                    content="Would you like to explore this further? 🤔",
                    timestamp=datetime.now()
                ))
            else:
                await self.connection_manager.send_message(connection_id, WebSocketMessage(
                    type=WebSocketMessageType.SYSTEM,
                    content="Thanks for overthinking with us! 🌪️ Feel free to share another concern.",
                    timestamp=datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"❌ Error processing conversation turn: {e}")
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content="Something went wrong while processing your concern. Please try again.",
                timestamp=datetime.now()
            ))
    
    async def _handle_continue_conversation(self, connection_id: str, user_id: str):
        """Handle continue conversation request"""
        try:
            # Get current conversation state
            conversation_state = await self.orchestrator.get_conversation_state(user_id)
            
            if not conversation_state or not conversation_state.last_concern:
                await self.connection_manager.send_message(connection_id, WebSocketMessage(
                    type=WebSocketMessageType.SYSTEM,
                    content="Please share a concern first! 🤔",
                    timestamp=datetime.now()
                ))
                return
            
            # Continue with last concern
            await self._process_conversation_turn(connection_id, user_id, conversation_state.last_concern)
            
        except Exception as e:
            logger.error(f"❌ Error continuing conversation: {e}")
    
    async def _handle_reset_conversation(self, connection_id: str, user_id: str):
        """Handle reset conversation request"""
        try:
            await self.orchestrator.reset_conversation(user_id)
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.SYSTEM,
                content="Conversation reset! Ready for fresh overthinking? 🌪️",
                timestamp=datetime.now()
            ))
        except Exception as e:
            logger.error(f"❌ Error resetting conversation: {e}")
    
    async def _handle_get_analytics(self, connection_id: str, user_id: str):
        """Handle analytics request"""
        try:
            analytics = await self.orchestrator.get_user_conversation_analytics(user_id)
            await self.connection_manager.send_message(connection_id, WebSocketMessage(
                type=WebSocketMessageType.ANALYTICS,
                content="Here's your overthinking analytics:",
                timestamp=datetime.now(),
                metadata=analytics.dict()
            ))
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")

# Global handler instance
websocket_handler: Optional[WebSocketHandler] = None

def get_websocket_handler() -> WebSocketHandler:
    """Get the global WebSocket handler instance"""
    global websocket_handler
    if not websocket_handler:
        raise RuntimeError("WebSocket handler not initialized")
    return websocket_handler

def initialize_websocket_handler(orchestrator: ConversationOrchestrator, anxiety_tracker: AnxietyTracker):
    """Initialize the global WebSocket handler"""
    global websocket_handler
    websocket_handler = WebSocketHandler(orchestrator, anxiety_tracker)
    return websocket_handler