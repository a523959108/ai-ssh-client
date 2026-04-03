"""Telnet protocol implementation"""

import telnetlib
import threading
import time
from typing import Optional, Callable, Tuple
from .base import BaseProtocol, get_default_port
from ai_ssh_client.config.settings import ConnectionConfig

class TelnetProtocol(BaseProtocol):
    """Telnet protocol handler"""

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.tn: Optional[telnetlib.Telnet] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_output_time = 0

    def connect(self) -> Tuple[bool, str]:
        """Connect to Telnet server"""
        try:
            port = self.config.port or get_default_port("telnet")
            self.tn = telnetlib.Telnet(
                host=self.config.host,
                port=port,
                timeout=10
            )
            self.connected = True
            return True, "Connected successfully"
        except ConnectionRefusedError:
            return False, "Connection refused"
        except TimeoutError:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def disconnect(self) -> None:
        """Close connection"""
        self._running = False
        if self.tn:
            try:
                self.tn.close()
            except:
                pass
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected and self.tn is not None

    def create_session(self, width: int = 80, height: int = 24) -> bool:
        """Telnet doesn't need pty creation"""
        return True

    def send_input(self, data: str) -> None:
        """Send input"""
        if self.tn:
            try:
                self.tn.write(data.encode('utf-8'))
                self._last_output_time = time.time()
            except Exception:
                pass

    def resize(self, width: int, height: int) -> None:
        """Telnet doesn't support resize"""
        pass

    def _read_output(self) -> None:
        """Read output in background thread"""
        buffer = []
        while self._running and self.tn:
            try:
                data = self.tn.read_eager()
                if data:
                    text = data.decode('utf-8', errors='replace')
                    self._last_output_time = time.time()
                    if self.output_callback:
                        self.output_callback(text)
                    buffer.append(text)
            except Exception:
                break

        # Check completion after silence
        if self.command_complete_callback:
            self.command_complete_callback()

    def start(self, width: int = 80, height: int = 24) -> bool:
        """Start reading output"""
        if not self.is_connected():
            return False

        self._running = True
        self._thread = threading.Thread(target=self._read_output, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        """Stop reading"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
