# api/auth/jwt_handler.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Simple security scheme for now
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Get current user from JWT token or return a mock user for development
    """
    # For development/testing, return a mock user
    # In production, this would validate the JWT token
    if credentials:
        # TODO: Implement proper JWT validation
        logger.info(f"Received credentials: {credentials.scheme}")

    # Return mock user for now
    return {
        "user_id": "test_user_001",
        "username": "test_user",
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
    }


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current admin user - requires admin role
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create JWT access token
    """
    # TODO: Implement proper JWT token creation
    return "mock_jwt_token"


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token
    """
    # TODO: Implement proper JWT token verification
    return {"user_id": "test_user_001", "username": "test_user", "role": "user"}
