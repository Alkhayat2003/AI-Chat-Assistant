#!/usr/bin/env python3
"""
Configuration Loader Module
"""

import json
import os
from pathlib import Path


class ConfigLoader:
    """Loads configuration from JSON files."""

    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config = {}
        self.messages = {}
        self.load_configs()

    def load_configs(self):
        """Load all configuration files."""
        config_file = self.config_dir / "config.json"
        messages_file = self.config_dir / "messages.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

        if messages_file.exists():
            with open(messages_file, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)

    def get(self, key, default=None):
        """Get config value with dot notation (e.g., 'server.url')."""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    def get_message(self, key, **kwargs):
        """Get message with formatting."""
        message = self.messages.get('messages', {}).get(key, key)
        return message.format(**kwargs)
