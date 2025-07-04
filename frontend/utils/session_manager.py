# frontend/utils/session_manager.py
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions and state in the Streamlit frontend"""

    def __init__(self):
        self.session_key = "ezoverthinking_session"
        self.user_data_key = "user_data"
        self.conversation_key = "conversation_data"
        self.settings_key = "user_settings"

    def initialize_session(self, user_id: str = None) -> bool:
        """Initialize a new user session"""
        try:
            if user_id is None:
                user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            session_data = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "authenticated": True,
                "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            }

            st.session_state[self.session_key] = session_data
            st.session_state[self.user_data_key] = {
                "user_id": user_id,
                "username": f"User_{user_id[-4:]}",
                "email": None,
                "preferences": {},
                "created_at": datetime.now().isoformat(),
            }

            # Initialize conversation data
            st.session_state[self.conversation_key] = {
                "conversation_id": None,
                "messages": [],
                "current_anxiety_level": "calm",
                "anxiety_history": [],
                "agents_involved": [],
                "start_time": None,
                "last_message_time": None,
            }

            # Initialize user settings
            st.session_state[self.settings_key] = {
                "theme": "dark",
                "notifications": True,
                "sound_effects": True,
                "auto_continue": False,
                "anxiety_alerts": True,
                "privacy_mode": False,
            }

            logger.info(f"✅ Session initialized for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing session: {e}")
            return False

    def get_user_id(self) -> Optional[str]:
        """Get current user ID"""
        session_data = st.session_state.get(self.session_key, {})
        return session_data.get("user_id")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        session_data = st.session_state.get(self.session_key, {})
        return session_data.get("authenticated", False)

    def update_activity(self):
        """Update last activity timestamp"""
        if self.session_key in st.session_state:
            st.session_state[self.session_key][
                "last_activity"
            ] = datetime.now().isoformat()

    def get_user_data(self) -> Dict[str, Any]:
        """Get user data"""
        return st.session_state.get(self.user_data_key, {})

    def update_user_data(self, data: Dict[str, Any]):
        """Update user data"""
        current_data = st.session_state.get(self.user_data_key, {})
        current_data.update(data)
        st.session_state[self.user_data_key] = current_data
        self.update_activity()

    def get_conversation_data(self) -> Dict[str, Any]:
        """Get conversation data"""
        return st.session_state.get(self.conversation_key, {})

    def update_conversation_data(self, data: Dict[str, Any]):
        """Update conversation data"""
        current_data = st.session_state.get(self.conversation_key, {})
        current_data.update(data)
        current_data["last_message_time"] = datetime.now().isoformat()
        st.session_state[self.conversation_key] = current_data
        self.update_activity()

    def add_message(self, message: Dict[str, Any]):
        """Add a message to conversation history"""
        conversation_data = self.get_conversation_data()
        messages = conversation_data.get("messages", [])
        messages.append(
            {
                **message,
                "timestamp": datetime.now().isoformat(),
                "id": f"msg_{len(messages) + 1}",
            }
        )
        conversation_data["messages"] = messages
        st.session_state[self.conversation_key] = conversation_data
        self.update_activity()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get conversation messages"""
        conversation_data = self.get_conversation_data()
        return conversation_data.get("messages", [])

    def clear_messages(self):
        """Clear conversation messages"""
        conversation_data = self.get_conversation_data()
        conversation_data["messages"] = []
        conversation_data["conversation_id"] = None
        conversation_data["start_time"] = None
        st.session_state[self.conversation_key] = conversation_data
        self.update_activity()

    def update_anxiety_level(self, level: str, trigger: str = None):
        """Update current anxiety level"""
        conversation_data = self.get_conversation_data()
        conversation_data["current_anxiety_level"] = level

        # Add to anxiety history
        anxiety_entry = {
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger,
        }
        anxiety_history = conversation_data.get("anxiety_history", [])
        anxiety_history.append(anxiety_entry)
        conversation_data["anxiety_history"] = anxiety_history[
            -50:
        ]  # Keep last 50 entries

        st.session_state[self.conversation_key] = conversation_data
        self.update_activity()

    def get_current_anxiety_level(self) -> str:
        """Get current anxiety level"""
        conversation_data = self.get_conversation_data()
        return conversation_data.get("current_anxiety_level", "calm")

    def get_anxiety_history(self) -> List[Dict[str, Any]]:
        """Get anxiety level history"""
        conversation_data = self.get_conversation_data()
        return conversation_data.get("anxiety_history", [])

    def get_settings(self) -> Dict[str, Any]:
        """Get user settings"""
        return st.session_state.get(self.settings_key, {})

    def update_settings(self, settings: Dict[str, Any]):
        """Update user settings"""
        current_settings = st.session_state.get(self.settings_key, {})
        current_settings.update(settings)
        st.session_state[self.settings_key] = current_settings
        self.update_activity()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        settings = self.get_settings()
        return settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """Set a specific setting value"""
        settings = self.get_settings()
        settings[key] = value
        st.session_state[self.settings_key] = settings
        self.update_activity()

    def reset_session(self):
        """Reset the entire session"""
        keys_to_clear = [
            self.session_key,
            self.user_data_key,
            self.conversation_key,
            self.settings_key,
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        logger.info("✅ Session reset completed")

    def export_session_data(self) -> Dict[str, Any]:
        """Export session data for backup/debugging"""
        return {
            "session": st.session_state.get(self.session_key, {}),
            "user_data": st.session_state.get(self.user_data_key, {}),
            "conversation": st.session_state.get(self.conversation_key, {}),
            "settings": st.session_state.get(self.settings_key, {}),
            "export_timestamp": datetime.now().isoformat(),
        }

    def import_session_data(self, data: Dict[str, Any]) -> bool:
        """Import session data from backup"""
        try:
            if "session" in data:
                st.session_state[self.session_key] = data["session"]
            if "user_data" in data:
                st.session_state[self.user_data_key] = data["user_data"]
            if "conversation" in data:
                st.session_state[self.conversation_key] = data["conversation"]
            if "settings" in data:
                st.session_state[self.settings_key] = data["settings"]

            logger.info("✅ Session data imported successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error importing session data: {e}")
            return False

    def is_session_expired(self, max_hours: int = 24) -> bool:
        """Check if session has expired"""
        session_data = st.session_state.get(self.session_key, {})
        last_activity = session_data.get("last_activity")

        if not last_activity:
            return True

        try:
            last_activity_dt = datetime.fromisoformat(last_activity)
            expiry_time = last_activity_dt + timedelta(hours=max_hours)
            return datetime.now() > expiry_time
        except Exception:
            return True

    def cleanup_expired_session(self):
        """Clean up expired session"""
        if self.is_session_expired():
            self.reset_session()
            logger.info("✅ Expired session cleaned up")
