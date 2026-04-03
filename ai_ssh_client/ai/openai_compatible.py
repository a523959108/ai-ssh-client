from typing import Optional
from openai import OpenAI as OpenAIClient
from .base import BaseAIClient, build_command_prompt, build_explain_prompt, build_troubleshoot_prompt
from ..config.settings import OpenAICompatibleConfig

class OpenAICompatibleClient(BaseAIClient):
    """Generic OpenAI-compatible API client"""

    def __init__(self, config: OpenAICompatibleConfig):
        self.config = config
        self.client: Optional[OpenAIClient] = None
        if self.is_available():
            self.client = OpenAIClient(
                api_key=config.api_key,
                base_url=config.base_url,
                default_headers=config.extra_headers if config.extra_headers else None
            )

    def is_available(self) -> bool:
        return bool(self.config.api_key and self.config.api_key.strip() and 
                   self.config.base_url and self.config.base_url.strip() and
                   self.config.model and self.config.model.strip())

    def _complete(self, prompt: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return None
        except Exception as e:
            print(f"OpenAI-compatible API error: {e}")
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
