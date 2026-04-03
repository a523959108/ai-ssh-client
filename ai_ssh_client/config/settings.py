import json
import os
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

AIProvider = Literal["openai", "ollama"]

class OpenAIConfig(BaseModel):
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    base_url: str = "https://api.openai.com/v1"

class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3"

class AIConfig(BaseModel):
    provider: AIProvider = "openai"
    openai: OpenAIConfig = OpenAIConfig()
    ollama: OllamaConfig = OllamaConfig()

class ConnectionConfig(BaseModel):
    name: str
    host: str
    port: int = 22
    username: str
    auth_type: Literal["password", "key", "certificate", "agent"] = "key"
    password: Optional[str] = None
    key_path: str = "~/.ssh/id_rsa"
    cert_path: Optional[str] = "~/.ssh/id_rsa-cert.pub"

class ThemeConfig(BaseModel):
    mode: Literal["dark", "light"] = "dark"
    accent_color: str = "blue"

class AppConfig(BaseModel):
    ai: AIConfig = AIConfig()
    connections: List[ConnectionConfig] = Field(default_factory=list)
    theme: ThemeConfig = ThemeConfig()

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = os.path.abspath(config_path)
        self.config = self.load()

    def load(self) -> AppConfig:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig.model_validate(data)
        return AppConfig()

    def save(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config.model_dump(), f, indent=2, ensure_ascii=False)

    def get_config(self) -> AppConfig:
        return self.config

    def add_connection(self, connection: ConnectionConfig) -> None:
        self.config.connections.append(connection)
        self.save()

    def remove_connection(self, index: int) -> None:
        if 0 <= index < len(self.config.connections):
            del self.config.connections[index]
            self.save()
