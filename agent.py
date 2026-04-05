import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, FileSystemEventHandler


# Configuration
LOG_FILE = "log.txt"
MEMORY_FILE = "memory.json"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

# Track last processed content to avoid processing same log twice
last_processed_content = ""


def load_memory():
    """Load memory from JSON file"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(memory):
    """Save memory to JSON file"""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def query_ollama(prompt):
    """Send prompt to Ollama and get response"""
    print("\n[*] Querying Ollama...")
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "[ERROR] Ollama not running. Start with: ollama serve"
    except Exception as e:
        return f"[ERROR] Failed to query Ollama: {str(e)}"


def analyze_error(error_content):
    """Analyze error/log content using Ollama"""
    prompt = f"""You are a helpful debugging assistant. Analyze the following error/log:

{error_content}

Provide your response in exactly this format:
ROOT CAUSE: [explain the root cause]

FIX: [explain how to fix it]

SHELL COMMAND: [provide a shell command to fix it, or "N/A" if not applicable]"""

    response = query_ollama(prompt)
    return response


def process_log():
    """Process log.txt content"""
    global last_processed_content

    if not os.path.exists(LOG_FILE):
        return

    try:
        with open(LOG_FILE, "r") as f:
            content = f.read().strip()

        # Avoid reprocessing same content
        if not content or content == last_processed_content:
            return

        last_processed_content = content

        print("\n" + "="*60)
        print(f"[LOG] New error detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print(f"Content:\n{content}\n")

        # Analyze error
        analysis = analyze_error(content)

        print("[ANALYSIS]")
        print(analysis)
        print("="*60 + "\n")

        # Save to memory
        memory = load_memory()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error": content,
            "analysis": analysis,
        }
        memory.append(entry)
        save_memory(memory)

        print(f"[*] Saved to {MEMORY_FILE}")

    except Exception as e:
        print(f"[ERROR] Failed to process log: {str(e)}")


class LogWatcher(FileSystemEventHandler):
    """Watch for changes in log.txt"""

    def on_modified(self, event):
        if event.src_path.endswith(LOG_FILE):
            time.sleep(0.5)  # Wait for file write to complete
            process_log()


def main():
    """Main function - start watching log.txt"""
    print(f"[*] Starting local-ai-agent")
    print(f"[*] Watching: {LOG_FILE}")
    print(f"[*] Ollama Model: {OLLAMA_MODEL}")
    print(f"[*] Memory file: {MEMORY_FILE}")
    print(f"[*] Press Ctrl+C to stop\n")

    # Setup file watcher
    observer = Observer()
    event_handler = LogWatcher()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[*] Stopping agent...")
    observer.join()


if __name__ == "__main__":
    main()
