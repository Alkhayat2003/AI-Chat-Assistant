#!/usr/bin/env python3
"""
UI Module — Handles terminal interface and user interactions.
"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
import time
from config import ConfigLoader


class ChatUI:
    """Handles the chat user interface."""

    def __init__(self, config_loader=None):
        self.config = config_loader or ConfigLoader()
        self.console = Console()

    def show_welcome(self):
        """Display welcome message."""
        welcome_msg = self.config.get_message('welcome')
        self.console.print(Panel.fit(
            f"[bold blue]{welcome_msg}[/bold blue]",
            border_style="blue"
        ))

    def get_user_input(self):
        """Get input from user."""
        return Prompt.ask("[bold green]You[/bold green]").strip()

    def display_response_gradually(self, response):
        """Display AI response gradually in a panel."""
        response_text = Text("", style="cyan")
        panel = Panel(response_text, title="[bold red]AI[/bold red]", border_style="red", expand=False)
        refresh_rate = self.config.get('ui.refresh_rate', 20)
        typing_speed = self.config.get('ui.typing_speed', 0.02)
        with Live(panel, console=self.console, refresh_per_second=refresh_rate) as live:
            for char in response:
                response_text.append(char)
                panel = Panel(response_text, title="[bold red]AI[/bold red]", border_style="red", expand=False)
                live.update(panel)
                time.sleep(typing_speed)  # Adjust typing speed here

        self.console.print()  # Add empty line after response

    def show_goodbye(self):
        """Display goodbye message."""
        goodbye_msg = self.config.get_message('goodbye')
        self.console.print(f"[yellow]{goodbye_msg}[/yellow]")

    def show_interrupted(self):
        """Display interrupted message."""
        interrupted_msg = self.config.get_message('interrupted')
        self.console.print(f"\n[yellow]{interrupted_msg}[/yellow]")

    def show_error(self, message):
        """Display error message."""
        self.console.print(f"[red]❌ {message}[/red]")

    def show_saving(self):
        """Show saving message."""
        saving_msg = self.config.get_message('saving_conversation')
        self.console.print(f"[blue]{saving_msg}[/blue]")

    def show_saved(self, filename):
        """Show saved message."""
        saved_msg = self.config.get_message('conversation_saved', filename=filename)
        self.console.print(f"[green]{saved_msg}[/green]")