# ChatWith

A terminal-based chat interface for interacting with multiple Large Language Model (LLM) providers directly from your command line.

## Overview

ChatWith allows you to chat with Claude, ChatGPT, and Gemini without leaving your terminal. It provides a unified interface with streaming responses, conversation history, and customizable system prompts for each model.

## Features

- **Multiple LLM Providers**: Chat with Claude, ChatGPT, or Gemini using a single tool
- **Streaming Responses**: See responses appear in real-time as they're generated
- **Conversation History**: Full context maintained throughout your session
- **Custom System Prompts**: Configure each model's behavior to your preferences
- **Simple Commands**: Easy-to-use slash commands for common operations
- **Lightweight**: Single Python file with minimal dependencies

## Requirements

- Python 3.8 or higher
- API keys for the providers you want to use

## Installation

### 1. Clone or Download

Download the repository or copy the `chatwith.py` file to your machine.

### 2. Install Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using uv (faster):
```bash
uv pip install -r requirements.txt
```

The required packages are:
- `anthropic` - For Claude models
- `openai` - For ChatGPT/GPT models
- `google-genai` - For Gemini models

### 3. Configure API Keys

You need API keys for the providers you want to use. Get your keys from:

- **Claude**: https://console.anthropic.com/
- **ChatGPT**: https://platform.openai.com/api-keys
- **Gemini**: https://aistudio.google.com/app/apikey

#### Option 1: Environment Variables

Set environment variables directly:
```bash
export ANTHROPIC_API_KEY='your-anthropic-key-here'
export OPENAI_API_KEY='your-openai-key-here'
export GOOGLE_API_KEY='your-google-key-here'
```

#### Option 2: Use .env File

Create a `.env` file in the project directory:
```bash
# ChatWith API Keys
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
```

Then load it before running:
```bash
set -a && source .env && set +a
```

### 4. Make Executable and Add to PATH

Make the script executable:
```bash
chmod +x chatwith.py
```

Create a symlink to use it as `chatwith`:
```bash
sudo ln -s $(pwd)/chatwith.py /usr/local/bin/chatwith
```

Now you can run `chatwith` from anywhere.

## Usage

### Starting a Chat Session

Chat with Claude:
```bash
chatwith claude
```

Chat with ChatGPT:
```bash
chatwith chatgpt
# or
chatwith gpt
```

Chat with Gemini:
```bash
chatwith gemini
```

### Example Session

````
$ chatwith claude
ChatWith [claude-sonnet-4-5-20250929]
─────────────────────────────────────
Type /help for available commands

You: What is Python?
...
Assistant: Python is a high-level, interpreted programming language known for its
simplicity and readability. It's widely used for web development, data analysis,
artificial intelligence, and automation.

You: Give me a hello world example
...
Assistant: Here's a simple Hello World in Python:

```python
print("Hello, World!")
```

That's it! Python's syntax is designed to be clean and intuitive.

You: /exit
Goodbye!
````

## Commands

ChatWith supports several special commands that you can use during a chat session. All commands start with a forward slash (`/`).

### /help

Display a list of all available commands.

```
You: /help

Available commands:
  /help   - Show this help message
  /clear  - Clear conversation history
  /cls    - Clear the terminal screen
  /system - Edit custom system prompt for current model
  /exit   - Exit the application
  /quit   - Exit the application
```

### /clear

Clear the conversation history. The model will no longer remember previous messages.

```
You: /clear
Conversation history cleared.
```

This is useful when you want to start a fresh conversation without restarting the application.

### /cls

Clear the terminal screen, similar to the `clear` command or Command-L on Mac. This doesn't affect conversation history.

```
You: /cls
```

This is useful when your terminal gets cluttered and you want a clean view.

### /system

Edit the custom system prompt for the current model. This opens your default text editor where you can specify how you want the model to behave.

```
You: /system
```

This will open your text editor (determined by the `$EDITOR` environment variable, or defaults to `vim`, `nano`, or `vi`). Edit the prompt, save, and close the editor.

Example system prompts:
- "You are a helpful Python expert. Be concise and provide code examples."
- "You specialize in web development. Focus on React and TypeScript."
- "Answer in a clear, technical manner with minimal explanations."

