"""AI client integration for command generation and troubleshooting"""

from typing import Optional
from .base import BaseAIClient
from .openai_client import OpenAILLMClient
from .ollama_client import OllamaClient
from ..config.settings import AppConfig, AIProvider

def create_ai_client(config: AppConfig) -> Optional[BaseAIClient]:
    """Create AI client based on configuration"""
    provider: AIProvider = config.ai.provider
    
    if provider == "openai":
        client = OpenAILLMClient(config.ai.openai)
        if client.is_available():
            return client
        return None
    elif provider == "ollama":
        client = OllamaClient(config.ai.ollama)
        if client.is_available():
            return client
        return None
    
    return None
