# ChatWith

A terminal-based chat interface for interacting with multiple LLM providers without leaving the command line.

## Overview

**ChatWith** is a Python-based CLI application that enables developers to chat with various Large Language Models (LLMs) directly from their terminal. It provides a unified interface for multiple LLM providers, eliminating the need to switch between different web interfaces or applications.

## Target Users

- Software developers
- DevOps engineers
- System administrators
- Anyone comfortable with terminal-based workflows
- Users who prefer staying in their development environment

## Core Objectives

1. **Single Entry Point**: One command to access multiple LLM providers
2. **Terminal Native**: Seamless integration with terminal workflows
3. **Simple Deployment**: Single Python file for easy installation and distribution
4. **Provider Agnostic**: Support for multiple LLM providers with a consistent interface

## Key Features

### MVP (Minimum Viable Product)

- [x] Interactive chat sessions with LLMs
- [x] Support for multiple LLM providers:
  - OpenAI (GPT models) - invoked as `chatgpt` or `gpt`
  - Anthropic (Claude models) - invoked as `claude`
  - Google (Gemini models) - invoked as `gemini`
  - OpenRouter (access to multiple models) - invoked as `openrouter`
- [x] Direct command-line invocation: `chatwith <provider>`
- [x] Streaming responses with real-time display
- [x] Loading animation while waiting for responses
- [x] Conversation history within a session
- [x] Clean, readable terminal output
- [x] Lazy API key validation (only check when provider is used)
- [x] Basic error handling and user feedback
- [x] Comprehensive test coverage
- [x] Custom system prompts per model (editable via `/system` command)

### Future Enhancements

- [ ] Model selection via command-line flags (e.g., `chatwith claude --model claude-opus-4`)
- [ ] Additional special command (`/model` to switch models)
- [ ] Color support for better terminal readability
- [ ] Conversation persistence (save/load chat history)
- [ ] Multi-line input support
- [ ] Syntax highlighting for code blocks
- [ ] Smart context window management (automatic truncation)
- [ ] Cost tracking per session
- [ ] System prompt customization
- [ ] Configuration file support
- [ ] Command history with search
- [ ] Export conversations to markdown
- [ ] Support for additional providers (Ollama, local models)

## Technical Specifications

### Technology Stack

- **Language**: Python 3.8+
- **Architecture**: Single-file application (`chatwith.py`)
- **Dependencies**: Official provider SDKs
  - `anthropic` - For Claude models
  - `openai` - For ChatGPT/GPT models
  - `google-generativeai` - For Gemini models
- **Configuration**: Environment variables for API keys
- **Installation**: Script with shebang, symlinked to PATH as `chatwith`

### File Structure

```
chatwith/
├── CHATWITH.md          # This specification
├── chatwith.py          # Main application (single file)
├── tests.py             # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── .env                 # API keys (gitignored)
├── .env.example         # Example environment file
├── .gitignore           # Git ignore patterns
└── README.md            # User documentation

~/.chatwith/             # User configuration directory
└── system-prompt.json   # Custom system prompts per model
```

### API Key Management

API keys should be stored in environment variables:
- `OPENAI_API_KEY` - Only required when using ChatGPT/GPT models
- `ANTHROPIC_API_KEY` - Only required when using Claude models
- `GOOGLE_API_KEY` - Only required when using Gemini models
- `OPENROUTER_API_KEY` - Only required when using OpenRouter

**Lazy Loading**: API keys are validated only when the corresponding provider is invoked. Users can install and use the tool with only the API keys they need.

### Default Models

Each provider uses a specific default model:
- **Claude** (`chatwith claude`): `claude-sonnet-4-5-20250929`
- **ChatGPT** (`chatwith chatgpt` or `chatwith gpt`): `gpt-5.2`
- **Gemini** (`chatwith gemini`): `gemini-2.5-flash`
- **OpenRouter** (`chatwith openrouter`): User will be prompted to select a model

**Note**: Model selection via command-line flags is deferred to a future phase.

### System Prompt Configuration

