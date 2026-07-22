# Sentinel AI

![CI](https://github.com/vaibhavgshete/Sentinal-AI/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Ollama](https://img.shields.io/badge/powered%20by-Ollama-black)

Sentinel AI is a local error monitoring tool that watches a log file, analyzes new errors with Ollama, and reuses cached results so repeated issues are answered instantly.

The project ships as an installable Python package with a CLI. The `sentinel_ai/` package is the single implementation we keep and maintain.

## Features

- Watches a log file in real time
- Reads only newly appended log content
- Reuses cached analyses for repeated errors
- Normalizes repeated errors so small formatting changes still match
- Calls a local Ollama model only when an error is new
- Stores results in persistent JSON memory

## Installation

## Prerequisites

Before installing Sentinel AI, make sure your system has:

- Python 3.10 or newer
- `pip` available in your terminal
- Ollama installed locally
- An Ollama model pulled locally, such as `gemma3:4b`

You can verify Python and pip with:

```bash
python --version
pip --version
```

### 1. Install Ollama

Install Ollama locally and make sure it is available on your machine.

### 2. Pull a Model

```bash
ollama pull gemma3:4b
```

### 3. Install Sentinel AI

From the project root directory, run:

```bash
pip install -e .
```

That command should be run in the same folder as `pyproject.toml`.

## Quick Start

### Terminal 1

```bash
ollama serve
```

If Ollama is already running on your system, you do not need to run `ollama serve` again. On some Windows setups, Ollama starts automatically at login. In that case, starting it manually can fail with a port `11434` already-in-use error.

### Terminal 2

```bash
sentinel-ai watch --log log.txt
```

You can also run the package module directly during development:

```bash
python -m sentinel_ai watch --log log.txt
```

An empty `log.txt` is included in the project root so you can try the default POC flow immediately.

## CLI Commands

Watch a log file:

```bash
sentinel-ai watch --log log.txt
```

By default, Sentinel AI stores cached analyses in `memory.json`.

Use a custom memory file when you want to keep cache history separate by project:

```bash
sentinel-ai watch --log log.txt --memory-file project-a-memory.json
```

Analyze one error directly:

```bash
sentinel-ai analyze "ModuleNotFoundError: No module named 'numpy'"
```

List cached memory entries:

```bash
sentinel-ai memory list --memory-file memory.json
```

## Example Output

Running `sentinel-ai analyze` against a real error, with a local Ollama model:

```bash
$ sentinel-ai analyze "ModuleNotFoundError: No module named 'numpy'"
[*] Calling Ollama...
ROOT CAUSE: The error "ModuleNotFoundError: No module named 'numpy'" indicates that
Python cannot find the NumPy library on your system. This usually happens because
NumPy is either not installed at all, or it's not accessible to the current Python
environment where you're running your code.

FIX: You need to install the NumPy library using a package installer like pip. Pip
will download and install NumPy along with its dependencies into your Python
environment.

SHELL COMMAND: `pip install numpy`
```

On a second, identical error, Sentinel AI skips the model call entirely and serves the cached analysis instantly:

```text
[*] Checking memory...
[OK] Found in memory! (Reusing previous analysis)
```

## How It Works

1. Sentinel AI watches a log file for changes.
2. When the file changes, it reads only the new content since the last processed position.
3. It extracts the latest error block from that new content.
4. It normalizes the error text and checks the memory file for a cached match.
5. If a match exists, it prints the saved analysis immediately.
6. If the error is new, it sends the error to Ollama.
7. The response is printed and saved to memory only if the Ollama call succeeded.
8. Older memory entries using `analysis` are still loaded and normalized to the current `response` schema.

## Running Tests

Install the dev dependencies and run the suite with `pytest`:

```bash
pip install -e ".[dev]"
pytest -v
```

Tests run automatically on every push and pull request via GitHub Actions (`.github/workflows/ci.yml`), across Python 3.10/3.11/3.13 on Linux and Windows, followed by a build job that packages and validates the sdist/wheel.

## Project Structure

```text
sentinel-ai/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
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
|-- tests/
|   |-- test_app.py
|   |-- test_memory.py
|   |-- test_ollama_client.py
|   `-- test_parsing.py
|-- ARCHITECTURE.md
|-- pyproject.toml
`-- README.md
```

## Architecture Notes

- `pyproject.toml` defines the package metadata and the `sentinel-ai` console script.
- `sentinel_ai/cli.py` is the user-facing entrypoint.
- `sentinel_ai/app.py` coordinates log reading, parsing, memory lookups, and Ollama calls.
- `log.txt` is included as an empty starter file for quick POC testing.
- Runtime data such as `memory.json` are user files, not tracked project source files.
- You can keep separate memory files per project when you want independent cached error histories.

For more implementation detail, see `ARCHITECTURE.md`.

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

Older entries that use `analysis` are still loaded correctly and rewritten into the `response` format.

## Notes

- Matching is normalized exact matching, not semantic similarity yet.
- The agent is optimized for logs that grow over time.
- If Ollama is down or times out, the failure message is shown but not cached.

## Troubleshooting

### Ollama is not running

```bash
ollama serve
```

If you see an error saying port `127.0.0.1:11434` is already in use, Ollama is probably already running. In that case, skip `ollama serve` and continue using Sentinel AI.

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

Apache-2.0
