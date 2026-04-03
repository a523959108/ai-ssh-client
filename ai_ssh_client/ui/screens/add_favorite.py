from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Button, Input, Label, Footer, Header
)
from textual.containers import Container, Vertical, Horizontal
from ai_ssh_client.config.settings import ConfigManager, FavoriteCommand

class AddFavoriteScreen(Screen):
    """Add new favorite command"""

    def __init__(self, config_manager: ConfigManager, on_done):
        super().__init__()
        self.config_manager = config_manager
        self.on_done = on_done

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Add Saved Command", classes="title"),
            Vertical(
                Horizontal(Label("Name:"), Input(placeholder="Display name", id="name")),
                Horizontal(Label("Command:"), Input(placeholder="The command to save", id="command")),
                Horizontal(Label("Description:"), Input(placeholder="Optional description", id="description")),
                classes="form"
            ),
            Horizontal(
                Button("Save", id="save"),
                Button("Cancel", id="cancel"),
                classes="buttons"
            ),
            id="add-favorite-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save":
            self._save()
            self.app.pop_screen()
            if self.on_done:
                self.on_done()

    def _save(self) -> None:
        name = self.query_one("#name", Input).value
        command = self.query_one("#command", Input).value
        description = self.query_one("#description", Input).value

        fav = FavoriteCommand(
            name=name,
            command=command,
            description=description
        )
        self.config_manager.config.favorite_commands.append(fav)
        self.config_manager.save()
