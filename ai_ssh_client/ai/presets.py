"""Pre-defined configurations for popular AI providers"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProviderPreset:
    name: str
    display_name: str
    default_model: str
    base_url: str
    description: str
    extra_headers: Dict[str, str] = None

PRESETS: List[ProviderPreset] = [
    ProviderPreset(
        name="openai",
        display_name="OpenAI",
        default_model="gpt-3.5-turbo",
        base_url="https://api.openai.com/v1",
        description="Official OpenAI API"
    ),
    ProviderPreset(
        name="tongyi",
        display_name="通义千问 (Alibaba)",
        default_model="qwen-turbo",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="阿里云通义千问"
    ),
    ProviderPreset(
        name="wenxin",
        display_name="文心一言 (Baidu)",
        default_model="ernie-3.5-8k",
        base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/",
        description="百度文心一言"
    ),
    ProviderPreset(
        name="doubao",
        display_name="豆包 (ByteDance)",
        default_model="doubao-pro-4k",
        base_url="https://aquasearch.volcengineapi.com/endpoint/https://openshift.ai-bj-tj.bytegoofy.com/v1",
        description="字节跳动豆包"
    ),
    ProviderPreset(
        name="xinghuo",
        display_name="讯飞星火 (iFlytek)",
        default_model="spark-v3.5",
        base_url="https://spark-api-open.xf-yun.com/v1",
        description="科大讯飞星火"
    ),
    ProviderPreset(
        name="claude",
        display_name="Anthropic Claude",
        default_model="claude-3-sonnet-20240229",
        base_url="https://api.anthropic.com/v1",
        description="Anthropic Claude (via OpenAI proxy)",
        extra_headers={"anthropic-version": "2023-06-01"}
    ),
    ProviderPreset(
        name="gemini",
        display_name="Google Gemini",
        default_model="gemini-pro",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="Google Gemini"
    ),
    ProviderPreset(
        name="ollama",
        display_name="Ollama Local",
        default_model="llama3",
        base_url="http://localhost:11434/v1",
        description="Local Ollama (OpenAI-compatible mode)"
    ),
    ProviderPreset(
        name="custom",
        display_name="Custom",
        default_model="",
        base_url="",
        description="Custom OpenAI-compatible API"
    )
]

def get_preset_by_name(name: str) -> Optional[ProviderPreset]:
    """Get preset by name"""
    for preset in PRESETS:
        if preset.name == name:
            return preset
    return None

def get_preset_options() -> List[tuple[str, str]]:
    """Get options for Select widget"""
    return [(p.display_name, p.name) for p in PRESETS]
