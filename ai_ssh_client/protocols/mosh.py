"""Mosh protocol implementation (wrapper around mosh-client)"""

import subprocess
import threading
import os
import select
from typing import Optional, Callable, Tuple
from .base import BaseProtocol, get_default_port
from ai_ssh_client.config.settings import ConnectionConfig

class MoshProtocol(BaseProtocol):
    """Mosh - Mobile Shell protocol
    Mosh provides roaming and UDP connectivity better for mobile
    Requires mosh-client must be installed on client and server
    """

    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.process: Optional[subprocess.Popen] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_output_time = 0

    def connect(self) -> Tuple[bool, str]:
        """Start mosh connection"""
        try:
            # Check if mosh-client is available
            if not self._is_mosh_available():
                return False, "mosh-client not found. Please install mosh first."

            port = self.config.port or get_default_port("mosh")
            
            cmd = ["mosh-client"]
            if self.config.username:
                cmd = ["mosh", f"{self.config.username}@{self.config.host}"]
            else:
                cmd = ["mosh", self.config.host]
            
            if self.config.port != 22:
                cmd.extend(["--ssh", f"ssh -p {port}"])

            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=False
                )
            except FileNotFoundError:
                return False, "mosh executable not found"

            self.connected = True
            return True, "Mosh connected successfully"
        except Exception as e:
            return False, f"Mosh connection error: {str(e)}"

    def _is_mosh_available(self) -> bool:
        """Check if mosh is available"""
        try:
            result = subprocess.run(["which", "mosh"], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def disconnect(self) -> None:
        """Terminate mosh process"""
        self._running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
        self.connected = False

    def is_connected(self) -> bool:
        if not self.connected or not self.process:
            return False
        return self.process.poll() is None

    def create_session(self, width: int = 80, height: int = 24) -> bool:
        """Set initial terminal size"""
        if self.process:
            # Mosh handles terminal itself, we just need to resize
            self.resize(width, height)
        return True

    def send_input(self, data: str) -> None:
        """Send input to mosh"""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(data.encode('utf-8'))
                self.process.stdin.flush()
            except Exception:
                pass

    def resize(self, width: int, height: int) -> None:
        """Resize terminal - handled by system, but mosh respects it"""
        # Mosh gets SIGWINCH, but we don't need to do anything special
        pass

    def _read_output(self) -> None:
        """Read output from mosh process"""
        if not self.process or not self.process.stdout:
            return

        while self._running:
            ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
            if ready:
                data = self.process.stdout.read(4096)
                if data:
                    text = data.decode('utf-8', errors='replace')
                    if self.output_callback:
                        self.output_callback(text)

    def start(self, width: int = 80, height: int = 24) -> bool:
        """Start output reading"""
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
