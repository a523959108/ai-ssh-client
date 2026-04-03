"""Protocol factory - create protocol instance based on connection config"""

from typing import Optional
from .base import BaseProtocol, get_default_port
from .ssh import SSHProtocol
from .telnet import TelnetProtocol
from .mosh import MoshProtocol
from ai_ssh_client.config.settings import ConnectionConfig

def create_protocol(config: ConnectionConfig) -> BaseProtocol:
    """Create protocol based on connection config"""
    
    # Fill in default port if not specified
    if config.port is None:
        # We need to cheat since pydantic doesn't allow dynamic default
        object.__setattr__(config, 'port', get_default_port(config.protocol))
    
    if config.protocol == "ssh":
        return SSHProtocol(config)
    elif config.protocol == "telnet":
        return TelnetProtocol(config)
    elif config.protocol == "mosh":
        return MoshProtocol(config)
    elif config.protocol == "sftp":
        # SFTP will be implemented later for file browsing
        return SSHProtocol(config)  # Fallback to SSH for now
    else:
        # Default to SSH
        return SSHProtocol(config)
