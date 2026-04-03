from typing import Optional
import requests
from .base import BaseAIClient, build_command_prompt, build_explain_prompt, build_troubleshoot_prompt
from ..config.settings import OllamaConfig

class OllamaClient(BaseAIClient):
    def __init__(self, config: OllamaConfig):
        self.config = config

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def _complete(self, prompt: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1
                    }
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            return None
        except Exception as e:
            print(f"Ollama API error: {e}")
            return None

    def generate_command(self, user_request: str, context: str = "") -> Optional[str]:
        prompt = build_command_prompt(user_request, context)
        return self._complete(prompt)

    def explain_command(self, command: str) -> Optional[str]:
        prompt = build_explain_prompt(command)
        return self._complete(prompt)

    def troubleshoot_error(self, command: str, error_output: str) -> Optional[str]:
        prompt = build_troubleshoot_prompt(command, error_output)
        return self._complete(prompt)
