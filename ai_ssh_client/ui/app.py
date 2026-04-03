from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, TabbedContent, TabPane
)
from textual.containers import Horizontal
from ..config.settings import ConfigManager
from .screens.connect import ConnectScreen
from .screens.terminal import TerminalScreen
from .screens.ai_settings import AISettingsScreen

class AISSHApp(App):
    """AI-enhanced SSH Client with multi-tab support"""
    
    TITLE = "AI SSH Client"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+a", "ai_settings", "AI Settings"),
        ("ctrl+t", "new_tab", "New Tab"),
    ]
    
    CSS = """
    TabbedContent {
        height: 100%;
    }

    TabPane {
        padding: 0;
    }

    #connect-pane {
        height: 100%;
    }
    """

    CSS_PATH = "app.tcss"

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager("config.json")
        self.current_ai_client = None
        self.tab_counter = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield TabbedContent(
            TabPane(
                Static("Loading...", id="connect-pane"),
                id="tab-connect",
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Mount the app"""
        self.push_screen(ConnectScreen(self.config_manager))

    def connect_to_host(self, connection_config) -> None:
        """Open connection in new tab"""
        self.tab_counter += 1
        tab_id = f"tab-{self.tab_counter}"
        tab_name = connection_config.name or f"Session {self.tab_counter}"
        
        # The terminal screen will be pushed within this tab
        self.push_screen(TerminalScreen(connection_config, self.config_manager))

    def action_new_tab(self) -> None:
        """Open new connection tab"""
        self.push_screen(ConnectScreen(self.config_manager))

    def action_ai_settings(self) -> None:
        """Open AI settings screen"""
        self.push_screen(AISSettingsScreen(self.config_manager))

if __name__ == "__main__":
    app = AISSHApp()
    app.run()
