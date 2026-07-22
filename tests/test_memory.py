import json

from sentinel_ai.memory import (
    find_similar_error,
    load_memory,
    normalize_error_text,
    save_memory,
    save_memory_entry,
)


def test_normalize_collapses_whitespace_and_lowercases():
    assert normalize_error_text("  ModuleNotFoundError:\n\tNo module  named 'numpy' ") == (
        "modulenotfounderror: no module named 'numpy'"
    )


def test_normalize_handles_none():
    assert normalize_error_text(None) == ""


def test_load_memory_missing_file_returns_empty_list(tmp_path):
    assert load_memory(tmp_path / "missing.json") == []


def test_load_memory_empty_file_returns_empty_list(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text("", encoding="utf-8")
    assert load_memory(memory_file) == []


def test_load_memory_reads_canonical_json_array(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text(
        json.dumps([{"error": "boom", "response": "fix it", "timestamp": "2026-01-01T00:00:00"}]),
        encoding="utf-8",
    )
    entries = load_memory(memory_file)
    assert entries == [{"error": "boom", "response": "fix it", "timestamp": "2026-01-01T00:00:00"}]


def test_load_memory_normalizes_legacy_analysis_field(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text(
        json.dumps([{"error": "boom", "analysis": "legacy fix"}]),
        encoding="utf-8",
    )
    entries = load_memory(memory_file)
    assert entries == [{"error": "boom", "response": "legacy fix", "timestamp": None}]


def test_load_memory_skips_invalid_entries(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text(
        json.dumps(
            [
                {"error": "boom", "response": "fix"},
                {"error": "no response here"},
                {"response": "no error here"},
                "not-a-dict",
            ]
        ),
        encoding="utf-8",
    )
    entries = load_memory(memory_file)
    assert len(entries) == 1
    assert entries[0]["error"] == "boom"


def test_load_memory_handles_corrupt_json(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory_file.write_text("{not valid json", encoding="utf-8")
    assert load_memory(memory_file) == []


def test_save_memory_writes_canonical_json(tmp_path):
    memory_file = tmp_path / "memory.json"
    memory = [{"error": "boom", "response": "fix", "timestamp": None}]

    assert save_memory(memory_file, memory) is True
    assert json.loads(memory_file.read_text(encoding="utf-8")) == memory


def test_save_memory_entry_appends_with_timestamp(tmp_path):
    memory_file = tmp_path / "memory.json"

    assert save_memory_entry(memory_file, "boom", "fix") is True

    entries = load_memory(memory_file)
    assert len(entries) == 1
    assert entries[0]["error"] == "boom"
    assert entries[0]["response"] == "fix"
    assert entries[0]["timestamp"] is not None


def test_find_similar_error_matches_normalized_text(tmp_path):
    memory_file = tmp_path / "memory.json"
    save_memory_entry(memory_file, "ModuleNotFoundError: No module named 'numpy'", "pip install numpy")

    result = find_similar_error(memory_file, "modulenotfounderror:   no module named 'numpy'")
    assert result == "pip install numpy"


def test_find_similar_error_returns_none_when_no_match(tmp_path):
    memory_file = tmp_path / "memory.json"
    save_memory_entry(memory_file, "boom", "fix")

    assert find_similar_error(memory_file, "a completely different error") is None
