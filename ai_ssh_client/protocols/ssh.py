"""SSH protocol implementation"""

import os
import paramiko
import threading
import time
import select
from typing import Optional, Callable, Tuple
from .base import BaseProtocol, get_default_port
from ai_ssh_client.config.settings import ConnectionConfig

class SSHProtocol(BaseProtocol):
    """SSH protocol handler"""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.client: Optional[paramiko.SSHClient] = None
        self.session: Optional[paramiko.Channel] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_output_time = 0

    def connect(self) -> Tuple[bool, str]:
        """Connect to SSH server"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            key_path = os.path.expanduser(self.config.key_path or "~/.ssh/id_rsa")
            
            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port or get_default_port("ssh"),
                "username": self.config.username,
                "timeout": 10
            }

            if self.config.auth_type == "password" and self.config.password:
                connect_kwargs["password"] = self.config.password
            elif self.config.auth_type == "key" and os.path.exists(key_path):
                connect_kwargs["key_filename"] = key_path
            elif self.config.auth_type == "certificate" and os.path.exists(key_path):
                connect_kwargs["key_filename"] = key_path
                if self.config.cert_path:
                    cert_path = os.path.expanduser(self.config.cert_path)
                    if os.path.exists(cert_path):
                        connect_kwargs["cert_file"] = cert_path
            elif self.config.auth_type == "agent":
                connect_kwargs["allow_agent"] = True
                connect_kwargs["look_for_keys"] = True

            self.client.connect(**connect_kwargs)
            self.connected = True
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
        """Close connection"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        if self.session:
            self.session.close()
        if self.client:
            self.client.close()
        self.connected = False

    def is_connected(self) -> bool:
        if not self.client or not self.connected:
            return False
        transport = self.client.get_transport()
        if transport is None:
            return False
        return transport.is_active()

    def create_session(self, width: int = 80, height: int = 24) -> bool:
        """Create interactive shell session"""
        if not self.is_connected():
            return False

        try:
            assert self.client is not None
            transport = self.client.get_transport()
            assert transport is not None
            self.session = transport.open_session()
            self.session.get_pty(width=width, height=height)
            self.session.invoke_shell()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False

    def send_input(self, data: str) -> None:
        """Send input to session"""
        if self.session and not self.session.closed:
            try:
                self.session.send(data.encode('utf-8'))
                self._last_output_time = time.time()
            except Exception:
                pass

    def resize(self, width: int, height: int) -> None:
        """Resize the pseudo-terminal"""
        if self.session:
            self.session.resize_pty(width=width, height=height)

    def _read_output(self) -> None:
        """Read output in background thread"""
        while self._running and self.session:
            if self.session.recv_ready():
                data = self.session.recv(4096)
                if data and self.output_callback:
                    try:
                        text = data.decode('utf-8', errors='replace')
                        self._last_output_time = time.time()
                        self.output_callback(text)
                    except Exception:
                        pass
            else:
                select.select([self.session], [], [], 0.1)

    def _monitor_completion(self) -> None:
        """Monitor for command completion when no output for a period of time"""
        while self._running:
            time.sleep(0.5)
            if (self.command_complete_callback and 
                self._last_output_time > 0 and 
                (time.time() - self._last_output_time) > 1.5):
                # No output for 1.5 seconds, consider command complete
                self.command_complete_callback()
                self._last_output_time = time.time()

    def start(self, width: int = 80, height: int = 24) -> bool:
        """Start session with output monitoring"""
        if not self.create_session(width, height):
            return False

        self._running = True
        self._last_output_time = time.time()
        self._thread = threading.Thread(target=self._read_output, daemon=True)
        self._thread.start()
        self._monitor_thread = threading.Thread(target=self._monitor_completion, daemon=True)
        self._monitor_thread.start()
        return True

    def stop(self) -> None:
        """Stop reading"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
