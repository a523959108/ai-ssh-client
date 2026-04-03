from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Static, Input, TextArea, Button, Label, 
    Footer, Header, Horizontal, Vertical, Container, ProgressBar
)
from textual.containers import Horizontal
from ai_ssh_client.config.settings import ConfigManager, ConnectionConfig
from ai_ssh_client.protocols.base import BaseProtocol
from ai_ssh_client.protocols.factory import create_protocol
from ai_ssh_client.ai import create_ai_client
from ai_ssh_client.ai.base import BaseAIClient
from ai_ssh_client.ai.planner import (
    generate_plan, ExecutionPlan, PlanStep, get_next_step, 
    get_plan_status, is_plan_complete, mark_current_step_done,
    mark_current_step_failed
)
from typing import Optional

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
        height: 85%;
        border: solid blue;
    }

    #terminal-input {
        height: 10%;
    }

    #ai-output {
        height: 50%;
        border: solid yellow;
    }

    #ai-goal-input {
        height: 8%;
    }

    #ai-command-input {
        height: 8%;
    }

    #ai-buttons {
        height: 8%;
    }

    #ai-buttons-single {
        height: 8%;
    }

    #ai-buttons-fav {
        height: 8%;
    }

    #status-text {
        width: 100%;
        height: 100%;
        content-align: left middle;
    }

    Button {
        width: 1fr;
    }

    Static#status-text {
        width: 100%;
        height: 100%;
        content-align: left middle;
    }
    """

    def __init__(self, connection_config: ConnectionConfig, config_manager: ConfigManager):
        super().__init__()
        self.connection_config = connection_config
        self.config_manager = config_manager
        self.protocol = create_protocol(connection_config)
        self.protocol.output_callback = self._on_terminal_output
        self.protocol.command_complete_callback = self._check_command_complete
        self.ai_client = None  # type: Optional[BaseAIClient]
        self.ai_client = create_ai_client(config_manager.config)
        self.ai_visible = False
        self.automation_plan = None  # type: Optional[ExecutionPlan]
        self.auto_executing: bool = False
        self._buffer: str = ""
        self._current_step = None  # type: Optional[PlanStep]
        self._pending_command: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                TextArea(id="terminal-output", read_only=True),
                Static("Ready", id="status-text"),
                Input(id="terminal-input", placeholder="Type command here..."),
                id="terminal-container"
            ),
            Container(
                TextArea(id="ai-output", read_only=True, placeholder="AI responses will appear here"),
                Input(id="ai-goal-input", placeholder="Describe what you want to do (Automated Planning)..."),
                Horizontal(
                    Button("Generate Plan", id="generate-plan"),
                    Button("Start Auto", id="start-auto"),
                    Button("Step by Step", id="step-mode"),
                    id="ai-buttons"
                ),
                Horizontal(
                    Button("Generate", id="generate-command"),
                    Button("Explain", id="explain-command"),
                    Button("Troubleshoot", id="troubleshoot"),
                    id="ai-buttons-single"
                ),
                Horizontal(
                    Button("Saved Commands", id="favorites"),
                    Button("History", id="command-history"),
                    Button("Add Current", id="add-current-fav"),
                    id="ai-buttons-fav"
                ),
                id="ai-panel"
            ),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Mount the screen"""
        success, message = self.protocol.connect()
        if not success:
            self.notify(message, severity="error")
            self.app.pop_screen()
            return

        width = self.query_one("#terminal-output").size.width
        height = self.query_one("#terminal-output").size.height
        if not self.protocol.start(width=width, height=height):
            self.notify("Failed to start session", severity="error")
            self.app.pop_screen()

        if self.ai_client:
            if self.ai_client.is_available():
                self.notify(f"AI client ready ({self.config_manager.config.ai.provider})")
            else:
                self.notify("AI client not configured", severity="warning")

        # Apply custom theme if any
        if self.connection_config.custom_theme:
            theme = self.connection_config.custom_theme
            terminal_output = self.query_one("#terminal-output", TextArea)
            terminal_output.styles.background = theme.background
            terminal_output.styles.color = theme.foreground

    def _on_terminal_output(self, text: str) -> None:
        """Callback for SSH output"""
        widget = self.query_one("#terminal-output", TextArea)
        current = widget.text
        widget.text = current + text
        widget.scroll_end()

        if self.auto_executing and self.automation_plan and self._current_step:
            self._buffer += text

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        if event.input.id == "terminal-input":
            if self.protocol:
                self.protocol.send_input(event.value + "\n")
                # Add command to history
                if event.value.strip():
                    self.config_manager.config.command_history.append(event.value.strip())
                    self.config_manager.save()
            event.input.value = ""
        elif event.input.id == "ai-command-input":
            self._generate_ai_command(event.value)
            event.value = ""
        elif event.input.id == "ai-goal-input":
            self._generate_execution_plan(event.value)
            event.value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "generate-command":
            input_widget = self.query_one("#ai-command-input", Input)
            if input_widget.value:
                self._generate_ai_command(input_widget.value)
                input_widget.value = ""
        elif event.button.id == "explain-command":
            self._explain_current_command()
        elif event.button.id == "troubleshoot":
            self._troubleshoot_current_error()
        elif event.button.id == "generate-plan":
            input_widget = self.query_one("#ai-goal-input", Input)
            if input_widget.value:
                self._generate_execution_plan(input_widget.value)
                input_widget.value = ""
        elif event.button.id == "start-auto":
            self._start_auto_execution()
        elif event.button.id == "step-mode":
            self._execute_next_step()
        elif event.button.id == "favorites":
            from ai_ssh_client.ui.screens.favorites import FavoritesScreen
            def on_select(cmd):
                self._execute_favorite(cmd)
            self.app.push_screen(FavoritesScreen(self.config_manager, on_select))
        elif event.button.id == "command-history":
            self._show_command_history()
        elif event.button.id == "add-current-fav":
            self._add_current_to_favorites()

    def _update_status(self, text: str) -> None:
        """Update status bar text"""
        status_widget = self.query_one("#status-text", Static)
        status_widget.update(text)

    def _generate_execution_plan(self, user_goal: str) -> None:
        """Generate execution plan from user goal"""
        if not self.ai_client:
            self._set_ai_output("AI client not configured. Please check your settings.")
            return

        self._set_ai_output("Generating execution plan...")
        terminal_output = self.query_one("#terminal-output", TextArea).text
        system_info = terminal_output[-1000:] if terminal_output else ""

        plan = generate_plan(self.ai_client, user_goal, system_info)
        if not plan:
            self._set_ai_output("Failed to generate plan. Please try again.")
            return

        self.automation_plan = plan
        self._display_plan(plan)
        self._update_status(f"Plan ready: {plan.goal} - {len(plan.steps)} steps")
        self._toggle_ai_panel(True)

    def _display_plan(self, plan: ExecutionPlan) -> None:
        """Display the generated plan"""
        output = f"Goal: {plan.goal}\n\nGenerated Plan:\n"
        for i, step in enumerate(plan.steps, 1):
            output += f"{i}. [{step.status}] {step.description}\n   Command: `{step.command}`\n\n"
        output += "Click 'Start Auto' for automatic execution, or 'Step by Step' to execute one step at a time."
        self._set_ai_output(output)

    def _start_auto_execution(self) -> None:
        """Start automatic execution of the plan"""
        if not self.automation_plan:
            self._set_ai_output("No plan generated yet. Please generate a plan first.")
            return
        
        self.auto_executing = True
        self._execute_next_step()

    def _execute_next_step(self) -> None:
        """Execute the next step in the plan"""
        if not self.automation_plan:
            return

        if is_plan_complete(self.automation_plan):
            self._finish_plan()
            return

        step = get_next_step(self.automation_plan)
        if not step:
            self._finish_plan()
            return

        self._current_step = step
        step.status = "running"
        self._update_status(get_plan_status(self.automation_plan))
        self._display_plan(self.automation_plan)

        if self.protocol:
            self._buffer = ""
            self.protocol.send_input(step.command + "\n")

    def _check_command_complete(self) -> None:
        """Called after command finishes to mark step complete"""
        if self.automation_plan and self._current_step:
            mark_current_step_done(self.automation_plan, self._buffer)
            self._display_plan(self.automation_plan)
            self._update_status(get_plan_status(self.automation_plan))
            
            if self.auto_executing and not is_plan_complete(self.automation_plan):
                self.app.call_later(1.5, self._execute_next_step)
            elif is_plan_complete(self.automation_plan):
                self._finish_plan()

    def _finish_plan(self) -> None:
        """Plan execution finished"""
        self.auto_executing = False
        if self.automation_plan:
            done = sum(1 for step in self.automation_plan.steps if step.status == "done")
            failed = sum(1 for step in self.automation_plan.steps if step.status == "failed")
            total = len(self.automation_plan.steps)
            self._update_status(f"✓ Completed: {done}/{total} steps, {failed} failed - {self.automation_plan.goal}")
            self._set_ai_output(f"Plan completed!\n\nStatistics:\n- Total steps: {total}\n- Completed: {done}\n- Failed: {failed}\n\nAll tasks done!")

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

    def _toggle_ai_panel(self, visible: 'bool | None' = None) -> None:
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
        if self.protocol:
            container = self.query_one("#terminal-container")
            self.protocol.resize(container.size.width, container.size.height)
