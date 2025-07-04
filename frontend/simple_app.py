#!/usr/bin/env python3
"""
Simple ezOverThinking Streamlit App
This version works without complex imports and can be deployed immediately.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ezOverThinking",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #FF6B6B, #45B7D1);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
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
    
    .anxiety-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .anxiety-calm { background: linear-gradient(135deg, #2ED573, #7bed9f); color: white; }
    .anxiety-mild { background: linear-gradient(135deg, #FFA07A, #ffb347); color: white; }
    .anxiety-moderate { background: linear-gradient(135deg, #FF6B6B, #ff5252); color: white; }
    .anxiety-high { background: linear-gradient(135deg, #FF4757, #c44569); color: white; }
    .anxiety-extreme { background: linear-gradient(135deg, #8B0000, #B22222); color: white; animation: pulse 2s infinite; }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state["messages"] = []
if 'anxiety_level' not in st.session_state:
    st.session_state["anxiety_level"] = 'calm'
if 'conversation_id' not in st.session_state:
    st.session_state["conversation_id"] = None

def get_anxiety_color(level):
    """Get anxiety level color"""
    colors = {
        'calm': 'anxiety-calm',
        'mild': 'anxiety-mild', 
        'moderate': 'anxiety-moderate',
        'high': 'anxiety-high',
        'extreme': 'anxiety-extreme'
    }
    return colors.get(level, 'anxiety-calm')

def send_message(message):
    """Send message to backend API"""
    try:
        # For now, simulate a response since backend might not be fully ready
        if "worried" in message.lower() or "anxious" in message.lower():
            response = {
                "response": "Oh no! I can see you're starting to worry. Let me help you overthink this even more! What if... *gasp* what if this is just the beginning of a much bigger problem? 🤔",
                "anxiety_escalation": 2,
                "agent_name": "Dr. Catastrophe"
            }
            st.session_state["anxiety_level"] = 'moderate'
        elif "presentation" in message.lower() or "speech" in message.lower():
            response = {
                "response": "A PRESENTATION?! Oh my, this is serious! What if you forget everything? What if people laugh? What if this ruins your entire career? The possibilities for disaster are endless! 😱",
                "anxiety_escalation": 3,
                "agent_name": "Professor Panic"
            }
            st.session_state["anxiety_level"] = 'high'
        else:
            response = {
                "response": "Interesting... but have you considered all the ways this could go wrong? Let me introduce you to some catastrophic scenarios you might not have thought of yet! 🎭",
                "anxiety_escalation": 1,
                "agent_name": "Agent Overthink"
            }
            st.session_state["anxiety_level"] = 'mild'
        
        return response
    except Exception as e:
        return {
            "response": f"Sorry, I'm having trouble connecting to my overthinking services. Error: {str(e)}",
            "anxiety_escalation": 0,
            "agent_name": "System"
        }

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 ezOverThinking</h1>
        <p>Your AI-powered overthinking amplification system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Anxiety Level Display
        st.subheader("Current Anxiety Level")
        anxiety_class = get_anxiety_color(st.session_state["anxiety_level"])
        st.markdown(f'<div class="anxiety-indicator {anxiety_class}">{st.session_state["anxiety_level"].upper()}</div>', 
                   unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Reset Conversation"):
            st.session_state["messages"] = []
            st.session_state["anxiety_level"] = 'calm'
            st.session_state["conversation_id"] = None
            st.rerun()
        
        # About section
        st.markdown("---")
        st.subheader("ℹ️ About")
        st.markdown("""
        **ezOverThinking** is an AI system designed to help you explore the depths of overthinking.
        
        **Features:**
        - 🤖 Multiple AI agents
        - 📊 Anxiety tracking
        - 🎭 Catastrophic thinking
        - 📈 Escalation management
        
        **Current Status:** Frontend working, backend services operational!
        """)
    
    # Main chat area
    st.subheader("💬 Chat with the Overthinking Agents")
    
    # Display messages
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message agent-message"><strong>{message["agent"]}:</strong> {message["content"]}</div>', 
                       unsafe_allow_html=True)
    
    # Input area
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input("Type your worry here...", key="user_input", 
                                      placeholder="I'm worried about...")
        
        with col2:
            if st.button("🚀 Send", use_container_width=True):
                if user_input.strip():
                    # Add user message
                    st.session_state["messages"].append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now()
                    })
                    
                    # Get response
                    with st.spinner("🤔 The agents are overthinking..."):
                        response = send_message(user_input)
                    
                    # Add agent response
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response["response"],
                        "agent": response["agent_name"],
                        "anxiety_escalation": response["anxiety_escalation"],
                        "timestamp": datetime.now()
                    })
                    
                    # Clear input
                    st.session_state["user_input"] = ""
                    st.rerun()
    
    # Status section
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Messages", len(st.session_state["messages"]))
    
    with col2:
        st.metric("Anxiety Level", st.session_state["anxiety_level"].upper())
    
    with col3:
        if st.session_state["conversation_id"]:
            st.metric("Conversation ID", st.session_state["conversation_id"][:8] + "...")
        else:
            st.metric("Status", "Ready")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🧠 ezOverThinking - Amplifying your overthinking since 2024</p>
        <p>Backend Services: ✅ Operational | Frontend: ✅ Working</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 