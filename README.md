# Sentinel AI

Sentinel AI is a local error monitoring agent that watches a log file, analyzes new errors with Ollama, and caches past results so repeated issues are answered instantly.

## Overview

Sentinel AI helps you debug faster by:
- Watching a log file in real time
- Reading only newly added log content instead of reprocessing the whole file
- Reusing cached analyses for repeated errors
- Normalizing repeated errors so small formatting differences still match
- Calling a local Ollama model only when an error is new
- Storing results in persistent JSON memory

This project is now structured as an installable Python package with a CLI, which is the recommended path for shipping the first version.

## Features

- Memory reuse for repeated errors
- Local-only analysis with Ollama
- Incremental log reading for append-style logs
- Normalized exact matching for small formatting differences
- Persistent JSON memory with backward-compatible loading
- Protection against caching transient Ollama failures
- Installable CLI package

## Installation

### 1. Install Ollama

Download Ollama for Windows and make sure it is available locally.

### 2. Pull a Model

```bash
ollama pull gemma3:4b
```

### 3. Install Sentinel AI

For local development:

```bash
pip install -e .
```

If you prefer the old dependency-only flow, this still works:

```bash
pip install -r requirements.txt
```

## Quick Start

### Terminal 1

```bash
ollama serve
```

### Terminal 2

Recommended CLI usage:

```bash
sentinel-ai watch --log log.txt
```

Alternative local development entrypoints:

```bash
python -m sentinel_ai watch --log log.txt
python agent.py
```

## CLI Commands

Watch a log file:

```bash
sentinel-ai watch --log log.txt --memory-file memory.json
```

Analyze one error directly:

```bash
sentinel-ai analyze "ModuleNotFoundError: No module named 'numpy'"
```

List cached memory entries:

```bash
sentinel-ai memory list --memory-file memory.json
```

## How It Works

1. Sentinel AI watches a log file for changes.
2. When the file changes, it reads only the new content since the last processed position.
3. It extracts the latest error block from that new content.
4. It normalizes the error text and checks `memory.json` for a cached match.
5. If a match exists, it prints the saved analysis immediately.
6. If the error is new, it sends the error to Ollama.
7. The response is printed and saved to memory only if the Ollama call succeeded.
8. Legacy memory entries using `analysis` are automatically normalized to the current `response` schema.

## Project Structure

```text
sentinel-ai/
|-- sentinel_ai/
|   |-- __init__.py
|   |-- __main__.py
|   |-- app.py
|   |-- cli.py
|   |-- config.py
|   |-- memory.py
|   |-- ollama_client.py
|   |-- parsing.py
|   `-- watcher.py
|-- agent.py
|-- log.txt
|-- memory.json
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Packaging Notes

- `pyproject.toml` defines the package metadata and the `sentinel-ai` console script.
- `agent.py` is now a compatibility wrapper that launches `watch`.
- The main shipping target is the CLI package, not an editor plugin.

## Memory Format

Sentinel AI stores memory in canonical JSON array format:

```json
[
  {
    "error": "ModuleNotFoundError: No module named 'numpy'",
    "response": "ROOT CAUSE: ...\n\nFIX: ...\n\nSHELL COMMAND: pip install numpy",
    "timestamp": "2026-04-05T20:08:49.981074"
  }
]
```

Older entries that use `analysis` are still loaded correctly and are rewritten into the `response` format.

## Notes

- Matching is normalized exact matching, not semantic similarity yet.
- The agent is optimized for logs that grow over time.
- If Ollama is down or times out, the failure message is shown but not cached.

## Troubleshooting

### Ollama is not running

```bash
ollama serve
```

### Missing Python packages

```bash
pip install -e .
```

### File changes are not detected

- Confirm `--log` points to the right file.
- Save the file explicitly in your editor.
- If your editor replaces files on save, Sentinel AI handles create, modify, and move events.

## Future Improvements

- Fuzzy or embedding-based similarity for near-duplicate errors
- Multiple log file support
- Error frequency analytics
- Notifications or integrations
- Better stack-trace extraction heuristics
- Tests and release automation

## License

MIT
