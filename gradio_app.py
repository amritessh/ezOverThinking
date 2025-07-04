import gradio as gr
import requests

def chat(user_input, history):
    # Call your backend API
    try:
        response = requests.post(
            "http://localhost:8000/chat/send",
            json={"message": user_input, "user_id": "demo_user"}
        )
        data = response.json()
        
        # Parse the response correctly
        if "message" in data:
            agent_reply = data["message"]
        else:
            agent_reply = "(No response)"
            
    except Exception as e:
        agent_reply = f"Error: {e}"

    # Use OpenAI-style message dicts
    history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": agent_reply}
    ]
    return history

iface = gr.ChatInterface(
    fn=chat,
    title="ezOverThinking Chat",
    description="Chat with your AI-powered overthinking agents!",
    theme="soft",
    chatbot=gr.Chatbot(type="messages")  # Use the new message format
)

if __name__ == "__main__":
    iface.launch()