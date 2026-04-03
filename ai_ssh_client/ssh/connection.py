import os
import paramiko
from typing import Optional, Tuple
from ..config.settings import ConnectionConfig

class SSHConnection:
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.client: Optional[paramiko.SSHClient] = None
        self.session: Optional[paramiko.Channel] = None

    def connect(self) -> Tuple[bool, str]:
        """Connect to SSH server"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            key_path = os.path.expanduser(self.config.key_path)
            cert_path = self.config.cert_path
            if cert_path:
                cert_path = os.path.expanduser(cert_path)
            
            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port,
                "username": self.config.username,
                "timeout": 10
            }

            if self.config.auth_type == "password" and self.config.password:
                connect_kwargs["password"] = self.config.password
            elif self.config.auth_type == "key" and os.path.exists(key_path):
                connect_kwargs["key_filename"] = key_path
            elif self.config.auth_type == "certificate" and os.path.exists(key_path):
                connect_kwargs["key_filename"] = key_path
                if cert_path and os.path.exists(cert_path):
                    connect_kwargs["cert_file"] = cert_path
            elif self.config.auth_type == "agent":
                # Use SSH agent forwarding
                connect_kwargs["allow_agent"] = True
                connect_kwargs["look_for_keys"] = True

            self.client.connect(**connect_kwargs)
            return True, "Connected successfully"
        except paramiko.AuthenticationException:
            return False, "Authentication failed"
        except paramiko.SSHException as e:
            return False, f"SSH error: {str(e)}"
        except TimeoutError:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def disconnect(self) -> None:
        """Close the SSH connection"""
        if self.session:
            self.session.close()
        if self.client:
            self.client.close()

    def is_connected(self) -> bool:
        """Check if connected"""
        if self.client is None:
            return False
        transport = self.client.get_transport()
        if transport is None:
            return False
        return transport.is_active()

    def create_session(self, width: int = 80, height: int = 24) -> Optional[paramiko.Channel]:
        """Create interactive shell session"""
        if not self.is_connected():
            return None

        try:
            assert self.client is not None
            transport = self.client.get_transport()
            assert transport is not None
            self.session = transport.open_session()
            self.session.get_pty(width=width, height=height)
            self.session.invoke_shell()
            return self.session
        except Exception as e:
            print(f"Error creating session: {e}")
            return None

    def resize_pty(self, width: int, height: int) -> None:
        """Resize the pseudo-terminal"""
        if self.session:
            self.session.resize_pty(width=width, height=height)
