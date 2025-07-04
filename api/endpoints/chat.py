# api/endpoints/chat.py
from fastapi import APIRouter, WebSocket, Depends, HTTPException, BackgroundTasks
from typing import List
import logging
from datetime import datetime

from src.services.conversation_orchestrator import ConversationOrchestrator
from src.services.anxiety_tracker import AnxietyTracker
from src.models.schemas import (
    ChatRequest,
    ChatResponse,
    UserConcern,
    ConversationState,
    AnxietyLevel,
    ConversationAnalytics,
    ConversationStatus,
)
from ..websocket_handler import get_websocket_handler, initialize_websocket_handler
from ..auth.jwt_handler import get_current_user
from ..dependencies import get_conversation_orchestrator, get_anxiety_tracker

logger = logging.getLogger(__name__)

router = APIRouter()


# REST Endpoints
@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Send a message and get agent responses"""
    try:
        user_id = current_user["user_id"]

        # Create user concern
        user_concern = UserConcern(
            user_id=user_id, original_worry=request.message, timestamp=datetime.now()
        )

        # Process with orchestrator
        result = await orchestrator.process_conversation_turn(
            user_id=user_id, user_concern=user_concern
        )

        # Get current anxiety level
        current_anxiety = await anxiety_tracker.get_current_anxiety_level(user_id)

        # Background task to update analytics
        background_tasks.add_task(
            update_analytics_background, user_id, result, orchestrator
        )

        return ChatResponse(
            conversation_id=result.get("conversation_id", "temp_conv"),
            message=result.get("response", "I'm processing your concern..."),
            agent_name=result.get("agent_name", "System"),
            anxiety_level=current_anxiety or AnxietyLevel.MINIMAL,
            conversation_status=ConversationStatus.ACTIVE,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"❌ Error in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue", response_model=ChatResponse)
async def continue_conversation(
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Continue the current conversation"""
    try:
        user_id = current_user["user_id"]

        # Get current conversation state
        conversation_state = await orchestrator.get_conversation_state(user_id)

        if not conversation_state or not conversation_state.last_concern:
            raise HTTPException(
                status_code=400, detail="No active conversation to continue"
            )

        # Continue with last concern
        result = await orchestrator.process_conversation_turn(
            user_id=user_id, user_concern=conversation_state.last_concern
        )

        current_anxiety = await anxiety_tracker.get_current_anxiety_level(user_id)

        return ChatResponse(
            conversation_id=result.get("conversation_id", "temp_conv"),
            message=result.get("response", "Continuing the conversation..."),
            agent_name=result.get("agent_name", "System"),
            anxiety_level=current_anxiety or AnxietyLevel.MINIMAL,
            conversation_status=ConversationStatus.ACTIVE,
            timestamp=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in continue_conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_conversation(
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Reset the current conversation"""
    try:
        user_id = current_user["user_id"]
        await orchestrator.reset_conversation(user_id)
        return {"message": "Conversation reset successfully"}

    except Exception as e:
        logger.error(f"❌ Error in reset_conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state", response_model=ConversationState)
async def get_conversation_state(
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Get current conversation state"""
    try:
        user_id = current_user["user_id"]
        state = await orchestrator.get_conversation_state(user_id)

        if not state:
            raise HTTPException(status_code=404, detail="No conversation state found")

        return state

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_conversation_state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anxiety-level", response_model=dict)
async def get_anxiety_level(
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Get current anxiety level"""
    try:
        user_id = current_user["user_id"]
        anxiety_level = await anxiety_tracker.get_current_anxiety_level(user_id)
        anxiety_history = await anxiety_tracker.get_anxiety_history(user_id)

        return {
            "current_level": anxiety_level.value,
            "history": [
                {
                    "level": entry.anxiety_level.value,
                    "timestamp": entry.timestamp.isoformat(),
                    "trigger": entry.trigger,
                }
                for entry in anxiety_history[-10:]  # Last 10 entries
            ],
        }

    except Exception as e:
        logger.error(f"❌ Error in get_anxiety_level: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=ConversationAnalytics)
async def get_conversation_analytics(
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Get conversation analytics"""
    try:
        user_id = current_user["user_id"]
        analytics = await orchestrator.get_conversation_analytics(user_id)
        return analytics

    except Exception as e:
        logger.error(f"❌ Error in get_conversation_analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket Endpoint
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
):
    """WebSocket endpoint for real-time chat"""
    try:
        # Verify token and get user
        # Note: In production, implement proper WebSocket auth
        user_id = "demo_user"  # Replace with actual auth

        # Initialize WebSocket handler if not already done
        try:
            handler = get_websocket_handler()
        except RuntimeError:
            handler = initialize_websocket_handler(orchestrator, anxiety_tracker)

        # Handle connection
        await handler.handle_connection(websocket, user_id)

    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason="Internal server error")


# Background task helpers
async def update_analytics_background(
    user_id: str, result: any, orchestrator: ConversationOrchestrator
):
    """Background task to update analytics"""
    try:
        await orchestrator.update_conversation_analytics(user_id, result)
        logger.debug(f"✅ Analytics updated for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Error updating analytics: {e}")


# Streaming endpoint for real-time responses
@router.post("/stream")
async def stream_conversation(
    request: ChatRequest,
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Stream conversation responses in real-time"""
    try:
        user_id = current_user["user_id"]

        # Create user concern
        user_concern = UserConcern(
            user_id=user_id, original_worry=request.message, timestamp=datetime.now()
        )

        # Create streaming response
        async def generate_responses():
            try:
                # Process with orchestrator
                async for response in orchestrator.stream_conversation_turn(
                    user_id=user_id, user_concern=user_concern
                ):
                    yield f"data: {response.json()}\n\n"

            except Exception as e:
                logger.error(f"❌ Error in stream generation: {e}")
                yield f"data: {{'error': '{str(e)}'}}\n\n"

        return StreamingResponse(
            generate_responses(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        logger.error(f"❌ Error in stream_conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch processing endpoint
@router.post("/batch", response_model=List[ChatResponse])
async def batch_process_concerns(
    requests: List[ChatRequest],
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    anxiety_tracker: AnxietyTracker = Depends(get_anxiety_tracker),
    current_user: dict = Depends(get_current_user),
):
    """Process multiple concerns in batch"""
    try:
        user_id = current_user["user_id"]
        responses = []

        for request in requests:
            user_concern = UserConcern(
                user_id=user_id, content=request.content, timestamp=datetime.now()
            )

            result = await orchestrator.process_conversation_turn(
                user_id=user_id, user_concern=user_concern
            )

            current_anxiety = await anxiety_tracker.get_current_anxiety_level(user_id)

            responses.append(
                ChatResponse(
                    responses=result.responses,
                    anxiety_level=current_anxiety,
                    should_continue=result.should_continue,
                    conversation_phase=result.conversation_phase,
                    timestamp=datetime.now(),
                )
            )

        return responses

    except Exception as e:
        logger.error(f"❌ Error in batch_process_concerns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints
@router.get("/admin/active-conversations")
async def get_active_conversations(
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Get active conversations (admin only)"""
    # Note: Add admin role check in production
    try:
        active_conversations = await orchestrator.get_active_conversations()
        return {"active_conversations": active_conversations}

    except Exception as e:
        logger.error(f"❌ Error in get_active_conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/broadcast")
async def broadcast_message(
    message: str,
    orchestrator: ConversationOrchestrator = Depends(get_conversation_orchestrator),
    current_user: dict = Depends(get_current_user),
):
    """Broadcast message to all active conversations (admin only)"""
    # Note: Add admin role check in production
    try:
        await orchestrator.broadcast_system_message(message)
        return {"message": "Broadcast sent successfully"}

    except Exception as e:
        logger.error(f"❌ Error in broadcast_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