Custom system prompts can be configured per model:
- **Storage**: `~/.chatwith/system-prompt.json`
- **Format**: JSON with model names as keys
- **Editing**: `/system` command opens default text editor
- **Editor**: Uses `$EDITOR` environment variable, falls back to `vim`, `nano`, or `vi`

Example `system-prompt.json`:
```json
{
  "claude-sonnet-4-5-20250929": "You are a helpful coding assistant.",
  "gpt-5.2": "You are an expert programmer.",
  "gemini-2.5-flash": "You are a concise technical advisor."
}
```

### User Interface

**Startup Flow**:
1. User invokes with provider name: `chatwith claude`
2. Validate API key for selected provider (lazy check)
3. Display welcome message with selected model
4. Enter interactive chat mode

**Chat Interface**:
```
ChatWith [claude-sonnet-4-5-20250929]
─────────────────────────────────────

You: How do I reverse a string in Python?
...
Assistant: You can reverse a string in Python using slicing:

```python
text = "hello"
reversed_text = text[::-1]
print(reversed_text)  # Output: olleh
```

The [::-1] slice means "start at the end and move backwards by 1 step".

You: /exit
Goodbye!
```

Note: The `...` loading animation appears on a new line and clears when the response starts streaming.

**Special Commands**:
- `/exit` or `/quit` - Exit the application
- `/clear` - Clear conversation history
- `/help` - Show available commands
- `/system` - Edit custom system prompt for current model

**Future Commands** (Post-MVP):
- `/model` - Switch to a different model

## Implementation Details

### Core Components

1. **Provider Interface**: Abstract base class defining the interface for LLM providers
2. **Provider Implementations**: Concrete classes for each LLM provider (OpenAI, Anthropic, etc.)
3. **System Prompt Manager**: Manages custom system prompts per model, stored in `~/.chatwith/system-prompt.json`
4. **Chat Manager**: Handles conversation flow and history
5. **Input Handler**: Manages user input and special commands
6. **Output Formatter**: Formats and displays streaming responses cleanly
7. **Loading Animator**: Displays animated dots/spinner while waiting for responses

### Loading Animation

While waiting for the LLM response to start streaming, display an animated indicator:
- Appears on a new line after the user's message
- Simple dots animation: `.`, `..`, `...`, repeating
- Clears automatically when response starts streaming
- Provides visual feedback that the request is being processed

Example:
```
You: What is Python?
...
Assistant: Python is a high-level programming language...
```

### System Prompt Implementation

Custom system prompts allow users to customize model behavior:

**Storage**:
- Location: `~/.chatwith/system-prompt.json`
- Format: JSON object with model IDs as keys, prompt text as values
- Created on first use of `/system` command

**Editing Workflow**:
1. User types `/system` command in chat
2. System opens text editor with current prompt (if any)
3. User edits and saves the file
4. System updates the JSON configuration
5. New prompt applies to all subsequent messages

**Editor Selection**:
- Checks `$EDITOR` environment variable
- Falls back to `$VISUAL` if `$EDITOR` not set
- Tries common editors: `vim`, `nano`, `vi` (in order)
- Shows error if no editor found

**Provider Integration**:
- **Claude (Anthropic)**: Passed as `system` parameter to API
- **ChatGPT (OpenAI)**: Added as first message with `role: "system"`
- **Gemini (Google)**: Set via `system_instruction` in config

**Example Configuration**:
```json
{
  "claude-sonnet-4-5-20250929": "You are a helpful Python expert. Be concise.",
  "gpt-5.2": "You specialize in web development with React and TypeScript.",
  "gemini-2.5-flash": "Answer in a clear, technical manner."
}
```

### Error Handling

- Missing API keys: Clear error message with setup instructions (only shown when provider is used)
- API errors: Display error message and allow retry
- Network issues: Timeout handling with user feedback
- Invalid provider name: Show available providers and exit
- Invalid model selection: List available models and re-prompt

### Testing Strategy

The `tests.py` file should include:

**Unit Tests**:
- Provider interface implementations
- Message formatting
- Command parsing
- API key validation logic
- Loading animation logic

**Integration Tests**:
- Mock API responses for each provider
- Streaming response handling
- Error handling flows
- Command-line argument parsing

