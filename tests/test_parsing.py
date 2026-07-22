from sentinel_ai.parsing import extract_latest_error


def test_empty_content_returns_empty_string():
    assert extract_latest_error("") == ""


def test_none_content_returns_empty_string():
    assert extract_latest_error(None) == ""


def test_whitespace_only_content_returns_empty_string():
    assert extract_latest_error("   \n\n  ") == ""


def test_single_block_returns_whole_text():
    text = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'numpy'"
    assert extract_latest_error(text) == text


def test_multiple_blocks_returns_last_block():
    text = (
        "INFO: server started\n\n"
        "Traceback (most recent call last):\n"
        "ModuleNotFoundError: No module named 'numpy'"
    )
    assert extract_latest_error(text) == (
        "Traceback (most recent call last):\nModuleNotFoundError: No module named 'numpy'"
    )


def test_trailing_blank_lines_are_ignored():
    text = "First block\n\nSecond block\n\n\n"
    assert extract_latest_error(text) == "Second block"
