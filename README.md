# Sentinel AI

An intelligent error monitoring agent that watches for errors, analyzes them using local LLMs, and learns from past issues to avoid redundant API calls.

## Overview

Sentinel AI is a lightweight error monitoring and analysis tool that:
- **Watches** log files for new errors in real-time
- **Analyzes** errors using local Ollama LLM (no cloud dependency)
- **Learns** from previous analyses by caching results
- **Suggests** root causes, fixes, and shell commands
- **Remembers** all errors and solutions in persistent memory

Perfect for developers who want intelligent error diagnostics with zero external dependencies.

## Features

✨ **Memory Reuse** - Skip LLM calls for repeated errors  
⚡ **Fast** - Instant responses from memory  
🔒 **Local Only** - No cloud API keys needed  
📝 **Smart Logging** - Clear step-by-step output  
💾 **Persistent** - Error history in JSON format  
🔧 **Simple** - Single file, no frameworks  
🪟 **Windows Ready** - Works on Windows with Git Bash

## How It Works

1. **File Watching** - Sentinel monitors `log.txt` for changes
2. **Error Detection** - When new content is found, reads the error
3. **Memory Check** - Before calling LLM, checks if error was seen before
4. **Smart Analysis**:
   - If error exists in memory → return cached analysis instantly ⚡
   - If new error → call Ollama and save for future reference 🤖
5. **Response** - Gets root cause, fix recommendations, and shell commands
6. **Memory** - Saves all error + analysis pairs with timestamps

## Installation

### 1. Install Ollama

Download from https://ollama.ai for Windows

### 2. Pull the Model

```bash
ollama pull gemma3:4b
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install watchdog requests
```

## Quick Start

### Terminal 1 - Start Ollama Server

```bash
ollama serve
```

This starts the API on `http://localhost:11434`

### Terminal 2 - Run Sentinel AI

```bash
python agent.py
```

Monitor the output as Sentinel watches for errors!

## Usage

### Real-World Setup

Point Sentinel to your application's error log:

```python
LOG_FILE = "/path/to/your/app/error.log"  # Your app writes errors here
```

When your app encounters an error, it writes to the log file. Sentinel automatically:
- Detects the new error
- Analyzes it with Ollama
- Saves the solution to memory
- Next time same error occurs → instant response from memory! ⚡

### Development/Testing

For testing, manually edit `log.txt`:

#### Example 1: Python Module Error

1. Edit `log.txt`:
```
ModuleNotFoundError: No module named 'numpy'. Install with: pip install numpy
```

2. Save the file (Ctrl+S)

3. Watch Sentinel AI analyze it:
   ```
   [CHANGE DETECTED] 2026-04-05 21:00:51
   [*] Checking memory...
   [*] Not in memory, calling LLM...
   [ANALYSIS]
   ROOT CAUSE: The error "ModuleNotFoundError..." indicates...
   FIX: Install the package...
   SHELL COMMAND: pip install numpy
   [*] Saving to memory...
   ```

#### Example 2: Type Error (Memory Reuse)

1. Edit `log.txt` with:
```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

2. **First time**: Sentinel calls Ollama (5-10 seconds)

3. **Edit again with same error**, save again:
   ```
   [CHANGE DETECTED] 2026-04-05 21:05:12
   [*] Checking memory...
   [✓] Found in memory! (Reusing previous analysis)
   ```
   **Instant response!** ⚡ No LLM call!

## Project Structure

```
sentinel-ai/
├── agent.py          # Core sentinel agent
├── log.txt           # Error/log input file (monitored)
├── memory.json       # Persistent error memory (auto-created)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Memory File Format

`memory.json` stores all analyzed errors for future reference:

```json
[
  {
    "error": "ModuleNotFoundError: No module named 'numpy'...",
    "response": "ROOT CAUSE: The numpy package is not installed...\nFIX: Install the numpy package...\nSHELL COMMAND: pip install numpy",
    "timestamp": "2026-04-05T20:08:49.981074"
  },
  {
    "error": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
    "response": "ROOT CAUSE: You are attempting to use the addition operator...",
    "timestamp": "2026-04-05T21:01:18.210588"
  }
]
```

## Configuration

Edit `agent.py` to customize:

```python
LOG_FILE = "log.txt"                    # Change to your app's error log
MEMORY_FILE = "memory.json"             # Where to store memory
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Ollama endpoint
OLLAMA_MODEL = "gemma3:4b"              # Change to any Ollama model
```

## Requirements

- **Python 3.7+**
- **Ollama** running locally on `http://localhost:11434`
- `watchdog` - file system monitoring
- `requests` - HTTP API calls to Ollama

## Tips & Best Practices

### Performance

- **First error**: 5-10 seconds (LLM processing)
- **Repeated error**: <100ms (from memory)
- **Gemma3:4b** runs on CPU - no GPU needed!

### Best Practices

- Always start Ollama first with `ollama serve`
- Point `LOG_FILE` to your real application logs
- Let memory grow - more history = smarter sentinel
- Review `memory.json` occasionally to see patterns

### Extending with More Models

```bash
ollama pull llama2
ollama pull mistral
ollama pull neural-chat
```

Then change `OLLAMA_MODEL` in `agent.py`

## Troubleshooting

### "Ollama not running"
```bash
ollama serve
```

### "ModuleNotFoundError: No module named 'watchdog'"
```bash
pip install -r requirements.txt
```

### File changes not detected
- Save the file explicitly (Ctrl+S in editor)
- Ensure `LOG_FILE` path is correct and accessible

### No response from Ollama

Check if Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

Verify model exists:
```bash
ollama list
```

Pull model if needed:
```bash
ollama pull gemma3:4b
```

## Future Roadmap

Sentinel AI can be extended with:
- 🔗 Multiple log file monitoring
- 🤖 Embedding-based similarity (fuzzy matching for similar errors)
- 📊 Error pattern analytics and trending
- 🌐 Slack/Discord notifications
- 📈 Error frequency tracking and alerts
- 🔐 Security vulnerability detection
- ☁️ Multi-model support and model switching

## License

MIT - Feel free to use, modify, and extend!

## Contributing

Found a bug or have a feature request? Open an issue or submit a PR!

---

**Made for developers who want smart error diagnostics. Locally.**
