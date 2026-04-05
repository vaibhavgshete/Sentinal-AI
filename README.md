# Local AI Agent

A simple Python agent that monitors `log.txt` for errors, analyzes them using Ollama, and saves responses to `memory.json`.

## Setup

### 1. Install Ollama
Download from https://ollama.ai for Windows

### 2. Pull the Model
```powershell
ollama pull gemma3:4b
```

### 3. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

Or manually:
```powershell
pip install watchdog requests
```

## Running the Agent

### Terminal 1 - Start Ollama Server
```powershell
ollama serve
```
This will start the API on `http://localhost:11434`

### Terminal 2 - Start the Agent
```powershell
python agent.py
```

## How It Works

1. **File Watching**: Agent monitors `log.txt` for changes
2. **Error Detection**: When `log.txt` is modified, it reads the content
3. **Analysis**: Sends the error to Ollama (gemma3:4b model)
4. **Response**: Gets root cause, fix recommendations, and shell commands
5. **Memory**: Saves error + analysis to `memory.json` with timestamp

## Project Structure

```
local-ai-agent/
├── agent.py          # Main agent code
├── log.txt           # Error/log input file
├── memory.json       # Persistent memory of all analyses
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Example Usage

### Test Case 1: Python Module Error

1. Open `log.txt` and replace content with:
```
ModuleNotFoundError: No module named 'numpy'. Install with: pip install numpy
```

2. Save the file

3. Watch the terminal - agent will:
   - Detect the change
   - Query Ollama
   - Print analysis with root cause, fix, and shell command
   - Save to `memory.json`

### Expected Output:
```
============================================================
[LOG] New error detected at 2026-04-05 10:30:45
============================================================
Content:
ModuleNotFoundError: No module named 'numpy'. Install with: pip install numpy

[*] Querying Ollama...
[ANALYSIS]
ROOT CAUSE: The numpy package is not installed in the Python environment.

FIX: Install the numpy package using pip, which is Python's package manager.

SHELL COMMAND: pip install numpy

============================================================

[*] Saved to memory.json
```

### Test Case 2: File Permission Error

1. Update `log.txt`:
```
PermissionError: [Errno 13] Permission denied: 'C:\\important_file.txt'
```

2. Save and observe the analysis

## Memory File Format

The `memory.json` file maintains a history of all errors and analyses:

```json
[
  {
    "timestamp": "2026-04-05T10:30:45.123456",
    "error": "ModuleNotFoundError: No module named 'numpy'...",
    "analysis": "ROOT CAUSE: The numpy package is not installed...\nFIX: Install the numpy package...\nSHELL COMMAND: pip install numpy"
  },
  {
    "timestamp": "2026-04-05T10:35:22.654321",
    "error": "PermissionError: [Errno 13] Permission denied...",
    "analysis": "ROOT CAUSE: The user account doesn't have read permissions...\n..."
  }
]
```

## Requirements

- Python 3.7+
- Ollama running locally (http://localhost:11434)
- `watchdog` - for file system monitoring
- `requests` - for HTTP API calls

## Notes

- Agent ignores duplicate errors (same content)
- Always start Ollama server first
- The model runs on CPU (fast with gemma3:4b)
- Ctrl+C stops the agent

## Troubleshooting

### "Ollama not running"
Make sure you started `ollama serve` in another terminal

### "ModuleNotFoundError: No module named 'watchdog'"
Run: `pip install -r requirements.txt`

### Agent not detecting file changes
- Save the file explicitly (Ctrl+S)
- Make sure you're editing the correct `log.txt` in the same directory

## License

This is a simple educational project. Feel free to modify and extend it.
