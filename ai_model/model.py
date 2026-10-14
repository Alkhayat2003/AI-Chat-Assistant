#!/usr/bin/env python3
"""
Model Module — Handles LLM interactions.
"""

import requests
import time
import logging
import re
import threading
from collections import deque
from config import ConfigLoader


class RateLimiter:
    """Simple rate limiter using sliding window."""

    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()

    def allow(self):
        """Check if request is allowed under rate limit."""
        with self.lock:
            now = time.time()
            # Remove old requests outside the window
            while self.requests and now - self.requests[0] > self.window_seconds:
                self.requests.popleft()

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False


class LLMModel:
    """Handles communication with the LLM server."""

    def __init__(self, config_loader=None):
        self.config = config_loader or ConfigLoader()
        self.server_url = self.config.get('server.url')
        self.timeout = self.config.get('server.timeout')
        self.available_models = self.config.get('models.available', [])
        self.model = self.config.get('models.default')
        self.max_retries = self.config.get('security.max_retries', 3)
        self.retry_delay = self.config.get('security.retry_delay', 1)
        self.max_message_length = self.config.get('security.max_message_length', 1000)
        self.conversation = []

        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        rate_limit_requests = self.config.get('security.rate_limit_requests', 10)
        rate_limit_window = self.config.get('security.rate_limit_window', 60)
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)

    def sanitize_input(self, user_message):
        """Sanitize user input to prevent injection attacks."""
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>]', '', user_message)
        # Trim whitespace
        sanitized = sanitized.strip()
        return sanitized

    def set_model(self, model_name):
        """Set the active model if it's available."""
        if model_name in self.available_models:
            self.model = model_name
            self.logger.info(f"Model switched to: {model_name}")
            return True
        self.logger.warning(f"Attempted to switch to unavailable model: {model_name}")
        return False

    def get_available_models(self):
        """Get list of available models."""
        return self.available_models

    def send_message(self, user_message):
        """Send a message to the LLM and get response with retry logic."""
        # Check rate limit
        if not self.rate_limiter.allow():
            raise RuntimeError("Rate limit exceeded. Please wait before sending more messages.")

        # Sanitize input
        user_message = self.sanitize_input(user_message)

        if len(user_message) > self.max_message_length:
            raise ValueError(f"Message too long. Maximum length: {self.max_message_length}")

        self.conversation.append({"role": "user", "content": user_message})
        self.logger.info(f"User message added to conversation. Length: {len(user_message)}")

        # Keep last messages for context
        max_history = self.config.get('chat.max_history', 10)
        messages = self.conversation[-max_history:]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.config.get('chat.temperature', 0.7),
            "max_tokens": self.config.get('chat.max_tokens', 1024),
            "stream": False,
        }

        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Sending request to LLM (attempt {attempt + 1}/{self.max_retries})")
                response = requests.post(
                    self.server_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"].strip()

                self.conversation.append({"role": "assistant", "content": ai_response})
                self.logger.info(f"AI response received. Length: {len(ai_response)}")
                return ai_response

            except requests.exceptions.ConnectionError:
                error_msg = self.config.get_message('connection_error')
                self.logger.error(f"Connection error on attempt {attempt + 1}: {error_msg}")
                if attempt == self.max_retries - 1:
                    raise ConnectionError(error_msg)
            except requests.exceptions.Timeout:
                error_msg = self.config.get_message('timeout_error')
                self.logger.error(f"Timeout error on attempt {attempt + 1}: {error_msg}")
                if attempt == self.max_retries - 1:
                    raise TimeoutError(error_msg)
            except Exception as e:
                error_msg = self.config.get_message('generic_error', error=str(e))
                self.logger.error(f"Generic error on attempt {attempt + 1}: {error_msg}")
                if attempt == self.max_retries - 1:
                    raise RuntimeError(error_msg)

            # Wait before retry
            time.sleep(self.retry_delay * (attempt + 1))

    def save_conversation(self, filename="conversation.json"):
        """Save the conversation to a JSON file."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "model": self.model,
                "timestamp": time.time(),
                "conversation": self.conversation
            }, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Conversation saved to {filename}")
        return filename

    def load_conversation(self, filename):
        """Load a conversation from a JSON file."""
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.model = data.get('model', self.model)
        self.conversation = data.get('conversation', [])
        self.logger.info(f"Conversation loaded from {filename}. Messages: {len(self.conversation)}")
        return len(self.conversation)

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation = []
        self.logger.info("Conversation history cleared")