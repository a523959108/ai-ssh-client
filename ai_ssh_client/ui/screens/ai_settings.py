from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Button, Input, Select, Label, 
    Footer, Header, TextArea
)
from textual.containers import Container, Vertical, Horizontal
from ai_ssh_client.ai.presets import PRESETS, get_preset_by_name, get_preset_options
from ai_ssh_client.config.settings import ConfigManager, AppConfig

class AISettingsScreen(Screen):
    """AI Provider settings screen"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.current_preset = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("AI Provider Settings", classes="title"),
            Vertical(
                Horizontal(
                    Label("Provider:"),
                    Select(
                        get_preset_options(),
                        id="provider-preset",
                        value=self._get_current_preset_name()
                    ),
                ),
                Horizontal(
                    Label("API Key:"),
                    Input(placeholder="Enter your API key here", id="api-key"),
                ),
                Horizontal(
                    Label("Model:"),
                    Input(placeholder="Model name", id="model-name"),
                ),
                Horizontal(
                    Label("Base URL:"),
                    Input(placeholder="API base URL", id="base-url"),
                ),
                Static("Extra Headers (JSON format, optional):", classes="label"),
                TextArea(placeholder="{}", id="extra-headers", classes="json-editor"),
                classes="form"
            ),
            Horizontal(
                Button("Save", id="save"),
                Button("Cancel", id="cancel"),
                classes="buttons"
            ),
            id="settings-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Fill current values"""
        config = self.config_manager.config.ai
        if config.provider == "openai":
            self._fill_values(
                "openai",
                config.openai.api_key,
                config.openai.model,
                config.openai.base_url,
                {}
            )
        elif config.provider == "openai_compatible":
            oc = config.openai_compatible
            self._fill_values(
                self._detect_preset(oc.base_url),
                oc.api_key,
                oc.model,
                oc.base_url,
                oc.extra_headers
            )

    def _detect_preset(self, base_url: str) -> str:
        """Try to detect which preset this URL belongs to"""
        for preset in PRESETS:
            if preset.base_url in base_url:
                return preset.name
        return "custom"

    def _get_current_preset_name(self) -> str:
        config = self.config_manager.config.ai
        if config.provider == "openai":
            return "openai"
        elif config.provider == "ollama":
            return "ollama"
        else:
            base_url = config.openai_compatible.base_url
            return self._detect_preset(base_url)

    def _fill_values(self, preset_name: str, api_key: str, model: str, base_url: str, extra_headers: dict):
        """Fill form values"""
        preset = get_preset_by_name(preset_name)
        if preset:
            self.current_preset = preset
            if not model:
                model = preset.default_model
            if not base_url:
                base_url = preset.base_url
        
        self.query_one("#api-key", Input).value = api_key
        self.query_one("#model-name", Input).value = model
        self.query_one("#base-url", Input).value = base_url
        
        import json
        self.query_one("#extra-headers", TextArea).text = json.dumps(extra_headers or {}, indent=2)

    def on_select_changed(self, event: Select.Changed) -> None:
        """When preset is selected, auto fill other fields"""
        preset_name = event.value
        preset = get_preset_by_name(preset_name)
        if preset:
            self.current_preset = preset
            model_input = self.query_one("#model-name", Input)
            base_url_input = self.query_one("#base-url", Input)
            if not model_input.value:
                model_input.value = preset.default_model
            if not base_url_input.value:
                base_url_input.value = preset.base_url
            
            extra_headers = self.query_one("#extra-headers", TextArea)
            if preset.extra_headers and not extra_headers.text.strip():
                import json
                extra_headers.text = json.dumps(preset.extra_headers, indent=2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        elif event.button.id == "save":
            self._save_settings()
            self.app.pop_screen()

    def _save_settings(self) -> None:
        """Save the AI configuration"""
        preset_name = self.query_one("#provider-preset", Select).value
        api_key = self.query_one("#api-key", Input).value
        model = self.query_one("#model-name", Input).value
        base_url = self.query_one("#base-url", Input).value
        extra_headers_text = self.query_one("#extra-headers", TextArea).text

        import json
        try:
            extra_headers = json.loads(extra_headers_text) if extra_headers_text else {}
        except:
            extra_headers = {}

        config = self.config_manager.config
        if preset_name == "openai":
            config.ai.provider = "openai"
            config.ai.openai.api_key = api_key
            config.ai.openai.model = model
            config.ai.openai.base_url = base_url
        elif preset_name == "ollama":
            config.ai.provider = "ollama"
            config.ai.ollama.model = model
            config.ai.ollama.base_url = base_url
        else:
            config.ai.provider = "openai_compatible"
            config.ai.openai_compatible.api_key = api_key
            config.ai.openai_compatible.model = model
            config.ai.openai_compatible.base_url = base_url
            config.ai.openai_compatible.extra_headers = extra_headers

        self.config_manager.save()
        self.notify("AI settings saved successfully", severity="information")
