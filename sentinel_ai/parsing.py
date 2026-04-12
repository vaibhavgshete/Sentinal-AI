def extract_latest_error(new_content):
    """Heuristically extract the newest error block from appended log content."""
    text = (new_content or "").strip()
    if not text:
        return ""

    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    if blocks:
        return blocks[-1]

    return text
