"""Configuration management for the application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("PORT", "8000"))
    
    # Content limits
    MAX_SOURCE_TEXT_LENGTH = 50000  # 50k chars for fetched content
    MAX_OUTPUT_LENGTH = 3000  # 3k chars for final output
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment or .env file")
        return True

