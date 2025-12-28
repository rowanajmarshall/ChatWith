#!/usr/bin/env python3
"""
Comprehensive test suite for ChatWith application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os
from io import StringIO

# Import the application modules
import chatwith
from chatwith import (
    LoadingAnimation,
    LLMProvider,
    ClaudeProvider,
    ChatGPTProvider,
    GeminiProvider,
    parse_arguments,
    create_provider,
    show_help,
)


class TestLoadingAnimation(unittest.TestCase):
    """Tests for the LoadingAnimation class."""

    def test_initialization(self):
        """Test that LoadingAnimation initializes correctly."""
        loader = LoadingAnimation()
        self.assertFalse(loader.is_running)
        self.assertIsNone(loader.thread)

    def test_start_stop(self):
        """Test starting and stopping the animation."""
        loader = LoadingAnimation()
        loader.start()
        self.assertTrue(loader.is_running)
        self.assertIsNotNone(loader.thread)

        # Stop the animation
        loader.stop()
        self.assertFalse(loader.is_running)


class TestArgumentParsing(unittest.TestCase):
    """Tests for command-line argument parsing."""

    def test_parse_claude(self):
        """Test parsing 'claude' provider."""
        with patch('sys.argv', ['chatwith', 'claude']):
            args = parse_arguments()
            self.assertEqual(args.provider, 'claude')

    def test_parse_chatgpt(self):
        """Test parsing 'chatgpt' provider."""
        with patch('sys.argv', ['chatwith', 'chatgpt']):
            args = parse_arguments()
            self.assertEqual(args.provider, 'chatgpt')

    def test_parse_gpt_alias(self):
        """Test parsing 'gpt' alias."""
        with patch('sys.argv', ['chatwith', 'gpt']):
            args = parse_arguments()
            self.assertEqual(args.provider, 'gpt')

    def test_parse_gemini(self):
        """Test parsing 'gemini' provider."""
        with patch('sys.argv', ['chatwith', 'gemini']):
            args = parse_arguments()
            self.assertEqual(args.provider, 'gemini')

    def test_invalid_provider(self):
        """Test that invalid provider raises SystemExit."""
        with patch('sys.argv', ['chatwith', 'invalid']):
            with self.assertRaises(SystemExit):
                parse_arguments()


class TestProviderInitialization(unittest.TestCase):
    """Tests for provider initialization and validation."""

    def test_claude_provider_no_api_key(self):
        """Test Claude provider with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('claude')
            self.assertIsNone(provider)

    def test_chatgpt_provider_no_api_key(self):
        """Test ChatGPT provider with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('chatgpt')
            self.assertIsNone(provider)

    def test_gemini_provider_no_api_key(self):
        """Test Gemini provider with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('gemini')
            self.assertIsNone(provider)

    def test_claude_provider_initialization(self):
        """Test Claude provider initialization with API key."""
        provider = ClaudeProvider("test-key")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "claude-sonnet-4-5-20250929")
        self.assertEqual(provider.conversation_history, [])

    def test_chatgpt_provider_initialization(self):
        """Test ChatGPT provider initialization with API key."""
        provider = ChatGPTProvider("test-key")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "gpt-5.2")
        self.assertEqual(provider.conversation_history, [])

    def test_gemini_provider_initialization(self):
        """Test Gemini provider initialization with API key."""
        provider = GeminiProvider("test-key")
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "gemini-2.5-flash")
        self.assertEqual(provider.conversation_history, [])


class TestConversationHistory(unittest.TestCase):
    """Tests for conversation history management."""

    def test_add_to_history(self):
        """Test adding messages to conversation history."""
        provider = ClaudeProvider("test-key")
        provider.add_to_history("user", "Hello")
        provider.add_to_history("assistant", "Hi there!")

        self.assertEqual(len(provider.conversation_history), 2)
        self.assertEqual(provider.conversation_history[0]["role"], "user")
        self.assertEqual(provider.conversation_history[0]["content"], "Hello")
        self.assertEqual(provider.conversation_history[1]["role"], "assistant")
        self.assertEqual(provider.conversation_history[1]["content"], "Hi there!")

    def test_clear_history(self):
        """Test clearing conversation history."""
        provider = ClaudeProvider("test-key")
        provider.add_to_history("user", "Hello")
        provider.add_to_history("assistant", "Hi there!")

        provider.conversation_history.clear()
        self.assertEqual(len(provider.conversation_history), 0)


