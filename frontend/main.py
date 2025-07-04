# frontend/main.py
"""
ezOverThinking - Main Streamlit Application
A modern, interactive frontend for the AI-powered overthinking amplification system
"""

import streamlit as st
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import websockets
import threading
import time

# Configure page
st.set_page_config(
    page_title="ezOverThinking - AI Anxiety Amplifier",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/ezoverthinking',
        'Report a bug': "https://github.com/your-repo/ezoverthinking/issues",
        'About': "# ezOverThinking\nThe AI-powered overthinking amplification system!"
    }
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom components
from components.chat_interface import ChatInterface
from components.analytics_dashboard import AnalyticsDashboard
from components.settings_page import SettingsPage
from components.real_time_handler import RealTimeHandler
from utils.api_client import APIClient
from utils.session_manager import SessionManager
from utils.theme_manager import ThemeManager

class EzOverThinkingApp:
    """Main application class for ezOverThinking"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.session_manager = SessionManager()
        self.theme_manager = ThemeManager()
        self.real_time_handler = RealTimeHandler()
        
        # Initialize session state
        self.initialize_session_state()
        
        # Apply custom styling
        self.apply_custom_styling()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        default_state = {
            'user_id': None,
            'authenticated': False,
            'conversation_history': [],
            'current_anxiety_level': 'calm',
            'analytics_data': {},
            'websocket_connected': False,
            'chat_messages': [],
            'typing_indicator': False,
            'current_page': 'chat',
            'settings': {
                'theme': 'dark',
                'notifications': True,
                'sound_effects': True,
                'auto_continue': False
            }
        }
        
        for key, value in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def apply_custom_styling(self):
        """Apply custom CSS styling"""
        st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary-color: #FF6B6B;
            --secondary-color: #4ECDC4;
            --accent-color: #45B7D1;
            --warning-color: #FFA07A;
            --danger-color: #FF4757;
            --success-color: #2ED573;
            --dark-bg: #1E1E1E;
            --light-bg: #F8F9FA;
        }
        
        /* Custom app header */
        .main-header {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            color: rgba(255,255,255,0.9);
            margin: 0;
            font-size: 1.1rem;
            font-style: italic;
        }
        
        /* Chat interface styling */
        .chat-container {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            min-height: 400px;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 12px;
            position: relative;
            animation: slideIn 0.3s ease-out;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: 2rem;
            text-align: right;
        }
        
        .agent-message {
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
            margin-right: 2rem;
        }
        
        .system-message {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            color: white;
            text-align: center;
            font-style: italic;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Anxiety level indicator */
        .anxiety-indicator {
            display: flex;
            align-items: center;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .anxiety-calm {
            background: linear-gradient(135deg, #2ED573, #7bed9f);
            color: white;
        }
        
        .anxiety-mild {
            background: linear-gradient(135deg, #FFA07A, #ffb347);
            color: white;
        }
        
        .anxiety-moderate {
            background: linear-gradient(135deg, #FF6B6B, #ff5252);
            color: white;
        }
        
        .anxiety-high {
            background: linear-gradient(135deg, #FF4757, #c44569);
            color: white;
        }
        
        .anxiety-extreme {
            background: linear-gradient(135deg, #8B0000, #B22222);
            color: white;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        /* Analytics dashboard styling */
        .analytics-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--primary-color);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
            margin: 0;
        }
        
        /* Sidebar styling */
        .sidebar-header {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #E0E0E0;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 2rem;
            }
            
            .chat-container {
                padding: 1rem;
            }
            
            .user-message, .agent-message {
                margin-left: 0.5rem;
                margin-right: 0.5rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header(self):
        """Render the main application header"""
        st.markdown("""
        <div class="main-header">
            <h1>🌪️ ezOverThinking</h1>
            <p>The AI-powered anxiety amplification system that helps you spiral deeper into overthinking!</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-header">
                <h3>🌪️ ezOverThinking</h3>
                <p>Navigation</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            pages = {
                "💬 Chat": "chat",
                "📊 Analytics": "analytics",
                "⚙️ Settings": "settings",
                "ℹ️ About": "about"
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # Connection status
            status_color = "🟢" if st.session_state.websocket_connected else "🔴"
            st.markdown(f"**Connection Status:** {status_color}")
            
            # Current anxiety level
            anxiety_level = st.session_state.current_anxiety_level
            anxiety_colors = {
                'calm': '🟢',
                'mild': '🟡',
                'moderate': '🟠',
                'high': '🔴',
                'extreme': '🆘'
            }
            
            st.markdown(f"**Anxiety Level:** {anxiety_colors.get(anxiety_level, '🤔')} {anxiety_level.title()}")
            
            # Quick stats
            st.markdown("---")
            st.markdown("**📊 Quick Stats**")
            st.metric("Messages Today", len(st.session_state.chat_messages))
            st.metric("Conversations", len(st.session_state.conversation_history))
            
            # Emergency controls
            st.markdown("---")
            st.markdown("**🚨 Emergency Controls**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reset", use_container_width=True):
                    self.reset_conversation()
            
            with col2:
                if st.button("🛑 Stop", use_container_width=True):
                    self.stop_conversation()
    
    def render_main_content(self):
        """Render the main content area based on current page"""
        page = st.session_state.current_page
        
        if page == "chat":
            self.render_chat_page()
        elif page == "analytics":
            self.render_analytics_page()
        elif page == "settings":
            self.render_settings_page()
        elif page == "about":
            self.render_about_page()
    
    def render_chat_page(self):
        """Render the chat interface page"""
        st.markdown("## 💬 Chat Interface")
        
        # Initialize chat interface
        chat_interface = ChatInterface(
            api_client=self.api_client,
            real_time_handler=self.real_time_handler
        )
        
        # Render chat interface
        chat_interface.render()
    
    def render_analytics_page(self):
        """Render the analytics dashboard page"""
        st.markdown("## 📊 Analytics Dashboard")
        
        # Initialize analytics dashboard
        analytics_dashboard = AnalyticsDashboard(
            api_client=self.api_client
        )
        
        # Render analytics dashboard
        analytics_dashboard.render()
    
    def render_settings_page(self):
        """Render the settings page"""
        st.markdown("## ⚙️ Settings")
        
        # Initialize settings page
        settings_page = SettingsPage(
            session_manager=self.session_manager,
            theme_manager=self.theme_manager
        )
        
        # Render settings page
        settings_page.render()
    
    def render_about_page(self):
        """Render the about page"""
        st.markdown("## ℹ️ About ezOverThinking")
        
        st.markdown("""
        ### Welcome to ezOverThinking! 🌪️
        
        The revolutionary AI-powered system designed to help you spiral deeper into overthinking 
        by asking progressively more anxious questions about your everyday concerns.
        
        #### How it works:
        1. **Share your worry** - Tell us what's bothering you
        2. **Meet the agents** - Our specialized AI agents take over
        3. **Spiral deeper** - Watch as simple concerns become elaborate disasters
        4. **Track your anxiety** - Monitor your escalating worry levels
        5. **Analyze patterns** - Discover your unique overthinking style
        
        #### Our AI Agents:
        - 🎭 **Dr. Intake McTherapy** - Your friendly intake specialist
        - 💥 **Professor Catastrophe Von Doomsworth** - Master of disaster scenarios
        - ⏰ **Dr. Ticktock McUrgency** - Time pressure anxiety expert
        - 📊 **Dr. Probability McStatistics** - Fake statistics specialist
        - 👥 **Professor Socially Awkward** - Social anxiety amplifier
        - 🎪 **Dr. Comfort McBackstab** - False comfort provider
        
        #### Technology Stack:
        - **Frontend**: Streamlit with custom styling
        - **Backend**: FastAPI with async support
        - **Real-time**: WebSocket communication
        - **AI**: Multi-agent coordination system
        - **Analytics**: Real-time insights and trends
        - **State Management**: Redis-based persistence
        
        #### Disclaimer:
        This application is for entertainment and educational purposes only. 
        If you're experiencing real anxiety, please consult with a mental health professional.
        
        ---
        
        **Built with ❤️ for your portfolio showcase**
        """)
        
        # Technical details
        with st.expander("🔧 Technical Details"):
            st.markdown("""
            #### Architecture:
            - **Multi-agent AI system** with 6 specialized agents
            - **Real-time communication** using WebSockets
            - **Scalable backend** with FastAPI and async processing
            - **Interactive frontend** with Streamlit and custom CSS
            - **Analytics dashboard** with real-time insights
            - **State management** with Redis persistence
            
            #### Features:
            - Real-time chat with AI agents
            - Anxiety level tracking and visualization
            - Conversation pattern analysis
            - Multi-user support with session isolation
            - Comprehensive analytics and insights
            - Responsive design for mobile devices
            
            #### Portfolio Highlights:
            - Advanced AI agent coordination
            - Real-time web application development
            - Modern frontend with custom styling
            - Production-ready backend architecture
            - Comprehensive testing and validation
            - Creative problem-solving with humor
            """)
    
    def reset_conversation(self):
        """Reset the current conversation"""
        try:
            self.api_client.reset_conversation()
            st.session_state.chat_messages = []
            st.session_state.conversation_history = []
            st.session_state.current_anxiety_level = 'calm'
            st.success("🔄 Conversation reset successfully!")
        except Exception as e:
            st.error(f"❌ Error resetting conversation: {e}")
    
    def stop_conversation(self):
        """Stop the current conversation"""
        try:
            st.session_state.chat_messages = []
            st.session_state.typing_indicator = False
            st.success("🛑 Conversation stopped!")
        except Exception as e:
            st.error(f"❌ Error stopping conversation: {e}")
    
    def run(self):
        """Run the main application"""
        # Render header
        self.render_header()
        
        # Render sidebar
        self.render_sidebar()
        
        # Render main content
        self.render_main_content()
        
        # Initialize real-time connection if not connected
        if not st.session_state.websocket_connected:
            self.real_time_handler.initialize_connection()

def main():
    """Main application entry point"""
    app = EzOverThinkingApp()
    app.run()

if __name__ == "__main__":
    main()