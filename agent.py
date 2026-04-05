import json
import os
import time
from datetime import datetime

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Configuration
LOG_FILE = "log.txt"
MEMORY_FILE = "memory.json"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

# Track last processed content to avoid processing same log twice
last_processed_content = ""


def load_memory():
    """Load memory from JSON file - returns list of entries"""
    if not os.path.exists(MEMORY_FILE):
        return []
    
    try:
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            # Handle both array format and newline-delimited format
            if content.startswith("["):
                return json.loads(content)
            else:
                # Newline-delimited JSON
                return [json.loads(line) for line in content.split("\n") if line.strip()]
    except Exception as e:
        print(f"[!] Error loading memory: {e}")
        return []


def save_memory_entry(error, response):
    """Save error + response to memory.json"""
    try:
        memory = load_memory()
        entry = {
            "error": error,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }
        memory.append(entry)
        
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
        
        return True
    except Exception as e:
        print(f"[!] Error saving to memory: {e}")
        return False


def find_similar_error(error_content):
    """Check if similar error exists in memory (exact match)"""
    memory = load_memory()
    
    for entry in memory:
        if entry.get("error", "").strip() == error_content.strip():
            return entry.get("response", "")
    
    return None


def ask_llm(error_content):
    """Send error to Ollama and get analysis"""
    print("[*] Calling Ollama...")
    
    prompt = f"""You are a helpful debugging assistant. Analyze the following error/log:

{error_content}

Provide your response in exactly this format:
ROOT CAUSE: [explain the root cause]

FIX: [explain how to fix it]

SHELL COMMAND: [provide a shell command to fix it, or "N/A" if not applicable]"""

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
        error_msg = "[ERROR] Ollama not available. Make sure 'ollama serve' is running"
        print(f"[!] {error_msg}")
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "[ERROR] Ollama request timed out"
        print(f"[!] {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"[ERROR] Failed to query Ollama: {str(e)}"
        print(f"[!] {error_msg}")
        return error_msg


def process_log():
    """Process log.txt content with memory checking"""
    global last_processed_content

    if not os.path.exists(LOG_FILE):
        return

    try:
        with open(LOG_FILE, "r") as f:
            content = f.read().strip()

        # Skip if empty or same as last processed
        if not content or content == last_processed_content:
            return

        last_processed_content = content

        # Print header
        print("\n" + "="*70)
        print(f"[CHANGE DETECTED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print(f"Error Content:\n{content}\n")

        # Check memory first
        print("[*] Checking memory...")
        cached_response = find_similar_error(content)
        
        if cached_response:
            print("[✓] Found in memory! (Reusing previous analysis)\n")
            print("[ANALYSIS]")
            print(cached_response)
            print("="*70 + "\n")
            return

        # Not in memory - call LLM
        print("[*] Not in memory, calling LLM...")
        response = ask_llm(content)

        # Print analysis
        print("\n[ANALYSIS]")
        print(response)
        print("="*70 + "\n")

        # Save to memory
        print("[*] Saving to memory...")
        if save_memory_entry(content, response):
            print(f"[✓] Saved to {MEMORY_FILE}")
        else:
            print(f"[!] Failed to save to {MEMORY_FILE}")

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
