import json
import os
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

AIProvider = Literal["openai", "ollama", "openai_compatible"]

ProtocolType = Literal["ssh", "mosh", "telnet", "sftp"]

class OpenAIConfig(BaseModel):
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    base_url: str = "https://api.openai.com/v1"

class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3"

class OpenAICompatibleConfig(BaseModel):
    """For OpenAI-compatible APIs like:
    - 通义千问 (https://dashscope.aliyuncs.com/compatibility/v1)
    - 文心一言 (https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat)
    - Claude Anthropic (via openai proxy)
    - Gemini Google (via openai proxy)
    - 豆包 Doubao (bytedance)
    - 讯飞星火
    """
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    extra_headers: Dict[str, str] = Field(default_factory=dict)

class AIConfig(BaseModel):
    provider: AIProvider = "openai"
    openai: OpenAIConfig = OpenAIConfig()
    ollama: OllamaConfig = OllamaConfig()
    openai_compatible: OpenAICompatibleConfig = OpenAICompatibleConfig()

class TerminalThemeConfig(BaseModel):
    """Per-connection terminal theme settings"""
    foreground: str = "#ffffff"
    background: str = "#0a0a0a"
    cursor: str = "#ffffff"
    selection: str = "#444444"
    font_size: int = 14
    font_family: str = "Menlo, Monaco, Consolas, monospace"

class ConnectionConfig(BaseModel):
    name: str
    protocol: ProtocolType = "ssh"
    host: str
    port: Optional[int] = None  # None means use default port for protocol
    username: Optional[str] = None
    auth_type: Literal["password", "key", "certificate", "agent"] = "key"
    password: Optional[str] = None
    key_path: str = "~/.ssh/id_rsa"
    cert_path: Optional[str] = "~/.ssh/id_rsa-cert.pub"
    # Port forwarding
    local_port_forward: Optional[str] = None  # format: local_port:remote_host:remote_port
    remote_port_forward: Optional[str] = None
    # Custom theme for this connection
    custom_theme: Optional[TerminalThemeConfig] = None
    # Saved commands for quick access
    saved_commands: List[str] = Field(default_factory=list)

class FavoriteCommand(BaseModel):
    """Saved favorite command/script for quick execution"""
    name: str
    command: str
    description: str = ""
    connection_filter: Optional[str] = None  # Only show for this connection pattern

class GlobalThemeConfig(BaseModel):
    mode: Literal["dark", "light"] = "dark"
    accent_color: str = "blue"
    default_font_size: int = 14
    default_font_family: str = "Menlo, Monaco, Consolas, monospace"

class AppConfig(BaseModel):
    ai: AIConfig = AIConfig()
    connections: List[ConnectionConfig] = Field(default_factory=list)
    theme: GlobalThemeConfig = GlobalThemeConfig()
    favorite_commands: List[FavoriteCommand] = Field(default_factory=list)
    command_history: List[str] = Field(default_factory=list)

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
