import json
from datetime import datetime
from pathlib import Path


def normalize_error_text(value):
    """Normalize error text so repeated variants reuse cached analysis."""
    return " ".join((value or "").split()).strip().lower()


def load_memory(memory_file: Path):
    """Load memory entries from disk and normalize legacy fields."""
    if not memory_file.exists():
        return []

    try:
        content = memory_file.read_text(encoding="utf-8").strip()
        if not content:
            return []
        if content.startswith("["):
            raw_entries = json.loads(content)
        else:
            raw_entries = [json.loads(line) for line in content.splitlines() if line.strip()]

        memory = []
        for entry in raw_entries:
            if not isinstance(entry, dict):
                continue

            response = entry.get("response") or entry.get("analysis")
            error = entry.get("error", "")
            if not error or not response:
                continue

            memory.append(
                {
                    "error": error,
                    "response": response,
                    "timestamp": entry.get("timestamp"),
                }
            )
        return memory
    except Exception as exc:
        print(f"[!] Error loading memory: {exc}")
        return []


def save_memory(memory_file: Path, memory):
    """Persist the full memory list using the canonical schema."""
    try:
        memory_file.write_text(json.dumps(memory, indent=2), encoding="utf-8")
        return True
    except Exception as exc:
        print(f"[!] Error writing memory: {exc}")
        return False


def save_memory_entry(memory_file: Path, error, response):
    """Save an analyzed error using the canonical response field."""
    try:
        memory = load_memory(memory_file)
        memory.append(
            {
                "error": error,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return save_memory(memory_file, memory)
    except Exception as exc:
        print(f"[!] Error saving to memory: {exc}")
        return False


def find_similar_error(memory_file: Path, error_content):
    """Return a cached response for normalized exact matches."""
    normalized_error = normalize_error_text(error_content)

    for entry in load_memory(memory_file):
        if normalize_error_text(entry.get("error", "")) == normalized_error:
            return entry.get("response", "")

    return None
