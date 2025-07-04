import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import streamlit as st
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the ezOverThinking API backend"""

    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url
        else:
            try:
                self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            except:
                try:
                    self.base_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
                except (FileNotFoundError, KeyError):
                    self.base_url = "http://localhost:8000"
                    logger.warning("Using default API URL: http://localhost:8000")

        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        self._setup_authentication()

    def _setup_authentication(self):
        token = st.session_state.get("auth_token", "demo_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            return {"error": "Connection error"}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise Exception(f"API Error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"Request failed: {str(e)}")

    def send_message(self, content: str, user_id: str = None) -> Dict[str, Any]:
        payload = {
            "content": content,
            "user_id": user_id or st.session_state.get("user_id", "demo_user"),
        }
        return self._make_request("POST", "/chat/send", json=payload)