System prompts are saved in `~/.chatwith/system-prompt.json` and persist across sessions.

### /exit or /quit

Exit the ChatWith application.

```
You: /exit
Goodbye!
```

You can also use `Ctrl+C` or `Ctrl+D` to exit.

## Configuration

### System Prompts

System prompts allow you to customize how each model behaves. They are stored per-model in `~/.chatwith/system-prompt.json`.

**To edit a system prompt:**
1. Start a chat session with your chosen provider
2. Type `/system`
3. Your default editor will open
4. Write your system prompt
5. Save and close the editor

**Example configuration file** (`~/.chatwith/system-prompt.json`):
```json
{
  "claude-sonnet-4-5-20250929": "You are a helpful coding assistant specializing in Python.",
  "gpt-5.2": "You are an expert in web development with React and TypeScript.",
  "gemini-2.5-flash": "Be concise and technical in your responses."
}
```

**Setting your default editor:**

The `/system` command uses your default text editor. Set it with:
```bash
export EDITOR=nano  # or vim, emacs, code, etc.
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Default Models

ChatWith uses these models by default:

- **Claude**: `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5)
- **ChatGPT**: `gpt-5.2` (GPT-5.2)
- **Gemini**: `gemini-2.5-flash` (Gemini 2.5 Flash)

## Troubleshooting

### "Error: ANTHROPIC_API_KEY environment variable not set"

You haven't set the API key for the provider you're trying to use. Follow the [Configure API Keys](#3-configure-api-keys) section above.

Note: You only need to set the API key for providers you actually want to use. For example, if you only use Claude, you only need `ANTHROPIC_API_KEY`.

### "Error: 'anthropic' package not installed"

The required Python package isn't installed. Run:
```bash
pip install -r requirements.txt
```

### "Error: No text editor found"

The `/system` command couldn't find a text editor. Set your `$EDITOR` environment variable:
```bash
export EDITOR=nano
```

Or install a common editor like `vim` or `nano`.

### Streaming responses are slow or choppy

This is usually due to network latency or API rate limits. The streaming feature displays tokens as they arrive from the API server.

### Python version error

ChatWith requires Python 3.8 or higher. Check your version:
```bash
python3 --version
```

If you need to upgrade Python, visit https://www.python.org/downloads/

## Tips and Best Practices

### Conversation Management

- Use `/clear` when you want to start a new topic or the context becomes too large
- The application keeps all messages in history by default for better context
- Each session is independent - history doesn't persist between sessions

### System Prompts

- Keep system prompts concise and specific
- Test different prompts to find what works best for your use case
- You can delete a system prompt by opening `/system` and leaving the file empty

### Multiple Providers

- Different models have different strengths - Claude excels at analysis, GPT at creative tasks, Gemini at speed
- You can run multiple instances of ChatWith simultaneously in different terminal windows
- System prompts are per-model, so each provider can have different behavior

### API Costs

- Be aware that API calls cost money (except for free tiers)
- Claude and ChatGPT charge per token
- Check your provider's pricing page for current rates
- Use `/clear` to reduce context size if needed

## Development

### Running Tests

The project includes a comprehensive test suite:
```bash
python3 tests.py
```

This runs 30+ tests covering all core functionality.

### Project Structure

```
chatwith/
├── chatwith.py          # Main application (single file)
├── tests.py             # Test suite
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── CHATWITH.md          # Technical specification
└── .env                 # Your API keys (not in git)

~/.chatwith/
└── system-prompt.json   # Your custom system prompts
```

## License

This project is provided as-is for personal and educational use.

## Support

For issues, questions, or contributions, please refer to the project repository or documentation.

## Changelog

### Current Version

- Multi-provider support (Claude, ChatGPT, Gemini)
- Streaming responses with loading animation
- Conversation history management
- Custom system prompts per model
- Special commands (/help, /clear, /cls, /system, /exit)
- Comprehensive test coverage

## Acknowledgments

Built using official SDKs from:
- Anthropic (Claude)
- OpenAI (ChatGPT)
- Google (Gemini)
