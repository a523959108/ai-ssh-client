from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from ..config.settings import ConfigManager
from .screens.connect import ConnectScreen
from .screens.terminal import TerminalScreen
from .screens.ai_settings import AISettingsScreen

class AISSHApp(App):
    """AI-enhanced SSH Client"""
    
    TITLE = "AI SSH Client"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        ("ctrl+a", "ai_settings", "AI Settings"),
    ]
    
    CSS_PATH = "app.tcss"

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager("config.json")
        self.current_ai_client = None

    def on_mount(self) -> None:
        """Mount the app"""
        self.push_screen(ConnectScreen(self.config_manager))

    def connect_to_host(self, connection_config) -> None:
        """Switch to terminal screen after connection"""
        self.push_screen(TerminalScreen(connection_config, self.config_manager))

    def action_ai_settings(self) -> None:
        """Open AI settings screen"""
        self.push_screen(AISettingsScreen(self.config_manager))

if __name__ == "__main__":
    app = AISSHApp()
    app.run()
