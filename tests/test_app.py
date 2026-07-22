from sentinel_ai.app import LogProcessor
from sentinel_ai.config import Settings


def make_processor(tmp_path, log_name="log.txt", memory_name="memory.json"):
    settings = Settings(log_file=tmp_path / log_name, memory_file=tmp_path / memory_name)
    return LogProcessor(settings=settings)


def test_prime_state_sets_read_position_to_existing_file_size(tmp_path):
    processor = make_processor(tmp_path)
    processor.settings.log_file.write_text("already here", encoding="utf-8")

    processor.prime_state()

    assert processor.last_read_position == len("already here")


def test_prime_state_handles_missing_log_file(tmp_path):
    processor = make_processor(tmp_path)

    processor.prime_state()

    assert processor.last_read_position == 0


def test_read_new_log_content_returns_only_appended_text(tmp_path):
    processor = make_processor(tmp_path)
    processor.settings.log_file.write_text("first", encoding="utf-8")
    processor.prime_state()

    with processor.settings.log_file.open("a", encoding="utf-8") as file_obj:
        file_obj.write("second")

    assert processor.read_new_log_content() == "second"


def test_read_new_log_content_resets_position_on_truncation(tmp_path):
    processor = make_processor(tmp_path)
    processor.settings.log_file.write_text("a long first line", encoding="utf-8")
    processor.prime_state()

    processor.settings.log_file.write_text("short", encoding="utf-8")

    assert processor.read_new_log_content() == "short"


def test_read_new_log_content_returns_empty_string_when_log_missing(tmp_path):
    processor = make_processor(tmp_path)

    assert processor.read_new_log_content() == ""
