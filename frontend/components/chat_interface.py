# frontend/components/chat_interface.py
"""
Chat Interface Component - Real-time conversation with AI agents
"""

import streamlit as st
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ChatInterface:
    """Interactive chat interface with real-time AI agent communication"""
    
    def __init__(self, api_client, real_time_handler):
        self.api_client = api_client
        self.real_time_handler = real_time_handler
        
        # Initialize chat state
        self.initialize_chat_state()
    
    def initialize_chat_state(self):
        """Initialize chat-specific session state"""
        chat_defaults = {
            'chat_input': '',
            'auto_scroll': True,
            'show_agent_details': True,
            'chat_mode': 'realtime',  # 'realtime' or 'batch'
            'typing_simulation': True,
            'sound_enabled': True
        }
        
        for key, value in chat_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render(self):
        """Render the complete chat interface"""
        # Chat controls
        self.render_chat_controls()
        
        # Chat container
        self.render_chat_container()
        
        # Input area
        self.render_input_area()
        
        # Agent status
        if st.session_state.show_agent_details:
            self.render_agent_status()
    
    def render_chat_controls(self):
        """Render chat control buttons and options"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            chat_mode = st.selectbox(
                "Mode",
                ["realtime", "batch"],
                index=0 if st.session_state.chat_mode == "realtime" else 1,
                key="chat_mode_select"
            )
            if chat_mode != st.session_state.chat_mode:
                st.session_state.chat_mode = chat_mode
                st.rerun()
        
        with col2:
            if st.button("🔄 Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        
        with col3:
            if st.button("📥 Export Chat", use_container_width=True):
                self.export_chat_history()
        
        with col4:
            st.session_state.show_agent_details = st.checkbox(
                "Show Agent Details",
                value=st.session_state.show_agent_details
            )
    
    def render_chat_container(self):
        """Render the main chat message container"""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Chat header
        self.render_chat_header()
        
        # Messages container
        chat_placeholder = st.container()
        
        with chat_placeholder:
            # Welcome message if no messages
            if not st.session_state.chat_messages:
                self.render_welcome_message()
            else:
                # Render all messages
                for message in st.session_state.chat_messages:
                    self.render_message(message)
                
                # Typing indicator
                if st.session_state.typing_indicator:
                    self.render_typing_indicator()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_chat_header(self):
        """Render chat header with status"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("### 💬 Chat with AI Agents")
        
        with col2:
            # Connection status
            if st.session_state.websocket_connected:
                st.markdown("🟢 **Connected**")
            else:
                st.markdown("🔴 **Disconnected**")
        
        with col3:
            # Message count
            msg_count = len(st.session_state.chat_messages)
            st.markdown(f"**Messages:** {msg_count}")
    
    def render_welcome_message(self):
        """Render welcome message for new users"""
        welcome_html = """
        <div class="chat-message system-message">
            <h4>🌪️ Welcome to ezOverThinking!</h4>
            <p>Ready to spiral into anxiety? Share any worry or concern, and our AI agents will help you overthink it to the maximum!</p>
            <p><strong>Try asking about:</strong></p>
            <ul>
                <li>A friend who didn't text you back</li>
                <li>An upcoming presentation or meeting</li>
                <li>A weird noise your car is making</li>
                <li>Someone who looked at you funny</li>
                <li>Literally anything that's on your mind!</li>
            </ul>
            <p><em>Our specialized agents are standing by to escalate your concerns into full-blown catastrophes! 😈</em></p>
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)
    
    def render_message(self, message: Dict[str, Any]):
        """Render a single chat message"""
        msg_type = message.get('type', 'user')
        content = message.get('content', '')
        timestamp = message.get('timestamp', datetime.now())
        agent_name = message.get('agent_name', '')
        anxiety_level = message.get('anxiety_level', 'calm')
        
        # Format timestamp
        time_str = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
        
        if msg_type == 'user':
            self.render_user_message(content, time_str)
        elif msg_type == 'agent':
            self.render_agent_message(content, agent_name, anxiety_level, time_str)
        elif msg_type == 'system':
            self.render_system_message(content, time_str)
        elif msg_type == 'anxiety_update':
            self.render_anxiety_update(anxiety_level, time_str)
    
    def render_user_message(self, content: str, timestamp: str):
        """Render user message"""
        message_html = f"""
        <div class="chat-message user-message">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">
                👤 You <span style="opacity: 0.7; font-size: 0.8rem;">({timestamp})</span>
            </div>
            <div>{content}</div>
        </div>
        """
        st.markdown(message_html, unsafe_allow_html=True)
    
    def render_agent_message(self, content: str, agent_name: str, anxiety_level: str, timestamp: str):
        """Render AI agent message"""
        # Agent emojis
        agent_emojis = {
            'IntakeSpecialistAgent': '🎭',
            'CatastropheEscalatorAgent': '💥',
            'TimelinePanicGeneratorAgent': '⏰',
            'ProbabilityTwisterAgent': '📊',
            'SocialAnxietyAmplifierAgent': '👥',
            'FalseComfortProviderAgent': '🎪'
        }
        
        emoji = agent_emojis.get(agent_name, '🤖')
        display_name = agent_name.replace('Agent', '').replace('Specialist', '').replace('Escalator', '').replace('Generator', '').replace('Twister', '').replace('Amplifier', '').replace('Provider', '')
        
        # Anxiety level indicator
        anxiety_indicators = {
            'calm': '🟢',
            'mild': '🟡',
            'moderate': '🟠',
            'high': '🔴',
            'extreme': '🆘'
        }
        
        anxiety_indicator = anxiety_indicators.get(anxiety_level, '🤔')
        
        message_html = f"""
        <div class="chat-message agent-message">
            <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <span>{emoji} {display_name}</span>
                <span style="opacity: 0.7; font-size: 0.8rem;">
                    {anxiety_indicator} {anxiety_level.title()} ({timestamp})
                </span>
            </div>
            <div>{content}</div>
        </div>
        """
        st.markdown(message_html, unsafe_allow_html=True)
    
    def render_system_message(self, content: str, timestamp: str):
        """Render system message"""
        message_html = f"""
        <div class="chat-message system-message">
            <div style="font-weight: 600; margin-bottom: 0.5rem;">
                🔔 System <span style="opacity: 0.7; font-size: 0.8rem;">({timestamp})</span>
            </div>
            <div>{content}</div>
        </div>
        """
        st.markdown(message_html, unsafe_allow_html=True)
    
    def render_anxiety_update(self, anxiety_level: str, timestamp: str):
        """Render anxiety level update"""
        anxiety_colors = {
            'calm': '#2ED573',
            'mild': '#FFA07A', 
            'moderate': '#FF6B6B',
            'high': '#FF4757',
            'extreme': '#8B0000'
        }
        
        color = anxiety_colors.get(anxiety_level, '#4ECDC4')
        
        update_html = f"""
        <div class="chat-message" style="background: {color}; color: white; text-align: center; font-weight: 600;">
            🌡️ Anxiety Level Updated: {anxiety_level.title()} ({timestamp})
        </div>
        """
        st.markdown(update_html, unsafe_allow_html=True)
    
    def render_typing_indicator(self):
        """Render typing indicator"""
        typing_html = """
        <div class="chat-message agent-message" style="opacity: 0.7;">
            <div style="display: flex; align-items: center;">
                <div style="margin-right: 1rem;">🤖 AI Agent is typing</div>
                <div class="typing-dots">
                    <span>●</span>
                    <span>●</span>
                    <span>●</span>
                </div>
            </div>
        </div>
        
        <style>
        .typing-dots span {
            animation: typing 1.4s infinite;
            opacity: 0.4;
        }
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.4; }
            30% { opacity: 1; }
        }
        </style>
        """
        st.markdown(typing_html, unsafe_allow_html=True)
    
    def render_input_area(self):
        """Render message input area"""
        st.markdown("### 💭 Share Your Worry")
        
        # Input form
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_area(
                    "",
                    placeholder="What's bothering you? Don't hold back - we'll help you make it worse! 😈",
                    height=100,
                    key="chat_input_area"
                )
            
            with col2:
                submit_button = st.form_submit_button(
                    "🌪️ Send",
                    use_container_width=True,
                    type="primary"
                )
                
                continue_button = st.form_submit_button(
                    "➡️ Continue",
                    use_container_width=True
                )
        
        # Handle form submission
        if submit_button and user_input.strip():
            self.handle_user_input(user_input.strip())
        
        if continue_button:
            self.handle_continue_conversation()
        
        # Quick action buttons
        self.render_quick_actions()
    
    def render_quick_actions(self):
        """Render quick action buttons"""
        st.markdown("#### 🚀 Quick Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📱 Phone Worry", use_container_width=True):
                self.handle_user_input("My friend hasn't texted me back in 2 hours")
        
        with col2:
            if st.button("🎤 Presentation Panic", use_container_width=True):
                self.handle_user_input("I have a presentation tomorrow and I'm worried")
        
        with col3:
            if st.button("👥 Social Anxiety", use_container_width=True):
                self.handle_user_input("Someone looked at me weird today")
        
        with col4:
            if st.button("🏥 Health Concern", use_container_width=True):
                self.handle_user_input("I have a small headache")
    
    def render_agent_status(self):
        """Render current agent status"""
        st.markdown("---")
        st.markdown("### 🤖 Agent Status")
        
        agents = [
            {'name': 'Dr. Intake McTherapy', 'emoji': '🎭', 'status': 'Ready', 'specialty': 'Friendly trap'},
            {'name': 'Prof. Catastrophe', 'emoji': '💥', 'status': 'Standby', 'specialty': 'Disaster scenarios'},
            {'name': 'Dr. Ticktock McUrgency', 'emoji': '⏰', 'status': 'Waiting', 'specialty': 'Time pressure'},
            {'name': 'Dr. Probability', 'emoji': '📊', 'status': 'Ready', 'specialty': 'Fake statistics'},
            {'name': 'Prof. Socially Awkward', 'emoji': '👥', 'status': 'Active', 'specialty': 'Social disasters'},
            {'name': 'Dr. Comfort McBackstab', 'emoji': '🎪', 'status': 'Ready', 'specialty': 'False hope'}
        ]
        
        # Create agent status grid
        cols = st.columns(3)
        for i, agent in enumerate(agents):
            with cols[i % 3]:
                status_color = {
                    'Ready': '🟢',
                    'Active': '🟡',
                    'Standby': '⚪',
                    'Waiting': '🔵'
                }.get(agent['status'], '⚪')
                
                st.markdown(f"""
                <div class="analytics-card" style="margin-bottom: 1rem; padding: 1rem;">
                    <div style="font-weight: 600; font-size: 1.1rem;">
                        {agent['emoji']} {agent['name']}
                    </div>
                    <div style="margin: 0.5rem 0; opacity: 0.8;">
                        {agent['specialty']}
                    </div>
                    <div style="display: flex; align-items: center;">
                        {status_color} <span style="margin-left: 0.5rem;">{agent['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def handle_user_input(self, user_input: str):
        """Handle user input and send to agents"""
        try:
            # Add user message to chat
            user_message = {
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            }
            st.session_state.chat_messages.append(user_message)
            
            # Show typing indicator
            st.session_state.typing_indicator = True
            
            # Process based on chat mode
            if st.session_state.chat_mode == 'realtime':
                self.process_realtime_message(user_input)
            else:
                self.process_batch_message(user_input)
            
            # Rerun to update UI
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error handling user input: {e}")
            st.error(f"❌ Error processing your message: {e}")
    
    def process_realtime_message(self, user_input: str):
        """Process message in real-time mode"""
        try:
            # Send via WebSocket if connected
            if st.session_state.websocket_connected:
                self.real_time_handler.send_message({
                    'type': 'user_concern',
                    'content': user_input
                })
            else:
                # Fallback to REST API
                self.process_via_api(user_input)
                
        except Exception as e:
            logger.error(f"Error in real-time processing: {e}")
            # Fallback to batch processing
            self.process_batch_message(user_input)
    
    def process_batch_message(self, user_input: str):
        """Process message in batch mode"""
        try:
            response = self.api_client.send_message(user_input)
            
            # Add agent responses
            for agent_response in response.get('responses', []):
                agent_message = {
                    'type': 'agent',
                    'content': agent_response.get('content', ''),
                    'agent_name': agent_response.get('agent_name', ''),
                    'anxiety_level': agent_response.get('anxiety_level', 'calm'),
                    'timestamp': datetime.now()
                }
                st.session_state.chat_messages.append(agent_message)
            
            # Update anxiety level
            if 'anxiety_level' in response:
                st.session_state.current_anxiety_level = response['anxiety_level']
                
                # Add anxiety update message
                anxiety_message = {
                    'type': 'anxiety_update',
                    'anxiety_level': response['anxiety_level'],
                    'timestamp': datetime.now()
                }
                st.session_state.chat_messages.append(anxiety_message)
            
            # Turn off typing indicator
            st.session_state.typing_indicator = False
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            st.error(f"❌ Error processing your message: {e}")
            st.session_state.typing_indicator = False
    
    def process_via_api(self, user_input: str):
        """Process message via REST API"""
        try:
            response = self.api_client.send_message(user_input)
            self.handle_api_response(response)
        except Exception as e:
            logger.error(f"Error processing via API: {e}")
            st.error(f"❌ API Error: {e}")
    
    def handle_api_response(self, response: Dict[str, Any]):
        """Handle API response and update chat"""
        try:
            # Add agent responses
            for agent_response in response.get('responses', []):
                agent_message = {
                    'type': 'agent',
                    'content': agent_response.get('content', ''),
                    'agent_name': agent_response.get('agent_name', ''),
                    'anxiety_level': agent_response.get('anxiety_level', 'calm'),
                    'timestamp': datetime.now()
                }
                st.session_state.chat_messages.append(agent_message)
            
            # Update session state
            if 'anxiety_level' in response:
                st.session_state.current_anxiety_level = response['anxiety_level']
            
            # Turn off typing indicator
            st.session_state.typing_indicator = False
            
        except Exception as e:
            logger.error(f"Error handling API response: {e}")
            st.session_state.typing_indicator = False
    
    def handle_continue_conversation(self):
        """Handle continue conversation button"""
        try:
            if st.session_state.chat_mode == 'realtime':
                self.real_time_handler.send_message({
                    'type': 'continue_conversation'
                })
            else:
                response = self.api_client.continue_conversation()
                self.handle_api_response(response)
            
            st.session_state.typing_indicator = True
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            st.error(f"❌ Error continuing conversation: {e}")
    
    def export_chat_history(self):
        """Export chat history"""
        try:
            # Prepare export data
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'message_count': len(st.session_state.chat_messages),
                'current_anxiety_level': st.session_state.current_anxiety_level,
                'messages': []
            }
            
            for msg in st.session_state.chat_messages:
                export_msg = {
                    'type': msg.get('type', ''),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', '').isoformat() if isinstance(msg.get('timestamp'), datetime) else str(msg.get('timestamp', '')),
                    'agent_name': msg.get('agent_name', ''),
                    'anxiety_level': msg.get('anxiety_level', '')
                }
                export_data['messages'].append(export_msg)
            
            # Convert to JSON
            json_data = json.dumps(export_data, indent=2)
            
            # Create download button
            st.download_button(
                label="📥 Download Chat History",
                data=json_data,
                file_name=f"ezoverthinking_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.success("📥 Chat history prepared for download!")
            
        except Exception as e:
            logger.error(f"Error exporting chat history: {e}")
            st.error(f"❌ Error exporting chat: {e}")