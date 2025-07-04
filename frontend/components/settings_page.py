# frontend/components/settings_page.py
"""
Settings Page Component - User configuration and preferences
"""

import streamlit as st
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class SettingsPage:
    """Settings page for user configuration and preferences"""
    
    def __init__(self, session_manager, theme_manager):
        self.session_manager = session_manager
        self.theme_manager = theme_manager
        
        # Initialize settings
        self.initialize_settings()
    
    def initialize_settings(self):
        """Initialize settings with defaults"""
        default_settings = {
            'appearance': {
                'theme': 'dark',
                'font_size': 'medium',
                'animation_speed': 'normal',
                'color_scheme': 'default'
            },
            'notifications': {
                'enabled': True,
                'sound_effects': True,
                'desktop_notifications': False,
                'email_notifications': False
            },
            'chat': {
                'auto_continue': False,
                'typing_simulation': True,
                'show_agent_names': True,
                'message_timestamps': True,
                'anxiety_alerts': True
            },
            'analytics': {
                'data_collection': True,
                'anonymous_mode': False,
                'export_format': 'json',
                'auto_refresh': True
            },
            'advanced': {
                'debug_mode': False,
                'api_timeout': 30,
                'max_retries': 3,
                'websocket_enabled': True
            }
        }
        
        if 'user_settings' not in st.session_state:
            st.session_state.user_settings = default_settings
    
    def render(self):
        """Render the complete settings page"""
        st.markdown("### ⚙️ Settings & Preferences")
        
        # Settings tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎨 Appearance",
            "🔔 Notifications", 
            "💬 Chat Settings",
            "📊 Analytics",
            "⚙️ Advanced"
        ])
        
        with tab1:
            self.render_appearance_settings()
        
        with tab2:
            self.render_notification_settings()
        
        with tab3:
            self.render_chat_settings()
        
        with tab4:
            self.render_analytics_settings()
        
        with tab5:
            self.render_advanced_settings()
        
        # Settings actions
        self.render_settings_actions()
    
    def render_appearance_settings(self):
        """Render appearance settings"""
        st.markdown("#### 🎨 Appearance & Theme")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Theme selection
            theme_options = ['light', 'dark', 'auto']
            current_theme = st.session_state.user_settings['appearance']['theme']
            
            new_theme = st.selectbox(
                "🌓 Theme",
                theme_options,
                index=theme_options.index(current_theme),
                help="Choose your preferred color theme"
            )
            
            if new_theme != current_theme:
                st.session_state.user_settings['appearance']['theme'] = new_theme
                self.theme_manager.apply_theme(new_theme)
                st.rerun()
            
            # Font size
            font_options = ['small', 'medium', 'large']
            current_font = st.session_state.user_settings['appearance']['font_size']
            
            new_font = st.selectbox(
                "📝 Font Size",
                font_options,
                index=font_options.index(current_font),
                help="Adjust text size for better readability"
            )
            
            if new_font != current_font:
                st.session_state.user_settings['appearance']['font_size'] = new_font
                st.success("Font size updated!")
        
        with col2:
            # Animation speed
            animation_options = ['slow', 'normal', 'fast', 'none']
            current_animation = st.session_state.user_settings['appearance']['animation_speed']
            
            new_animation = st.selectbox(
                "🎭 Animation Speed",
                animation_options,
                index=animation_options.index(current_animation),
                help="Control animation and transition speeds"
            )
            
            if new_animation != current_animation:
                st.session_state.user_settings['appearance']['animation_speed'] = new_animation
                st.success("Animation speed updated!")
            
            # Color scheme
            color_options = ['default', 'colorful', 'monochrome', 'high_contrast']
            current_color = st.session_state.user_settings['appearance']['color_scheme']
            
            new_color = st.selectbox(
                "🎨 Color Scheme",
                color_options,
                index=color_options.index(current_color),
                help="Choose your preferred color palette"
            )
            
            if new_color != current_color:
                st.session_state.user_settings['appearance']['color_scheme'] = new_color
                st.success("Color scheme updated!")
        
        # Theme preview
        st.markdown("#### 🔍 Theme Preview")
        self.render_theme_preview()
    
    def render_notification_settings(self):
        """Render notification settings"""
        st.markdown("#### 🔔 Notifications & Alerts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Notification toggles
            st.session_state.user_settings['notifications']['enabled'] = st.checkbox(
                "🔔 Enable Notifications",
                value=st.session_state.user_settings['notifications']['enabled'],
                help="Enable or disable all notifications"
            )
            
            st.session_state.user_settings['notifications']['sound_effects'] = st.checkbox(
                "🔊 Sound Effects",
                value=st.session_state.user_settings['notifications']['sound_effects'],
                help="Play sound effects for interactions"
            )
            
            st.session_state.user_settings['notifications']['desktop_notifications'] = st.checkbox(
                "🖥️ Desktop Notifications",
                value=st.session_state.user_settings['notifications']['desktop_notifications'],
                help="Show browser notifications"
            )
            
            st.session_state.user_settings['notifications']['email_notifications'] = st.checkbox(
                "📧 Email Notifications",
                value=st.session_state.user_settings['notifications']['email_notifications'],
                help="Send email notifications for important events"
            )
        
        with col2:
            # Notification preferences
            st.markdown("##### 📋 Notification Types")
            
            notification_types = [
                "New agent responses",
                "Anxiety level changes",
                "Connection status updates",
                "System maintenance",
                "Weekly analytics summary"
            ]
            
            for notif_type in notification_types:
                enabled = st.checkbox(
                    notif_type,
                    value=True,
                    key=f"notif_{notif_type.replace(' ', '_').lower()}"
                )
        
        # Test notification
        if st.button("🧪 Test Notification"):
            st.success("🔔 Test notification sent successfully!")
            st.balloons()
    
    def render_chat_settings(self):
        """Render chat settings"""
        st.markdown("#### 💬 Chat Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Chat behavior
            st.session_state.user_settings['chat']['auto_continue'] = st.checkbox(
                "🔄 Auto-continue Conversations",
                value=st.session_state.user_settings['chat']['auto_continue'],
                help="Automatically continue conversations without prompting"
            )
            
            st.session_state.user_settings['chat']['typing_simulation'] = st.checkbox(
                "⌨️ Typing Simulation",
                value=st.session_state.user_settings['chat']['typing_simulation'],
                help="Show typing indicators while agents are responding"
            )
            
            st.session_state.user_settings['chat']['show_agent_names'] = st.checkbox(
                "🏷️ Show Agent Names",
                value=st.session_state.user_settings['chat']['show_agent_names'],
                help="Display the name of each AI agent"
            )
            
            st.session_state.user_settings['chat']['message_timestamps'] = st.checkbox(
                "🕐 Message Timestamps",
                value=st.session_state.user_settings['chat']['message_timestamps'],
                help="Show timestamps for all messages"
            )
        
        with col2:
            # Anxiety settings
            st.session_state.user_settings['chat']['anxiety_alerts'] = st.checkbox(
                "🚨 Anxiety Level Alerts",
                value=st.session_state.user_settings['chat']['anxiety_alerts'],
                help="Get alerts when anxiety levels reach certain thresholds"
            )
            
            # Anxiety threshold
            anxiety_threshold = st.slider(
                "📊 Anxiety Alert Threshold",
                min_value=1,
                max_value=5,
                value=4,
                help="Set the anxiety level that triggers alerts"
            )
            
            # Message history
            history_limit = st.number_input(
                "📝 Message History Limit",
                min_value=50,
                max_value=1000,
                value=200,
                step=50,
                help="Maximum number of messages to keep in history"
            )
            
            # Auto-export
            auto_export = st.checkbox(
                "💾 Auto-export Chat History",
                value=False,
                help="Automatically export chat history daily"
            )
    
    def render_analytics_settings(self):
        """Render analytics settings"""
        st.markdown("#### 📊 Analytics & Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data collection
            st.session_state.user_settings['analytics']['data_collection'] = st.checkbox(
                "📈 Enable Data Collection",
                value=st.session_state.user_settings['analytics']['data_collection'],
                help="Allow collection of usage data for analytics"
            )
            
            st.session_state.user_settings['analytics']['anonymous_mode'] = st.checkbox(
                "🕵️ Anonymous Mode",
                value=st.session_state.user_settings['analytics']['anonymous_mode'],
                help="Anonymize your data in analytics"
            )
            
            st.session_state.user_settings['analytics']['auto_refresh'] = st.checkbox(
                "🔄 Auto-refresh Analytics",
                value=st.session_state.user_settings['analytics']['auto_refresh'],
                help="Automatically refresh analytics data"
            )
        
        with col2:
            # Export settings
            export_options = ['json', 'csv', 'excel']
            current_export = st.session_state.user_settings['analytics']['export_format']
            
            st.session_state.user_settings['analytics']['export_format'] = st.selectbox(
                "📄 Export Format",
                export_options,
                index=export_options.index(current_export),
                help="Default format for data exports"
            )
            
            # Data retention
            retention_days = st.number_input(
                "🗓️ Data Retention (days)",
                min_value=7,
                max_value=365,
                value=90,
                help="How long to keep your data"
            )
            
            # Analytics sharing
            share_analytics = st.checkbox(
                "🤝 Share Anonymous Analytics",
                value=False,
                help="Share anonymized analytics to help improve the system"
            )
        
        # Data management
        st.markdown("#### 🗂️ Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export All Data"):
                st.success("📥 Data export initiated!")
        
        with col2:
            if st.button("🔄 Reset Analytics"):
                st.warning("⚠️ This will clear all your analytics data!")
        
        with col3:
            if st.button("🗑️ Delete All Data"):
                st.error("❌ This will permanently delete all your data!")
    
    def render_advanced_settings(self):
        """Render advanced settings"""
        st.markdown("#### ⚙️ Advanced Configuration")
        
        st.warning("⚠️ Advanced settings - modify with caution!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Debug settings
            st.session_state.user_settings['advanced']['debug_mode'] = st.checkbox(
                "🐛 Debug Mode",
                value=st.session_state.user_settings['advanced']['debug_mode'],
                help="Enable debug logging and additional information"
            )
            
            st.session_state.user_settings['advanced']['websocket_enabled'] = st.checkbox(
                "🌐 WebSocket Enabled",
                value=st.session_state.user_settings['advanced']['websocket_enabled'],
                help="Enable real-time WebSocket communication"
            )
            
            # API settings
            st.session_state.user_settings['advanced']['api_timeout'] = st.number_input(
                "⏱️ API Timeout (seconds)",
                min_value=5,
                max_value=120,
                value=st.session_state.user_settings['advanced']['api_timeout'],
                help="Request timeout for API calls"
            )
            
            st.session_state.user_settings['advanced']['max_retries'] = st.number_input(
                "🔄 Max Retries",
                min_value=1,
                max_value=10,
                value=st.session_state.user_settings['advanced']['max_retries'],
                help="Maximum number of retry attempts"
            )
        
        with col2:
            # System information
            st.markdown("##### 📋 System Information")
            
            system_info = {
                "App Version": "1.0.0",
                "Streamlit Version": st.__version__,
                "Python Version": "3.11+",
                "API Status": "Connected" if st.session_state.get('websocket_connected', False) else "Disconnected",
                "Session ID": st.session_state.get('user_id', 'demo_user')[:8] + "...",
                "Settings Last Modified": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            for key, value in system_info.items():
                st.text(f"{key}: {value}")
            
            # Advanced actions
            st.markdown("##### 🔧 Advanced Actions")
            
            if st.button("🔄 Reset All Settings"):
                if st.checkbox("⚠️ Confirm Reset"):
                    self.reset_all_settings()
                    st.success("✅ All settings reset to defaults!")
                    st.rerun()
            
            if st.button("📋 Export Settings"):
                self.export_settings()
            
            if st.button("📄 View Logs"):
                self.show_debug_logs()
    
    def render_theme_preview(self):
        """Render theme preview"""
        current_theme = st.session_state.user_settings['appearance']['theme']
        
        # Create preview layout
        preview_html = f"""
        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h4>🎨 {current_theme.title()} Theme Preview</h4>
            <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                <div style="background: {'#1E1E1E' if current_theme == 'dark' else '#FFFFFF'}; 
                            color: {'#FFFFFF' if current_theme == 'dark' else '#000000'}; 
                            padding: 0.5rem; border-radius: 5px; flex: 1;">
                    <strong>Chat Message</strong><br>
                    This is how your messages will look
                </div>
                <div style="background: linear-gradient(135deg, #FF6B6B, #4ECDC4); 
                            color: white; padding: 0.5rem; border-radius: 5px; flex: 1;">
                    <strong>Agent Response</strong><br>
                    This is how agent responses will appear
                </div>
            </div>
        </div>
        """
        
        st.markdown(preview_html, unsafe_allow_html=True)
    
    def render_settings_actions(self):
        """Render settings action buttons"""
        st.markdown("---")
        st.markdown("#### 💾 Settings Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Save Settings", type="primary"):
                self.save_settings()
                st.success("✅ Settings saved successfully!")
        
        with col2:
            if st.button("🔄 Reset to Defaults"):
                self.reset_to_defaults()
                st.success("✅ Settings reset to defaults!")
                st.rerun()
        
        with col3:
            if st.button("📥 Import Settings"):
                self.import_settings()
        
        with col4:
            if st.button("📤 Export Settings"):
                self.export_settings()
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Save to session state
            st.session_state.user_settings['last_modified'] = datetime.now().isoformat()
            
            # In a real app, you'd save to database or file
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            st.error(f"❌ Error saving settings: {e}")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        try:
            self.initialize_settings()
            logger.info("Settings reset to defaults")
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            st.error(f"❌ Error resetting settings: {e}")
    
    def reset_all_settings(self):
        """Reset all settings including session state"""
        try:
            # Clear all settings
            st.session_state.user_settings = {}
            self.initialize_settings()
            
            # Reset other session state
            st.session_state.current_anxiety_level = 'calm'
            st.session_state.chat_messages = []
            
            logger.info("All settings and data reset")
            
        except Exception as e:
            logger.error(f"Error resetting all settings: {e}")
            st.error(f"❌ Error resetting all settings: {e}")
    
    def export_settings(self):
        """Export settings to JSON"""
        try:
            settings_json = json.dumps(
                st.session_state.user_settings,
                indent=2,
                default=str
            )
            
            st.download_button(
                label="📥 Download Settings",
                data=settings_json,
                file_name=f"ezoverthinking_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("📤 Settings prepared for download!")
            
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            st.error(f"❌ Error exporting settings: {e}")
    
    def import_settings(self):
        """Import settings from JSON"""
        st.markdown("##### 📥 Import Settings")
        
        uploaded_file = st.file_uploader(
            "Choose settings file",
            type=['json'],
            help="Upload a JSON file with your settings"
        )
        
        if uploaded_file is not None:
            try:
                settings_data = json.load(uploaded_file)
                
                # Validate settings structure
                if self.validate_settings(settings_data):
                    st.session_state.user_settings = settings_data
                    st.success("✅ Settings imported successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid settings file format!")
                    
            except Exception as e:
                logger.error(f"Error importing settings: {e}")
                st.error(f"❌ Error importing settings: {e}")
    
    def validate_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Validate settings data structure"""
        try:
            required_sections = ['appearance', 'notifications', 'chat', 'analytics', 'advanced']
            
            for section in required_sections:
                if section not in settings_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def show_debug_logs(self):
        """Show debug logs"""
        st.markdown("##### 📄 Debug Logs")
        
        # Mock debug logs for demo
        debug_logs = [
            "2024-01-15 10:30:15 - INFO - Settings page loaded",
            "2024-01-15 10:30:16 - DEBUG - Theme applied: dark",
            "2024-01-15 10:30:17 - INFO - WebSocket connection established",
            "2024-01-15 10:30:18 - DEBUG - Analytics data refreshed",
            "2024-01-15 10:30:19 - INFO - User interaction recorded"
        ]
        
        log_text = "\n".join(debug_logs)
        st.text_area("Debug Logs", value=log_text, height=200)
        
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return st.session_state.user_settings.copy()
    
    def update_setting(self, section: str, key: str, value: Any):
        """Update a specific setting"""
        if section in st.session_state.user_settings:
            st.session_state.user_settings[section][key] = value
            self.save_settings()
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return st.session_state.user_settings.get(section, {}).get(key, default)