#!/usr/bin/env python3
"""
ChatWith - A terminal-based chat interface for multiple LLM providers.
"""

import sys
import os
import argparse
import threading
import time
import json
import subprocess
import tempfile
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LoadingAnimation:
    """Displays an animated loading indicator while waiting for responses."""

    def __init__(self):
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start the loading animation."""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the loading animation and clear the line."""
        self.is_running = False
        if self.thread:
            self.thread.join()
        # Clear the loading line
        sys.stdout.write('\r' + ' ' * 10 + '\r')
        sys.stdout.flush()

    def _animate(self):
        """Animation loop that displays dots."""
        dots = ['', '.', '..', '...']
        idx = 0
        while self.is_running:
            sys.stdout.write('\r' + dots[idx % len(dots)])
            sys.stdout.flush()
            idx += 1
            time.sleep(0.5)


class SystemPromptManager:
    """Manages custom system prompts for different models."""

    def __init__(self):
        self.config_dir = Path.home() / ".chatwith"
        self.config_file = self.config_dir / "system-prompt.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)

    def load_prompts(self) -> Dict[str, str]:
        """Load system prompts from config file."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load system prompts: {e}")
            return {}

    def save_prompts(self, prompts: Dict[str, str]):
        """Save system prompts to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(prompts, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save system prompts: {e}")

    def get_prompt(self, model: str) -> Optional[str]:
        """Get system prompt for a specific model."""
        prompts = self.load_prompts()
        return prompts.get(model)

    def edit_prompt(self, model: str) -> bool:
        """Open editor to edit system prompt for a model."""
        prompts = self.load_prompts()
        current_prompt = prompts.get(model, "")

        # Create temporary file with current prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
            tf.write(current_prompt)
            temp_path = tf.name

        try:
            # Get editor from environment, with fallbacks
            editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
            if not editor:
                # Try common editors
                for candidate in ['vim', 'nano', 'vi']:
                    if subprocess.run(['which', candidate], capture_output=True).returncode == 0:
                        editor = candidate
                        break

            if not editor:
                print("Error: No text editor found. Set $EDITOR environment variable.")
                return False

            # Open editor
            subprocess.run([editor, temp_path])

            # Read edited content
            with open(temp_path, 'r') as f:
                new_prompt = f.read().strip()

            # Save if changed
            if new_prompt != current_prompt:
                if new_prompt:
                    prompts[model] = new_prompt
                elif model in prompts:
                    del prompts[model]  # Remove if empty

                self.save_prompts(prompts)
                print(f"System prompt updated for {model}")
            else:
                print("No changes made.")

            return True

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt_manager = SystemPromptManager()

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is present and properly formatted."""
        pass

    @abstractmethod
    def send_message(self, message: str) -> None:
        """Send a message and stream the response."""
        pass

    def add_to_history(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})


class ClaudeProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "claude-sonnet-4-5-20250929")
        self.client = None

    def validate_api_key(self) -> bool:
        """Validate the API key is present."""
        if not self.api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set.")
            print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
            return False

        # Initialize the client
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            return True
        except ImportError:
            print("Error: 'anthropic' package not installed.")
            print("Please install it with: pip install anthropic")
            return False
        except Exception as e:
            print(f"Error initializing Anthropic client: {e}")
            return False

    def send_message(self, message: str) -> None:
        """Send a message and stream the response."""
        # Add user message to history
        self.add_to_history("user", message)

        # Show loading animation
        loader = LoadingAnimation()
        loader.start()

        try:
            # Create streaming request
            response_text = ""

            # Get system prompt if configured
            system_prompt = self.system_prompt_manager.get_prompt(self.model)
            request_params = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": self.conversation_history,
            }
            if system_prompt:
                request_params["system"] = system_prompt

            with self.client.messages.stream(**request_params) as stream:
                # Stop loading animation when stream starts
                loader.stop()

                # Print assistant prefix
                sys.stdout.write("Assistant: ")
                sys.stdout.flush()

                # Stream the response
                for text in stream.text_stream:
                    response_text += text
                    sys.stdout.write(text)
                    sys.stdout.flush()

                # Add newline after response
                print()

            # Add assistant response to history
            self.add_to_history("assistant", response_text)

        except Exception as e:
            loader.stop()
            print(f"\nError: {e}")
            # Remove the user message from history since the request failed
            self.conversation_history.pop()


class ChatGPTProvider(LLMProvider):
    """Provider for OpenAI's ChatGPT models."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "gpt-5.2")
        self.client = None

    def validate_api_key(self) -> bool:
        """Validate the API key is present."""
        if not self.api_key:
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set it with: export OPENAI_API_KEY='your-key-here'")
            return False

        # Initialize the client
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            return True
        except ImportError:
            print("Error: 'openai' package not installed.")
            print("Please install it with: pip install openai")
            return False
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            return False

    def send_message(self, message: str) -> None:
        """Send a message and stream the response."""
        # Add user message to history
        self.add_to_history("user", message)

        # Show loading animation
        loader = LoadingAnimation()
        loader.start()

        try:
            # Create streaming request
            response_text = ""

            # Build messages with system prompt if configured
            messages = []
            system_prompt = self.system_prompt_manager.get_prompt(self.model)
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.conversation_history)

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )

            # Stop loading animation when stream starts
            loader.stop()

            # Print assistant prefix
            sys.stdout.write("Assistant: ")
            sys.stdout.flush()

            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    sys.stdout.write(text)
                    sys.stdout.flush()

            # Add newline after response
            print()

            # Add assistant response to history
            self.add_to_history("assistant", response_text)

        except Exception as e:
            loader.stop()
            print(f"\nError: {e}")
            # Remove the user message from history since the request failed
            self.conversation_history.pop()


