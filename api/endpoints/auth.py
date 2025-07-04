# api/endpoints/auth.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login")
async def login(username: str, password: str) -> Dict[str, Any]:
    """Simple login endpoint for demo purposes"""
    try:
        # For demo purposes, accept any login
        # In production, implement proper authentication

        # Generate a simple token
        token = f"demo_token_{username}_{datetime.now().timestamp()}"

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": username,
            "expires_in": 3600,
        }

    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """Logout endpoint"""
    return {
        "message": "Logged out successfully",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/me")
async def get_current_user_info() -> Dict[str, Any]:
    """Get current user information"""
    return {
        "user_id": "demo_user",
        "username": "demo_user",
        "email": "demo@ezoverthinking.com",
        "created_at": datetime.now().isoformat(),
    }
