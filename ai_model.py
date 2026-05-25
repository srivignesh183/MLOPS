import os
from typing import Generator, List
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class GeminiChatSession:
    """
    Manages a stateful conversation with Google Gemini models using the modern google-genai SDK.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash", system_instruction: str = None):
        """
        Initializes the Gemini Client and Chat session.
        If api_key is not provided, the SDK automatically tries to load GEMINI_API_KEY from environment variables.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API Key is not set. Please set the GEMINI_API_KEY environment variable, "
                "add it to a .env file, or provide it during initialization."
            )
            
        # Initialize client with explicit API key
        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.system_instruction = system_instruction
        self.chat = None
        
        # Start a clean chat session
        self.reset_chat()

    def _get_config(self) -> types.GenerateContentConfig:
        """Helper to build GenerateContentConfig configuration object."""
        config_args = {"temperature": 0.7}
        if self.system_instruction:
            config_args["system_instruction"] = self.system_instruction
        return types.GenerateContentConfig(**config_args)

    def reset_chat(self):
        """Resets the chat history and starts a fresh session."""
        self.chat = self.client.chats.create(
            model=self.model,
            config=self._get_config()
        )

    def change_model(self, new_model: str):
        """
        Changes the model for the active chat session while preserving conversation history.
        """
        history = self.chat.get_history()
        self.model = new_model
        
        # Recreate session with new model and existing history
        self.chat = self.client.chats.create(
            model=self.model,
            config=self._get_config(),
            history=history
        )

    def update_system_instruction(self, new_instruction: str):
        """
        Updates the system instruction dynamically while preserving conversation history.
        """
        history = self.chat.get_history()
        self.system_instruction = new_instruction
        
        # Recreate session with updated config and existing history
        self.chat = self.client.chats.create(
            model=self.model,
            config=self._get_config(),
            history=history
        )

    def send_message_stream(self, message: str) -> Generator[str, None, None]:
        """
        Sends a message and yields response chunks in real-time.
        """
        response_stream = self.chat.send_message_stream(message)
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    def send_message(self, message: str) -> str:
        """
        Sends a message synchronously and returns the complete response text.
        """
        response = self.chat.send_message(message)
        return response.text or ""

    def get_history(self) -> List[types.Content]:
        """
        Returns the conversation history.
        """
        return self.chat.get_history()

    def get_formatted_history(self) -> List[dict]:
        """
        Formats history into a clean list of dictionaries for easier display.
        """
        formatted = []
        for content in self.get_history():
            role = content.role
            # Reconstruct content parts
            text_parts = []
            if content.parts:
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
            text = "".join(text_parts)
            formatted.append({
                "role": "User" if role == "user" else "Gemini",
                "text": text
            })
        return formatted
