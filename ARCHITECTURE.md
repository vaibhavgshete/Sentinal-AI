# Sentinel AI Architecture

## Purpose

Sentinel AI is a local log-watching and error-analysis tool. It watches a log file, extracts new error content, checks whether that error was already analyzed, and only calls Ollama when it needs a fresh answer.

## High-Level Flow

```mermaid
flowchart TD
    user[User / Terminal<br/>sentinel-ai watch]
    cli[sentinel_ai.cli<br/>command parsing]
    app[sentinel_ai.app<br/>LogProcessor]
    watcher[sentinel_ai.watcher<br/>file events]
    parsing[sentinel_ai.parsing<br/>latest error extraction]
    memory[sentinel_ai.memory<br/>load / save / cache match]
    ollama_client[sentinel_ai.ollama_client<br/>requests to Ollama]
    ollama[Local Ollama Server<br/>model inference]

    user --> cli
    cli --> app
    app --> watcher
    app --> parsing
    app --> memory
    app --> ollama_client
    ollama_client --> ollama
```

## Runtime Sequence

```mermaid
sequenceDiagram
    participant U as User / Terminal
    participant C as sentinel_ai.cli
    participant A as sentinel_ai.app
    participant W as sentinel_ai.watcher
    participant P as sentinel_ai.parsing
    participant M as sentinel_ai.memory
    participant O as sentinel_ai.ollama_client
    participant L as Local Ollama Server

    U->>C: Run `sentinel-ai watch`
    C->>A: Build Settings and start LogProcessor
    A->>M: Load and normalize memory
    A->>W: Start watching log file
    W-->>A: File change detected
    A->>A: Read newly appended log content
    A->>P: Extract latest error block
    P-->>A: Return latest error block
    A->>M: Check normalized cache match

    alt Cached match found
        M-->>A: Cached response
        A-->>U: Print saved analysis
    else New error
        M-->>A: Cache miss
        A->>O: Request fresh analysis
        O->>L: Send prompt to local model
        L-->>O: Return model response
        O-->>A: Structured analysis
        A->>M: Save new memory entry
        A-->>U: Print analysis
    end
```

## Components

### `sentinel_ai/cli.py`

Entry point for the packaged application.

Responsibilities:

- parse CLI commands
- build runtime settings
- dispatch to `watch`, `analyze`, and `memory list`

### `sentinel_ai/config.py`

Defines configuration values in one place using the `Settings` dataclass.

Responsibilities:

- log file path
- memory file path
- Ollama API URL
- model name

### `sentinel_ai/app.py`

Contains the main orchestration logic in `LogProcessor`.

Responsibilities:

- track read position in the log
- track last processed error
- coordinate parsing, memory lookup, Ollama calls, and saving

This is the main runtime brain of the app.

### `sentinel_ai/watcher.py`

Handles file-system watching.

Responsibilities:

- listen for create/modify/move events
- normalize watched file matching
- trigger the processing callback

### `sentinel_ai/parsing.py`

Responsible for turning newly appended log text into the error block to analyze.

Current heuristic:

- split on blank lines
- use the newest block

### `sentinel_ai/memory.py`

Handles persistent cache behavior.

Responsibilities:

- load memory entries
- normalize old schema (`analysis` -> `response`)
- save memory entries
- match repeated errors using normalized text

### `sentinel_ai/ollama_client.py`

Encapsulates communication with Ollama.

Responsibilities:

- build prompt
- call Ollama API
- return structured analysis
- surface connection and timeout failures

## Data Flow

```mermaid
flowchart LR
    log[log file]
    watcher[watcher.py]
    app[app.py]
    parsing[parsing.py]
    memory[memory.py]
    ollama[ollama_client.py]
    terminal[terminal output]

    log --> watcher
    watcher --> app
    app --> parsing
    parsing --> memory
    memory -->|cache hit| terminal
    memory -->|cache miss| ollama
    ollama --> memory
    memory --> terminal
```

## Files And Roles

```text
pyproject.toml             package metadata and console script
sentinel_ai/cli.py         CLI entrypoint
sentinel_ai/app.py         runtime orchestration
sentinel_ai/watcher.py     filesystem watching
sentinel_ai/parsing.py     log parsing
sentinel_ai/memory.py      cache persistence and lookup
sentinel_ai/config.py      settings definition
sentinel_ai/ollama_client.py Ollama API integration
README.md                  usage and installation guide
ARCHITECTURE.md            architecture overview
```

## Why This Structure Works

- The project is now shippable as a package.
- The CLI layer is separate from the business logic.
- File watching, parsing, memory, and model calls are isolated.
- Each part can be tested independently.
- Future integrations can reuse the core package instead of rebuilding the logic.

## Future Architecture Improvements

- add a dedicated `logging` layer instead of `print`
- introduce a richer parser for stack traces and multiline errors
- add tests around `parsing.py`, `memory.py`, and `app.py`
- support alternate inference backends beyond Ollama
