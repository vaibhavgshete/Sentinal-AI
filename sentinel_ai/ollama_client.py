import requests


def is_successful_analysis(response):
    """Avoid caching transport/runtime failures as valid memory entries."""
    return bool(response) and not response.startswith("[ERROR]")


def ask_llm(error_content, model, api_url):
    """Send error text to Ollama and return a structured analysis."""
    print("[*] Calling Ollama...")

    prompt = f"""You are a helpful debugging assistant. Analyze the following error/log:

{error_content}

Provide your response in exactly this format:
ROOT CAUSE: [explain the root cause]

FIX: [explain how to fix it]

SHELL COMMAND: [provide a shell command to fix it, or "N/A" if not applicable]"""

    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(api_url, json=payload, timeout=60)
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
    except Exception as exc:
        error_msg = f"[ERROR] Failed to query Ollama: {str(exc)}"
        print(f"[!] {error_msg}")
        return error_msg
