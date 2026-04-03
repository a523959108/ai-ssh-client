"""Base protocol interface"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from ai_ssh_client.config.settings import ConnectionConfig

class BaseProtocol(ABC):
    """Base interface for all connection protocols"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connected = False
        self.output_callback: Optional[Callable[[str], None]] = None
        self.command_complete_callback: Optional[Callable[[], None]] = None

    @abstractmethod
    def connect(self) -> tuple[bool, str]:
        """Connect to server"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected"""
        pass

    @abstractmethod
    def create_session(self, width: int = 80, height: int = 24) -> bool:
        """Create interactive session"""
        pass

    @abstractmethod
    def send_input(self, data: str) -> None:
        """Send input to session"""
        pass

    @abstractmethod
    def resize(self, width: int, height: int) -> None:
        """Resize terminal"""
        pass

    @abstractmethod
    def start(self, width: int = 80, height: int = 24) -> bool:
        """Start session with output monitoring"""
        pass

    def stop(self) -> None:
        """Stop the session"""
        pass

DEFAULT_PORTS = {
    "ssh": 22,
    "telnet": 23,
    "mosh": 22,  # Mosh uses SSH for initial connection
    "sftp": 22,
}

def get_default_port(protocol: str) -> int:
    """Get default port for protocol"""
    return DEFAULT_PORTS.get(protocol, 22)