class TestClaudeProvider(unittest.TestCase):
    """Tests for Claude provider specific functionality."""

    @patch('builtins.__import__')
    def test_validate_api_key_success(self, mock_import):
        """Test successful API key validation for Claude."""
        mock_anthropic = Mock()
        mock_client = Mock()
        mock_anthropic.Anthropic.return_value = mock_client

        def import_mock(name, *args, **kwargs):
            if name == 'anthropic':
                return mock_anthropic
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_mock

        provider = ClaudeProvider("test-key")
        result = provider.validate_api_key()

        self.assertTrue(result)
        self.assertIsNotNone(provider.client)

    def test_validate_api_key_missing(self):
        """Test API key validation with missing key."""
        provider = ClaudeProvider("")
        result = provider.validate_api_key()
        self.assertFalse(result)

    def test_send_message_adds_to_history(self):
        """Test that messages are added to history structure."""
        provider = ClaudeProvider("test-key")

        # Manually add messages to simulate conversation
        provider.add_to_history("user", "Test message")
        provider.add_to_history("assistant", "Test response")

        # Verify history
        self.assertEqual(len(provider.conversation_history), 2)
        self.assertEqual(provider.conversation_history[0]["content"], "Test message")
        self.assertEqual(provider.conversation_history[1]["content"], "Test response")


class TestChatGPTProvider(unittest.TestCase):
    """Tests for ChatGPT provider specific functionality."""

    @patch('builtins.__import__')
    def test_validate_api_key_success(self, mock_import):
        """Test successful API key validation for ChatGPT."""
        mock_openai = Mock()
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client

        def import_mock(name, *args, **kwargs):
            if name == 'openai':
                return mock_openai
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_mock

        provider = ChatGPTProvider("test-key")
        result = provider.validate_api_key()

        self.assertTrue(result)
        self.assertIsNotNone(provider.client)

    def test_validate_api_key_missing(self):
        """Test API key validation with missing key."""
        provider = ChatGPTProvider("")
        result = provider.validate_api_key()
        self.assertFalse(result)


class TestGeminiProvider(unittest.TestCase):
    """Tests for Gemini provider specific functionality."""

    @patch('builtins.__import__')
    def test_validate_api_key_success(self, mock_import):
        """Test successful API key validation for Gemini."""
        mock_genai = Mock()
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        def import_mock(name, *args, **kwargs):
            if 'google' in name or 'genai' in name:
                return mock_genai
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_mock

        provider = GeminiProvider("test-key")
        result = provider.validate_api_key()

        self.assertTrue(result)
        self.assertIsNotNone(provider.client)

    def test_validate_api_key_missing(self):
        """Test API key validation with missing key."""
        provider = GeminiProvider("")
        result = provider.validate_api_key()
        self.assertFalse(result)


class TestSpecialCommands(unittest.TestCase):
    """Tests for special commands functionality."""

    def test_help_command_output(self):
        """Test that help command produces expected output."""
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            show_help()

        output = captured_output.getvalue()
        self.assertIn("/help", output)
        self.assertIn("/clear", output)
        self.assertIn("/exit", output)
        self.assertIn("/quit", output)


class TestCreateProvider(unittest.TestCase):
    """Tests for the create_provider function."""

    def test_create_claude_provider_no_key(self):
        """Test creating Claude provider without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('claude')
            self.assertIsNone(provider)

    def test_create_chatgpt_provider_no_key(self):
        """Test creating ChatGPT provider without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('chatgpt')
            self.assertIsNone(provider)

    def test_create_gpt_alias_no_key(self):
        """Test creating provider with 'gpt' alias without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('gpt')
            self.assertIsNone(provider)

    def test_create_gemini_provider_no_key(self):
        """Test creating Gemini provider without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = create_provider('gemini')
            self.assertIsNone(provider)

    def test_create_openrouter_not_implemented(self):
        """Test that OpenRouter returns None (not yet implemented)."""
        provider = create_provider('openrouter')
        self.assertIsNone(provider)

    def test_create_unknown_provider(self):
        """Test creating unknown provider."""
        provider = create_provider('unknown')
        self.assertIsNone(provider)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling scenarios."""

    def test_history_management(self):
        """Test that conversation history can be managed correctly."""
        provider = ClaudeProvider("test-key")

        # Add messages
        provider.add_to_history("user", "Message 1")
        provider.add_to_history("assistant", "Response 1")
        self.assertEqual(len(provider.conversation_history), 2)

        # Simulate error rollback (removing last user message)
        provider.conversation_history.pop()
        self.assertEqual(len(provider.conversation_history), 1)

        # Clear history
        provider.conversation_history.clear()
        self.assertEqual(len(provider.conversation_history), 0)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLoadingAnimation))
    suite.addTests(loader.loadTestsFromTestCase(TestArgumentParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestProviderInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestClaudeProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestChatGPTProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestGeminiProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestSpecialCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestCreateProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
