from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    log_file: Path = Path("log.txt")
    memory_file: Path = Path("memory.json")
    ollama_api_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "gemma3:4b"