**Test Coverage Goals**:
- Minimum 80% code coverage
- All critical paths tested
- Edge cases and error conditions covered

### Data Structures

**Message Format**:
```python
{
    "role": "user" | "assistant",
    "content": "message text"
}
```

**Conversation History**:
```python
[
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
]
```

**Context Management**:
- Keep all messages in the conversation history for the entire session
- Send full conversation history with each API request
- No automatic truncation (rely on provider's context window limits)
- Future enhancement: Implement smart context window management

## Usage Examples

### Basic Usage

```bash
# Chat with Claude
chatwith claude

# Chat with ChatGPT
chatwith chatgpt
# or
chatwith gpt

# Chat with Gemini
chatwith gemini

# Chat with OpenRouter
chatwith openrouter
```

### Environment Setup

```bash
# Set API keys (only for providers you want to use)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."

# Run with your chosen provider
chatwith claude
```

### Installation

The script includes a shebang (`#!/usr/bin/env python3`) for direct execution.

```bash
# Make the script executable
chmod +x chatwith.py

# Symlink to PATH (allows running as 'chatwith' instead of 'chatwith.py')
ln -s $(pwd)/chatwith.py /usr/local/bin/chatwith

# Now you can run:
chatwith claude
```

## Development Phases

### Phase 1: Foundation (MVP)
- Command-line argument parsing (provider selection)
- Single provider support (start with Anthropic/Claude)
- Streaming response support with official SDK
- Loading animation while waiting (new line, dots)
- Basic chat loop with conversation history (keep all messages)
- Lazy API key validation
- Basic special commands (`/exit`, `/quit` only)

### Phase 2: Multi-Provider
- Add OpenAI/ChatGPT support
- Add Google Gemini support
- Add OpenRouter support
- Unified provider interface
- Provider-specific model defaults

### Phase 3: Testing & Polish
- Comprehensive test suite (tests.py)
- Error handling improvements
- Special commands (/exit, /clear, /help)
- Better output formatting

### Phase 4: Advanced Features
- Conversation persistence
- Multi-line input
- Model selection flags
- Cost tracking

## Success Criteria

The application is considered successful when:

1. **Functional**: Users can chat with multiple LLM providers using simple commands (`chatwith claude`, etc.)
2. **Streaming**: Responses stream in real-time with smooth display
3. **Reliable**: Handles errors gracefully without crashing
4. **Simple**: Single file, easy to install and run with `chatwith <provider>`
5. **Fast**: Minimal startup time and responsive interactions
6. **Visual Feedback**: Loading animation provides clear feedback while waiting
7. **Flexible**: API keys only required for providers being used
8. **Customizable**: System prompts editable per model via `/system` command
9. **Clear**: Output is readable and well-formatted
10. **Tested**: Comprehensive test coverage (80%+)
11. **Documented**: Clear README with setup and usage instructions

## Non-Goals

To maintain simplicity, the following are explicitly out of scope:

- GUI or web interface
- Complex configuration systems
- Built-in model fine-tuning
- Voice input/output
- Image or multimodal support (MVP)
- Distributed or multi-user support
- Plugin system

## Design Decisions

The following questions have been resolved:

- ✅ **Default models**: Claude Sonnet 4.5, GPT-5.2, Gemini 2.5 Flash
- ✅ **Context management**: Keep all messages (no automatic truncation)
- ✅ **Dependencies**: Use official provider SDKs for better streaming support
- ✅ **Special commands**: `/exit`, `/quit`, `/help`, `/clear`, `/system`
- ✅ **Loading animation**: Display on new line with dots
- ✅ **Color support**: Plain text for MVP, colors deferred to future
- ✅ **Model selection flags**: Deferred to future enhancement
- ✅ **Script installation**: `chatwith.py` with shebang, symlinked as `chatwith`
- ✅ **System prompts**: Editable per-model via `/system` command, stored in `~/.chatwith/system-prompt.json`

## Open Questions

- Should we support local models (Ollama) in Phase 2 or defer to later?
- What should the API timeout be for requests?
- Should we display token count or cost information during the session?

## References

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
