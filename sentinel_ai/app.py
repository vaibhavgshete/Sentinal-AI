from dataclasses import dataclass
from datetime import datetime

from .config import Settings
from .memory import find_similar_error, load_memory, normalize_error_text, save_memory, save_memory_entry
from .ollama_client import ask_llm, is_successful_analysis
from .parsing import extract_latest_error


APP_NAME = "Sentinel AI"


@dataclass(slots=True)
class LogProcessor:
    settings: Settings
    last_processed_error: str = ""
    last_read_position: int = 0

    def prime_state(self):
        """Initialize watcher state from existing files and repair legacy memory."""
        if self.settings.log_file.exists():
            self.last_read_position = self.settings.log_file.stat().st_size

        memory = load_memory(self.settings.memory_file)
        if memory:
            save_memory(self.settings.memory_file, memory)

    def read_new_log_content(self):
        """Read only newly appended content, while handling truncation/replacement."""
        if not self.settings.log_file.exists():
            return ""

        current_size = self.settings.log_file.stat().st_size
        if current_size < self.last_read_position:
            self.last_read_position = 0

        with self.settings.log_file.open("r", encoding="utf-8", errors="replace") as file_obj:
            file_obj.seek(self.last_read_position)
            new_content = file_obj.read()
            self.last_read_position = file_obj.tell()

        return new_content

    def process_log(self):
        """Process only new log content and reuse memory when possible."""
        try:
            new_content = self.read_new_log_content()
            error_content = extract_latest_error(new_content)
            if not error_content:
                return

            normalized_error = normalize_error_text(error_content)
            if not normalized_error or normalized_error == self.last_processed_error:
                return

            self.last_processed_error = normalized_error

            print("\n" + "=" * 70)
            print(f"[CHANGE DETECTED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            print(f"Latest Error Block:\n{error_content}\n")

            print("[*] Checking memory...")
            cached_response = find_similar_error(self.settings.memory_file, error_content)
            if cached_response:
                print("[OK] Found in memory! (Reusing previous analysis)\n")
                print("[ANALYSIS]")
                print(cached_response)
                print("=" * 70 + "\n")
                return

            print("[*] Not in memory, calling LLM...")
            response = ask_llm(
                error_content,
                model=self.settings.ollama_model,
                api_url=self.settings.ollama_api_url,
            )

            print("\n[ANALYSIS]")
            print(response)
            print("=" * 70 + "\n")

            if not is_successful_analysis(response):
                print("[!] Skipping memory save because analysis failed")
                return

            print("[*] Saving to memory...")
            if save_memory_entry(self.settings.memory_file, error_content, response):
                print(f"[OK] Saved to {self.settings.memory_file}")
            else:
                print(f"[!] Failed to save to {self.settings.memory_file}")
        except Exception as exc:
            print(f"[ERROR] Failed to process log: {str(exc)}")
