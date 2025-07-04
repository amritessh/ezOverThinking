import os
import logging
from typing import Optional, List
import google.generativeai as genai
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger(__name__)

class GeminiLLMService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini LLM service
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model_name: Gemini model to use (default: gemini-1.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized Gemini LLM service with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model {model_name}: {e}")
            raise
    
    async def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a response using Gemini
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens for response
            
        Returns:
            Generated response text
        """
        try:
            logger.info(f"Generating Gemini response with prompt length: {len(prompt)}")
            
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.8,
                    top_p=0.9,
                    top_k=40
                )
            )
            
            result = response.text if response.text else ""
            logger.info(f"Gemini response length: {len(result)}")
            
            if not result:
                logger.warning("Gemini returned empty response")
                return "I'm having trouble thinking about this right now. Let me try to overthink something else for you."
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return "My overthinking circuits are temporarily malfunctioning. Please try again in a moment."
    
    async def ainvoke(self, messages: List[BaseMessage]) -> AIMessage:
        """
        Async interface compatible with LangChain's LLM interface
        
        Args:
            messages: List of messages (HumanMessage, AIMessage, etc.)
            
        Returns:
            AIMessage with generated response
        """
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        response_text = await self.generate_response(prompt)
        return AIMessage(content=response_text)
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert a list of messages to a single prompt string
        
        Args:
            messages: List of BaseMessage objects
            
        Returns:
            Combined prompt string
        """
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                prompt_parts.append(f"User: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                # For other message types, just include the content
                prompt_parts.append(f"{message.content}")
        
        return "\n\n".join(prompt_parts)
    
    def __call__(self, prompt: str) -> str:
        """
        Synchronous interface for backward compatibility
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        import asyncio
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                # For now, return a placeholder
                return "Async call not supported in sync context"
            else:
                return loop.run_until_complete(self.generate_response(prompt))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.generate_response(prompt)) 