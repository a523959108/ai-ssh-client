from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Button, Input, Select, Label, 
    Checkbox, Footer, Header, ListView, ListItem
)
from textual.containers import Container, Vertical, Horizontal
from ..app import AISSHApp
from .ai_settings import AISettingsScreen
from ai_ssh_client.config.settings import ConfigManager, ConnectionConfig
from ai_ssh_client.protocols.factory import create_protocol

class ConnectScreen(Screen):
    """Connection selection screen"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Saved Connections", classes="title"),
            ListView(
                *[ListItem(Static(f"{conn.name} - {conn.username}@{conn.host}:{conn.port}")) 
                  for conn in self.config_manager.config.connections],
                id="connection-list"
            ) if self.config_manager.config.connections else Static("No saved connections", classes="empty"),
            Horizontal(
                Button("New Connection", id="new-connection"),
                Button("Quick Connect", id="quick-connect"),
                Button("AI Settings", id="ai-settings"),
                classes="buttons"
            ),
            id="connect-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new-connection":
            self.app.push_screen(NewConnectionScreen(self.config_manager))
        elif event.button.id == "quick-connect":
            self.app.push_screen(QuickConnectScreen(self.config_manager))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Connect to selected saved connection"""
        index = event.list_view.index
        if index is not None:
            connection_config = self.config_manager.config.connections[index]
            self._try_connect(connection_config)

    def _try_connect(self, connection_config: ConnectionConfig) -> None:
        """Attempt connection"""
        conn = create_protocol(connection_config)
        success, message = conn.connect()
        if success:
            self.app.connect_to_host(connection_config)
        else:
            self.notify(message, severity="error")

class NewConnectionScreen(Screen):
    """New connection creation screen"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("New Connection", classes="title"),
            Vertical(
                Horizontal(Label("Name:"), Input(placeholder="Connection name", id="name")),
                Horizontal(Label("Protocol:"), Select([
                    ("SSH", "ssh"),
                    ("Mosh", "mosh"),
                    ("Telnet", "telnet"),
                    ("SFTP", "sftp")
                ], id="protocol")),
                Horizontal(Label("Host:"), Input(placeholder="hostname or IP", id="host")),
                Horizontal(Label("Port:"), Input(placeholder="auto", id="port")),
                Horizontal(Label("Username:"), Input(placeholder="username", id="username")),
                Horizontal(Label("Auth:"), Select([
                    ("SSH Key", "key"), 
                    ("Password", "password"),
                    ("Certificate", "certificate"),
                    ("SSH Agent", "agent")
                ], id="auth_type")),
                Horizontal(Label("Key Path:"), Input(value="~/.ssh/id_rsa", id="key_path")),
                Horizontal(Label("Cert Path:"), Input(value="~/.ssh/id_rsa-cert.pub", id="cert_path")),
                Static("Custom Terminal Theme:", classes="section-title"),
                Horizontal(Label("Foreground:"), Input(value="#ffffff", id="theme-fg")),
                Horizontal(Label("Background:"), Input(value="#0a0a0a", id="theme-bg")),
                Horizontal(Label("Font Size:"), Input(value="14", id="font-size")),
                Horizontal(Label("Font:"), Input(value="Menlo, Monaco, Consolas", id="font-family")),
                classes="form"
            ),
            Horizontal(
                Button("Save", id="save"),
                Button("Cancel", id="cancel"),
                classes="buttons"
            ),
            id="new-connection-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save":
            self._save_connection()
            self.app.pop_screen()

    def _save_connection(self) -> None:
        name = self.query_one("#name", Input).value
        protocol = self.query_one("#protocol", Select).value
        host = self.query_one("#host", Input).value
        port_val = self.query_one("#port", Input).value
        port = int(port_val) if port_val else None
        username = self.query_one("#username", Input).value
        auth_type = self.query_one("#auth_type", Select).value
        key_path = self.query_one("#key_path", Input).value
        cert_path = self.query_one("#cert_path", Input).value
        
        # Custom theme
        fg = self.query_one("#theme-fg", Input).value or "#ffffff"
        bg = self.query_one("#theme-bg", Input).value or "#0a0a0a"
        font_size = int(self.query_one("#font-size", Input).value or "14")
        font_family = self.query_one("#font-family", Input).value or "Menlo, Monaco, Consolas"
        
        from ai_ssh_client.config.settings import TerminalThemeConfig
        custom_theme = TerminalThemeConfig(
            foreground=fg,
            background=bg,
            font_size=font_size,
            font_family=font_family
        )

        conn = ConnectionConfig(
            name=name,
            protocol=protocol,
            host=host,
            port=port,
            username=username,
            auth_type=auth_type,
            key_path=key_path,
            cert_path=cert_path,
            custom_theme=custom_theme
        )
        self.config_manager.add_connection(conn)
        self.config_manager.save()

class QuickConnectScreen(Screen):
    """Quick connect without saving"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Quick Connect", classes="title"),
            Vertical(
                Horizontal(Label("Host:"), Input(placeholder="hostname or IP", id="host")),
                Horizontal(Label("Port:"), Input(value="22", id="port")),
                Horizontal(Label("Username:"), Input(placeholder="username", id="username")),
                classes="form"
            ),
            Horizontal(
                Button("Connect", id="connect"),
                Button("Cancel", id="cancel"),
                classes="buttons"
            )
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "connect":
            host = self.query_one("#host", Input).value
            port = int(self.query_one("#port", Input).value or "22")
            username = self.query_one("#username", Input).value
             
            conn_config = ConnectionConfig(
                name="Quick Connect",
                protocol="ssh",
                host=host,
                port=port,
                username=username,
                auth_type="key",
                key_path="~/.ssh/id_rsa"
            )
            app = self.app
            assert isinstance(app, AISSHApp)
            app.connect_to_host(conn_config)