class GeminiProvider(LLMProvider):
    """Provider for Google's Gemini models."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "gemini-2.5-flash")
        self.client = None
        self.chat = None

    def validate_api_key(self) -> bool:
        """Validate the API key is present."""
        if not self.api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            print("Please set it with: export GOOGLE_API_KEY='your-key-here'")
            return False

        # Initialize the client
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            return True
        except ImportError:
            print("Error: 'google-genai' package not installed.")
            print("Please install it with: pip install google-genai")
            return False
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            return False

    def send_message(self, message: str) -> None:
        """Send a message and stream the response."""
        # Add user message to history
        self.add_to_history("user", message)

        # Show loading animation
        loader = LoadingAnimation()
        loader.start()

        try:
            # Build contents from conversation history
            from google.genai import types
            contents = [
                types.Content(
                    role=msg["role"] if msg["role"] == "user" else "model",
                    parts=[types.Part(text=msg["content"])]
                )
                for msg in self.conversation_history
            ]

            # Get system prompt if configured
            system_prompt = self.system_prompt_manager.get_prompt(self.model)
            config = types.GenerateContentConfig()
            if system_prompt:
                config.system_instruction = system_prompt

            # Send message with streaming
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=config
            )

            # Stop loading animation when stream starts
            loader.stop()

            # Print assistant prefix
            sys.stdout.write("Assistant: ")
            sys.stdout.flush()

            # Stream the response
            response_text = ""
            for chunk in response:
                if chunk.text:
                    response_text += chunk.text
                    sys.stdout.write(chunk.text)
                    sys.stdout.flush()

            # Add newline after response
            print()

            # Add assistant response to history
            self.add_to_history("model", response_text)

        except Exception as e:
            loader.stop()
            print(f"\nError: {e}")
            # Remove the user message from history since the request failed
            self.conversation_history.pop()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ChatWith - Chat with LLMs from your terminal",
        usage="chatwith <provider>"
    )

    parser.add_argument(
        "provider",
        choices=["claude", "chatgpt", "gpt", "gemini", "openrouter"],
        help="LLM provider to use"
    )

    return parser.parse_args()


def create_provider(provider_name: str) -> Optional[LLMProvider]:
    """Create and validate a provider instance."""
    if provider_name == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        provider = ClaudeProvider(api_key)
        if not provider.validate_api_key():
            return None
        return provider
    elif provider_name in ["chatgpt", "gpt"]:
        api_key = os.getenv("OPENAI_API_KEY", "")
        provider = ChatGPTProvider(api_key)
        if not provider.validate_api_key():
            return None
        return provider
    elif provider_name == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY", "")
        provider = GeminiProvider(api_key)
        if not provider.validate_api_key():
            return None
        return provider
    elif provider_name == "openrouter":
        print("Error: OpenRouter support coming soon!")
        return None
    else:
        print(f"Error: Unknown provider '{provider_name}'")
        return None


def show_help():
    """Display help message with available commands."""
    print("\nAvailable commands:")
    print("  /help   - Show this help message")
    print("  /clear  - Clear conversation history")
    print("  /cls    - Clear the terminal screen")
    print("  /system - Edit custom system prompt for current model")
    print("  /exit   - Exit the application")
    print("  /quit   - Exit the application")
    print()


def chat_loop(provider: LLMProvider):
    """Main chat loop."""
    # Print welcome message
    print(f"ChatWith [{provider.model}]")
    print("─" * (len(provider.model) + 11))
    print("Type /help for available commands")
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle special commands
            if user_input in ["/exit", "/quit"]:
                print("Goodbye!")
                break
            elif user_input == "/help":
                show_help()
                continue
            elif user_input == "/clear":
                provider.conversation_history.clear()
                print("Conversation history cleared.")
                print()
                continue
            elif user_input == "/cls":
                # Clear the terminal screen using ANSI escape codes
                print("\033[2J\033[H", end="")
                sys.stdout.flush()
                continue
            elif user_input == "/system":
                provider.system_prompt_manager.edit_prompt(provider.model)
                print()
                continue

            # Send message and get response
            provider.send_message(user_input)
            print()  # Extra newline for readability

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    # Create provider
    provider = create_provider(args.provider)
    if not provider:
        sys.exit(1)

    # Start chat loop
    chat_loop(provider)


if __name__ == "__main__":
    main()
