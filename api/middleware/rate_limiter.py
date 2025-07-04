# api/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if not self._is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded. Please try again later."
            )

        # Record request
        self._record_request(client_ip)

        # Process request
        response = await call_next(request)
        return response

    def _is_allowed(self, client_ip: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] if req_time > minute_ago
        ]

        # Check if under limit
        return len(self.requests[client_ip]) < self.calls_per_minute

    def _record_request(self, client_ip: str):
        """Record a request for rate limiting"""
        self.requests[client_ip].append(time.time())
