from abc import ABC, abstractmethod
from typing import Optional

class BaseAIClient(ABC):
    """Base interface for AI clients"""
    
    @abstractmethod
    def generate_command(self, user_request: str, context: str = "") -> Optional[str]:
        """Generate shell command from natural language request"""
        pass

    @abstractmethod
    def explain_command(self, command: str) -> Optional[str]:
        """Explain what a command does"""
        pass

    @abstractmethod
    def troubleshoot_error(self, command: str, error_output: str) -> Optional[str]:
        """Analyze error output and suggest solution"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI client is properly configured"""
        pass

SYSTEM_PROMPT = """You are an AI assistant integrated into an SSH client.
Your role is to help users with Linux/Unix command line tasks.

Follow these rules:
1. When generating commands, output ONLY the command, no extra explanation unless explanation is requested
2. Keep explanations clear and concise
3. When troubleshooting, explain the error and give the fix command
4. Always prefer standard Linux/Unix commands that are commonly available
"""

def build_command_prompt(request: str, context: str = "") -> str:
    prompt = SYSTEM_PROMPT + f"\n\nUser request: {request}\n"
    if context:
        prompt += f"Current context (recent output/commands): {context}\n"
    prompt += "\nGenerate the appropriate shell command. Output ONLY the command:"
    return prompt

def build_explain_prompt(command: str) -> str:
    return SYSTEM_PROMPT + f"\n\nExplain what this command does: {command}\n\nProvide clear explanation:"

def build_troubleshoot_prompt(command: str, error_output: str) -> str:
    return SYSTEM_PROMPT + f"\n\nCommand that failed: {command}\nError output:\n{error_output}\n\nAnalyze the problem and suggest the solution:"
