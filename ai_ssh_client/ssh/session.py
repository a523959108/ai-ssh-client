import select
import threading
from typing import Optional, Callable
import paramiko
from .connection import SSHConnection

class SSHSession:
    def __init__(self, connection: SSHConnection):
        self.connection = connection
        self.session: Optional[paramiko.Channel] = None
        self.output_callback: Optional[Callable[[str], None]] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, width: int = 80, height: int = 24) -> bool:
        """Start the SSH session"""
        self.session = self.connection.create_session(width, height)
        if not self.session:
            return False
        
        self._running = True
        self._thread = threading.Thread(target=self._read_output, daemon=True)
        self._thread.start()
        return True

    def _read_output(self) -> None:
        """Read output from SSH session in background thread"""
        while self._running and self.session:
            if self.session.recv_ready():
                data = self.session.recv(4096)
                if data and self.output_callback:
                    try:
                        text = data.decode('utf-8', errors='replace')
                        self.output_callback(text)
                    except Exception:
                        pass
            else:
                select.select([self.session], [], [], 0.1)

    def send_input(self, data: str) -> None:
        """Send input to SSH session"""
        if self.session and not self.session.closed:
            try:
                self.session.send(data.encode('utf-8'))
            except Exception:
                pass

    def resize(self, width: int, height: int) -> None:
        """Resize terminal"""
        self.connection.resize_pty(width, height)

    def stop(self) -> None:
        """Stop the session"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self.session:
            self.session.close()
