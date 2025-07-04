import gradio as gr
import requests
import json
from datetime import datetime
from typing import Dict, List, Any


def chat_with_agent(message, history, agent_type="auto"):
    """Chat function that calls the backend API"""
    try:
        # Prepare the request payload
        payload = {
            "user_id": "demo_user",
            "message": message,
            "anxiety_level": "moderate",
        }

        # Add agent preference if specified
        if agent_type != "auto":
            payload["preferred_agent"] = agent_type

        response = requests.post(
            "http://localhost:8000/chat/send", json=payload, timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            agent_reply = data.get("message", "Sorry, I couldn't process that.")
            agent_name = data.get("agent_name", "Unknown Agent")
            anxiety_level = data.get("anxiety_level", 0)

            # Return just the agent reply (the agent name will be handled by the backend)
            return agent_reply, agent_name, anxiety_level
        else:
            return f"Error: {response.status_code} - {response.text}", "Error", 0

    except Exception as e:
        return f"Error connecting to backend: {str(e)}", "Error", 0


def clear_chat():
    """Clear the chat history"""
    return [], "", {"total_messages": 0, "current_anxiety": "Calm", "agents_used": []}


def get_anxiety_color(level):
    """Get color for anxiety level"""
    colors = {
        "calm": "#2ED573",
        "mild": "#FFA07A", 
        "moderate": "#FF6B6B",
        "high": "#FF4757",
        "extreme": "#8B0000"
    }
    return colors.get(level.lower(), "#2ED573")


def format_analytics(history, agents_used, anxiety_level):
    """Format analytics data for display"""
    total_messages = len(history) if history else 0
    
    # Count agent usage
    agent_counts = {}
    for agent in agents_used:
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    # Create analytics summary
    analytics_html = f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="margin: 0 0 0.5rem 0; color: #333;">📊 Conversation Analytics</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <strong>Total Messages:</strong> {total_messages}<br>
                <strong>Current Anxiety:</strong> 
                <span style="color: {get_anxiety_color(anxiety_level)}; font-weight: bold;">
                    {anxiety_level.title()}
                </span>
            </div>
            <div>
                <strong>Agents Used:</strong><br>
                {', '.join([f"{agent} ({count})" for agent, count in agent_counts.items()]) if agent_counts else 'None yet'}
            </div>
        </div>
    </div>
    """
    return analytics_html


# Create the Gradio interface
with gr.Blocks(title="ezOverThinking Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤔 ezOverThinking Chat")
    gr.Markdown("Chat with your AI-powered overthinking agents!")

    # Initialize analytics state
    analytics_state = gr.State({"total_messages": 0, "current_anxiety": "Calm", "agents_used": []})

    with gr.Row():
        with gr.Column(scale=3):
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat History",
                height=500,
                show_label=True,
                container=True,
                type="messages",
            )

            with gr.Row():
                message_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your worry here...",
                    lines=2,
                    max_lines=4,
                    scale=4,
                    show_label=False,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")

            # Analytics display
            analytics_display = gr.HTML(
                value=format_analytics([], [], "Calm"),
                label="Analytics"
            )

        with gr.Column(scale=1):
            # Conversation suggestions moved to right column
            gr.Markdown("### 💭 Try starting with one of these:")
            gr.Markdown("""
            - "I'm worried about my job interview tomorrow"
            - "What if my friends don't like me anymore?"
            - "I think I might be getting sick"
            - "I'm not sure if I made the right decision"
            - "What if something goes wrong with my presentation?"
            """)
            
            gr.Markdown("### Agent Options")
            agent_dropdown = gr.Dropdown(
                choices=[
                    "auto",
                    "intake_specialist",
                    "catastrophe_escalator",
                    "probability_twister",
                    "social_anxiety_amplifier",
                    "timeline_panic_generator",
                ],
                value="auto",
                label="Preferred Agent",
                info="Choose a specific agent or let the system decide",
            )

            # Anxiety level indicator
            gr.Markdown("### 🌡️ Current Anxiety Level")
            anxiety_indicator = gr.HTML(
                value='<div style="background: #2ED573; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: bold;">Calm</div>',
                label="Anxiety Level"
            )

            gr.Markdown("### About")
            gr.Markdown(
                """
            This system uses multiple AI agents to help you explore your worries and concerns.
            
            Each agent has a different approach to amplifying your overthinking in various ways.
            
            **Warning**: This is for entertainment purposes only. If you're experiencing real anxiety, please seek professional help.
            """
            )

    # Set up event handlers
    def handle_chat(message, history, agent_type, analytics):
        # Clean the message and check if it's empty
        message = message.strip() if message else ""
        if not message:
            return history, "", analytics, analytics["current_anxiety"]

        # Get agent response first
        agent_response, agent_name, anxiety_level = chat_with_agent(message, history, agent_type)

        # Add user message to history using new format
        history.append({"role": "user", "content": message})

        # Add agent response to history using new format
        history.append({"role": "assistant", "content": agent_response})

        # Update analytics
        analytics["total_messages"] = len(history)
        analytics["current_anxiety"] = anxiety_level.title() if anxiety_level else "Calm"
        if agent_name and agent_name != "Error":
            analytics["agents_used"].append(agent_name)

        # Update analytics display
        analytics_html = format_analytics(history, analytics["agents_used"], analytics["current_anxiety"])
        
        # Update anxiety indicator
        anxiety_color = get_anxiety_color(analytics["current_anxiety"])
        anxiety_html = f'<div style="background: {anxiety_color}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: bold;">{analytics["current_anxiety"]}</div>'

        # Clear the input field
        return history, "", analytics, analytics_html

    # Connect the send button and Enter key
    send_btn.click(
        handle_chat,
        inputs=[message_input, chatbot, agent_dropdown, analytics_state],
        outputs=[chatbot, message_input, analytics_state, anxiety_indicator],
    )

    # Enable Enter key submission (this should make Enter work)
    message_input.submit(
        handle_chat,
        inputs=[message_input, chatbot, agent_dropdown, analytics_state],
        outputs=[chatbot, message_input, analytics_state, anxiety_indicator],
        api_name="submit_message",
    )

    # Clear chat functionality
    def clear_all():
        empty_analytics = {"total_messages": 0, "current_anxiety": "Calm", "agents_used": []}
        empty_analytics_html = format_analytics([], [], "Calm")
        empty_anxiety_html = '<div style="background: #2ED573; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; font-weight: bold;">Calm</div>'
        return [], "", empty_analytics, empty_anxiety_html

    clear_btn.click(clear_all, outputs=[chatbot, message_input, analytics_state, anxiety_indicator])


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1", 
        server_port=7860, 
        share=True,  # Enable public link
        show_error=True
    )
