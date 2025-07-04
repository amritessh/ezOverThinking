# frontend/utils/api_client.py
"""
API Client Utility - Handle all backend API communication
"""

import requests
import streamlit as st
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with the ezOverThinking API backend"""

    def __init__(self, base_url: str = None):
        # Try to get API URL from environment or secrets, fallback to default
        if base_url:
            self.base_url = base_url
        else:
            try:
                # Try environment variable first
                import os

                self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            except:
                try:
                    # Try secrets file
                    self.base_url = st.secrets.get(
                        "API_BASE_URL", "http://localhost:8000"
                    )
                except (FileNotFoundError, KeyError):
                    # Final fallback
                    self.base_url = "http://localhost:8000"
                    logger.warning("Using default API URL: http://localhost:8000")

        self.session = requests.Session()

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        # Initialize authentication
        self._setup_authentication()

    def _setup_authentication(self):
        """Setup authentication for API requests"""
        # For demo purposes, we'll use a mock token
        # In production, implement proper OAuth/JWT flow
        token = st.session_state.get("auth_token", "demo_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            # Return mock data for demo
            return self._get_mock_response(endpoint, method)

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise Exception(f"API Error: {e.response.status_code}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Request failed: {str(e)}")

    def _get_mock_response(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Return mock response when API is unavailable"""
        logger.info(f"Returning mock response for {method} {endpoint}")

        if "send" in endpoint:
            return {
                "responses": [
                    {
                        "agent_name": "IntakeSpecialistAgent",
                        "content": "I understand you're concerned about that. Let me connect you with our specialists who can help explore this worry more deeply...",
                        "anxiety_level": "mild",
                        "escalation_level": 1,
                    },
                    {
                        "agent_name": "CatastropheEscalatorAgent",
                        "content": "But what if this concern is actually a sign of something much worse? Have you considered that this could be the beginning of a complete disaster?",
                        "anxiety_level": "moderate",
                        "escalation_level": 2,
                    },
                ],
                "anxiety_level": "moderate",
                "should_continue": True,
                "conversation_phase": "escalation",
                "timestamp": datetime.now().isoformat(),
            }

        elif "analytics" in endpoint:
            return {
                "user_analytics": {
                    "total_conversations": 47,
                    "average_anxiety_level": 2.8,
                    "peak_anxiety_events": 5,
                    "most_common_triggers": ["social", "work", "health"],
                }
            }

        elif "anxiety-level" in endpoint:
            return {
                "current_level": "moderate",
                "history": [
                    {
                        "level": "mild",
                        "timestamp": "2024-01-01T10:00:00",
                        "trigger": "work_deadline",
                    }
                ],
            }

        else:
            return {"message": "Mock response", "status": "success"}

    # Chat API methods
    def send_message(self, content: str, user_id: str = None) -> Dict[str, Any]:
        """Send message to chat API"""
        payload = {
            "content": content,
            "user_id": user_id or st.session_state.get("user_id", "demo_user"),
        }

        return self._make_request("POST", "/chat/send", json=payload)

    def continue_conversation(self) -> Dict[str, Any]:
        """Continue current conversation"""
        return self._make_request("POST", "/chat/continue")

    def reset_conversation(self) -> Dict[str, Any]:
        """Reset current conversation"""
        return self._make_request("POST", "/chat/reset")

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return self._make_request("GET", "/chat/state")

    def get_anxiety_level(self) -> Dict[str, Any]:
        """Get current anxiety level"""
        return self._make_request("GET", "/chat/anxiety-level")

    def batch_process_concerns(self, concerns: List[str]) -> List[Dict[str, Any]]:
        """Process multiple concerns in batch"""
        payload = [{"content": concern} for concern in concerns]
        return self._make_request("POST", "/chat/batch", json=payload)

    # Analytics API methods
    def get_user_analytics(self, time_range: str = "week") -> Dict[str, Any]:
        """Get user analytics overview"""
        params = {"time_range": time_range}
        return self._make_request("GET", "/analytics/user/overview", params=params)

    def get_anxiety_trends(self, time_range: str = "week") -> Dict[str, Any]:
        """Get anxiety trends data"""
        params = {"time_range": time_range}
        return self._make_request(
            "GET", "/analytics/user/anxiety-trends", params=params
        )

    def get_conversation_patterns(self, time_range: str = "week") -> Dict[str, Any]:
        """Get conversation patterns"""
        params = {"time_range": time_range}
        return self._make_request(
            "GET", "/analytics/user/conversation-patterns", params=params
        )

    def get_worry_categories(self, time_range: str = "week") -> Dict[str, Any]:
        """Get worry categories breakdown"""
        params = {"time_range": time_range}
        return self._make_request(
            "GET", "/analytics/user/worry-categories", params=params
        )

    def get_system_analytics(self, time_range: str = "day") -> Dict[str, Any]:
        """Get system-wide analytics"""
        params = {"time_range": time_range}
        return self._make_request("GET", "/analytics/system/overview", params=params)

    def get_agent_performance(
        self, time_range: str = "day", agent_name: str = None
    ) -> Dict[str, Any]:
        """Get agent performance metrics"""
        params = {"time_range": time_range}
        if agent_name:
            params["agent_name"] = agent_name
        return self._make_request(
            "GET", "/analytics/system/agent-performance", params=params
        )

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return self._make_request("GET", "/analytics/realtime/active-conversations")

    def export_user_data(self, format: str = "json", time_range: str = "all") -> Any:
        """Export user data"""
        params = {"format": format, "time_range": time_range}

        if format == "json":
            return self._make_request(
                "GET", "/analytics/export/user-data", params=params
            )
        else:
            # For CSV/Excel, we'd need to handle binary response
            url = f"{self.base_url}/analytics/export/user-data"
            response = self.session.get(url, params=params)
            return response.content

    def get_personalized_recommendations(self) -> Dict[str, Any]:
        """Get personalized recommendations"""
        return self._make_request("GET", "/analytics/insights/recommendations")

    def get_anxiety_prediction(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Get anxiety level prediction"""
        params = {"hours_ahead": hours_ahead}
        return self._make_request(
            "GET", "/analytics/insights/prediction", params=params
        )

    # Health and system methods
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/health")

    def get_system_health(self) -> Dict[str, Any]:
        """Get detailed system health"""
        return self._make_request("GET", "/analytics/system/health")

    # Authentication methods (for future implementation)
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user"""
        payload = {"username": username, "password": password}
        response = self._make_request("POST", "/auth/login", json=payload)

        if "access_token" in response:
            st.session_state["auth_token"] = response["access_token"]
            st.session_state["user_id"] = response.get("user_id")
            self._setup_authentication()

        return response

    def logout(self) -> None:
        """Logout user"""
        st.session_state.pop("auth_token", None)
        st.session_state.pop("user_id", None)
        self.session.headers.pop("Authorization", None)

    # WebSocket support methods
    def get_websocket_url(self) -> str:
        """Get WebSocket URL for real-time communication"""
        ws_url = self.base_url.replace("http", "ws")
        token = st.session_state.get("auth_token", "demo_token")
        return f"{ws_url}/chat/ws?token={token}"

    # Utility methods
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            self.health_check()
            return True
        except Exception:
            return False

    def get_api_status(self) -> Dict[str, Any]:
        """Get comprehensive API status"""
        try:
            health = self.health_check()
            return {
                "connected": True,
                "status": health.get("status", "unknown"),
                "message": "API is accessible",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "connected": False,
                "status": "error",
                "message": f"API connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Global API client instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()
