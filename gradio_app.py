import gradio as gr
import requests


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
            return agent_reply
        else:
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error connecting to backend: {str(e)}"


def clear_chat():
    """Clear the chat history"""
    return [], ""


# Create the Gradio interface
with gr.Blocks(title="ezOverThinking Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤔 ezOverThinking Chat")
    gr.Markdown("Chat with your AI-powered overthinking agents!")

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

            gr.Markdown("### About")
            gr.Markdown(
                """
            This system uses multiple AI agents to help you explore your worries and concerns.
            
            Each agent has a different approach to amplifying your overthinking in various ways.
            
            **Warning**: This is for entertainment purposes only. If you're experiencing real anxiety, please seek professional help.
            """
            )

    # Set up event handlers
    def handle_chat(message, history, agent_type):
        # Clean the message and check if it's empty
        message = message.strip() if message else ""
        if not message:
            return history, ""

        # Get agent response first
        agent_response = chat_with_agent(message, history, agent_type)

        # Add user message to history using new format
        history.append({"role": "user", "content": message})

        # Add agent response to history using new format
        history.append({"role": "assistant", "content": agent_response})

        # Clear the input field
        return history, ""

    # Connect the send button and Enter key
    send_btn.click(
        handle_chat,
        inputs=[message_input, chatbot, agent_dropdown],
        outputs=[chatbot, message_input],
    )

    # Enable Enter key submission (this should make Enter work)
    message_input.submit(
        handle_chat,
        inputs=[message_input, chatbot, agent_dropdown],
        outputs=[chatbot, message_input],
        api_name="submit_message",
    )

    # Clear chat functionality
    clear_btn.click(clear_chat, outputs=[chatbot, message_input])


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1", 
        server_port=7860, 
        share=True,  # Enable public link
        show_error=True
    )
