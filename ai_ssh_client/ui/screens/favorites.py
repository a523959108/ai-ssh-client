from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Button, Input, ListView, ListItem, Label, 
    Footer, Header
)
from textual.containers import Container, Vertical, Horizontal
from ai_ssh_client.config.settings import ConfigManager, FavoriteCommand

class FavoritesScreen(Screen):
    """Saved favorite commands screen"""

    def __init__(self, config_manager: ConfigManager, on_select):
        super().__init__()
        self.config_manager = config_manager
        self.on_select = on_select

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Saved Commands", classes="title"),
            ListView(
                *[ListItem(Static(f"{cmd.name}: {cmd.command[:50]}")) 
                  for cmd in self.config_manager.config.favorite_commands],
                id="favorites-list"
            ) if self.config_manager.config.favorite_commands else 
            Static("No saved commands", classes="empty"),
            Horizontal(
                Button("Add New", id="add-favorite"),
                Button("Close", id="close"),
                classes="buttons"
            ),
            id="favorites-container"
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """User selected a favorite command"""
        index = event.list_view.index
        if index is not None:
            cmd = self.config_manager.config.favorite_commands[index]
            self.on_select(cmd.command)
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()
        elif event.button.id == "add-favorite":
            self.app.push_screen(AddFavoriteScreen(self.config_manager, self._on_added))

    def _on_added(self):
        """Refresh after adding"""
        self.app.pop_screen()
        self.app.refresh()
