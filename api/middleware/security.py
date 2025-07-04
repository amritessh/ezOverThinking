# api/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Basic security middleware"""

    async def dispatch(self, request: Request, call_next):
        # Bypass authentication for local testing
        # if not authenticated:
        #     return JSONResponse(status_code=403, content={"detail": "Not authenticated"})
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
