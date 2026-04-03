from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Input, TextArea, Button, Label, 
    Footer, Header, Horizontal, Vertical, Container
)
from textual.containers import Horizontal
from ai_ssh_client.config.settings import ConfigManager, ConnectionConfig
from ai_ssh_client.ssh.connection import SSHConnection
from ai_ssh_client.ssh.session import SSHSession
from ai_ssh_client.ai import create_ai_client
from ai_ssh_client.ai.base import BaseAIClient

class TerminalScreen(Screen):
    """Main SSH terminal screen with AI panel"""

    CSS = """
    #main-container {
        height: 100%;
    }

    #terminal-container {
        width: 70%;
        height: 100%;
    }

    #ai-panel {
        width: 30%;
        height: 100%;
        background: #1a1a1a;
        border-left: solid green;
        display: none;
    }

    #ai-panel.visible {
        display: block;
    }

    #terminal-output {
        height: 90%;
        border: solid blue;
    }

    #terminal-input {
        height: 10%;
    }

    #ai-output {
        height: 80%;
        border: solid yellow;
    }

    #ai-command-input {
        height: 10%;
    }

    #ai-buttons {
        height: 10%;
    }

    Button {
        width: 1fr;
    }
    """

    def __init__(self, connection_config: ConnectionConfig, config_manager: ConfigManager):
        super().__init__()
        self.connection_config = connection_config
        self.config_manager = config_manager
        self.connection = SSHConnection(connection_config)
        self.session: SSHSession | None = None
        self.ai_client: BaseAIClient | None = create_ai_client(config_manager.config)
        self.ai_visible = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                TextArea(id="terminal-output", read_only=True),
                Input(id="terminal-input", placeholder="Type command here..."),
                id="terminal-container"
            ),
            Container(
                TextArea(id="ai-output", read_only=True, placeholder="AI responses will appear here"),
                Input(id="ai-command-input", placeholder="Describe what you want in natural language..."),
                Horizontal(
                    Button("Generate", id="generate-command"),
                    Button("Explain", id="explain-command"),
                    Button("Troubleshoot", id="troubleshoot"),
                    id="ai-buttons"
                ),
                id="ai-panel"
            ),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Mount the screen"""
        success, message = self.connection.connect()
        if not success:
            self.notify(message, severity="error")
            self.app.pop_screen()
            return

        self.session = SSHSession(self.connection)
        self.session.output_callback = self._on_terminal_output
        width = self.query_one("#terminal-output").size.width
        height = self.query_one("#terminal-output").size.height
        if not self.session.start(width=width, height=height):
            self.notify("Failed to start session", severity="error")
            self.app.pop_screen()

        if self.ai_client:
            if self.ai_client.is_available():
                self.notify(f"AI client ready ({self.config_manager.config.ai.provider})")
            else:
                self.notify("AI client not configured", severity="warning")

    def _on_terminal_output(self, text: str) -> None:
        """Callback for SSH output"""
        widget = self.query_one("#terminal-output", TextArea)
        current = widget.text
        widget.text = current + text
        widget.scroll_end()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        if event.input.id == "terminal-input":
            if self.session:
                self.session.send_input(event.value + "\n")
            event.input.value = ""
        elif event.input.id == "ai-command-input":
            self._generate_ai_command(event.value)
            event.value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle AI button presses"""
        if event.button.id == "generate-command":
            input_widget = self.query_one("#ai-command-input", Input)
            if input_widget.value:
                self._generate_ai_command(input_widget.value)
                input_widget.value = ""
        elif event.button.id == "explain-command":
            self._explain_current_command()
        elif event.button.id == "troubleshoot":
            self._troubleshoot_current_error()

    def _generate_ai_command(self, user_request: str) -> None:
        """Generate command from natural language"""
        if not self.ai_client:
            self._set_ai_output("AI client not configured. Please check your settings.")
            return

        terminal_output = self.query_one("#terminal-output", TextArea).text
        context = terminal_output[-500:] if terminal_output else ""

        self._set_ai_output("Generating...")

        command = self.ai_client.generate_command(user_request, context)
        if command:
            self._set_ai_output(f"Generated command:\n\n{command}\n\nPress [Enter] to execute.")
            self._pending_command = command
        else:
            self._set_ai_output("Failed to generate command. Please try again.")

        self._toggle_ai_panel(True)

    def _explain_current_command(self) -> None:
        """Explain the current command"""
        if not self.ai_client:
            self._set_ai_output("AI client not configured.")
            return

        input_val = self.query_one("#terminal-input", Input).value
        if not input_val:
            self._set_ai_output("No command to explain. Enter a command first.")
            return

        explanation = self.ai_client.explain_command(input_val)
        if explanation:
            self._set_ai_output(f"Explanation:\n\n{explanation}")
        else:
            self._set_ai_output("Failed to get explanation.")

        self._toggle_ai_panel(True)

    def _troubleshoot_current_error(self) -> None:
        """Troubleshoot the last error"""
        if not self.ai_client:
            self._set_ai_output("AI client not configured.")
            return

        terminal_output = self.query_one("#terminal-output", TextArea).text
        last_lines = terminal_output.splitlines()[-20:]
        error_text = "\n".join(last_lines)
        last_command = self.query_one("#terminal-input", Input).value or "last command"

        result = self.ai_client.troubleshoot_error(last_command, error_text)
        if result:
            self._set_ai_output(f"Troubleshooting result:\n\n{result}")
        else:
            self._set_ai_output("Failed to troubleshoot.")

        self._toggle_ai_panel(True)

    def _set_ai_output(self, text: str) -> None:
        """Set AI output text"""
        output_widget = self.query_one("#ai-output", TextArea)
        output_widget.text = text

    def _toggle_ai_panel(self, visible: bool = None) -> None:
        """Toggle AI panel visibility"""
        panel = self.query_one("#ai-panel", Container)
        if visible is None:
            self.ai_visible = not self.ai_visible
        else:
            self.ai_visible = visible

        if self.ai_visible:
            panel.add_class("visible")
        else:
            panel.remove_class("visible")

    def on_resize(self, event):
        """Handle terminal resize"""
        if self.session:
            container = self.query_one("#terminal-container")
            self.session.resize(container.size.width, container.size.height)
