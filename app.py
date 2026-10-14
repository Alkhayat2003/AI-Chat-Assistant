#!/usr/bin/env python3
"""
Main Chat Application
"""

from ai_model.model import LLMModel
from ui.terminal import ChatUI
from ui.gui import ChatGUI
from config import ConfigLoader
import argparse
import os


def chat_terminal():
    """Start interactive chat session in terminal."""
    config = ConfigLoader()
    model = LLMModel(config)
    ui = ChatUI(config)

    ui.show_welcome()

    # Show available models
    available_models = model.get_available_models()
    if len(available_models) > 1:
        ui.console.print(f"[dim]Available models: {', '.join(available_models)}[/dim]")
        ui.console.print(f"[dim]Current model: {model.model}[/dim]")
        ui.console.print("[dim]Type 'model <name>' to switch models[/dim]")
        ui.console.print()

    while True:
        try:
            user_input = ui.get_user_input()

            # Handle special commands
            if user_input.lower() in config.messages.get('exit_commands', ['exit', 'quit', 'q']):
                ui.show_saving()
                filename = model.save_conversation()
                ui.show_saved(filename)
                ui.show_goodbye()
                break

            elif user_input.startswith('model '):
                new_model = user_input.split(' ', 1)[1]
                if model.set_model(new_model):
                    ui.console.print(f"[green]✅ Switched to model: {new_model}[/green]")
                else:
                    ui.console.print(f"[red]❌ Model '{new_model}' not available. Available: {', '.join(available_models)}[/red]")
                continue

            elif user_input.lower() == 'save':
                ui.show_saving()
                filename = model.save_conversation()
                ui.show_saved(filename)
                continue

            if not user_input:
                continue

            # Get response from model
            try:
                response = model.send_message(user_input)
                ui.display_response_gradually(response)
            except (ConnectionError, TimeoutError, RuntimeError, ValueError) as e:
                ui.show_error(str(e))
                continue

        except KeyboardInterrupt:
            ui.show_saving()
            filename = model.save_conversation()
            ui.show_saved(filename)
            ui.show_interrupted()
            break


def chat_gui():
    """Start GUI chat session."""
    gui = ChatGUI()
    gui.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Chat Assistant")
    parser.add_argument("--gui", action="store_true", help="Run with graphical interface")
    args = parser.parse_args()

    if args.gui:
        chat_gui()
    else:
        chat_terminal()