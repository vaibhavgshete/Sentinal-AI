import argparse
from pathlib import Path

from .app import APP_NAME, LogProcessor
from .config import Settings
from .memory import load_memory
from .ollama_client import ask_llm
from .watcher import run_watch_loop


def build_parser():
    parser = argparse.ArgumentParser(prog="sentinel-ai", description="Local AI log watcher and analyzer.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    watch_parser = subparsers.add_parser("watch", help="Watch a log file for new errors.")
    _add_common_options(watch_parser)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single error message.")
    analyze_parser.add_argument("error", help="The error text to analyze.")
    analyze_parser.add_argument("--model", default="gemma3:4b", help="Ollama model to use.")
    analyze_parser.add_argument("--api-url", default="http://localhost:11434/api/generate", help="Ollama API URL.")

    memory_parser = subparsers.add_parser("memory", help="Inspect cached analyses.")
    memory_parser.add_argument(
        "action",
        choices=["list"],
        help="Memory action to perform.",
    )
    memory_parser.add_argument("--memory-file", default="memory.json", help="Path to the memory JSON file.")

    return parser


def _add_common_options(parser):
    parser.add_argument("--log", default="log.txt", help="Path to the log file to watch.")
    parser.add_argument("--memory-file", default="memory.json", help="Path to the memory JSON file.")
    parser.add_argument("--model", default="gemma3:4b", help="Ollama model to use.")
    parser.add_argument("--api-url", default="http://localhost:11434/api/generate", help="Ollama API URL.")


def settings_from_args(args):
    return Settings(
        log_file=Path(args.log),
        memory_file=Path(args.memory_file),
        ollama_model=args.model,
        ollama_api_url=args.api_url,
    )


def run_watch(args):
    settings = settings_from_args(args)
    processor = LogProcessor(settings)
    processor.prime_state()

    print(f"[*] Starting {APP_NAME}")
    print(f"[*] Watching: {settings.log_file}")
    print(f"[*] Ollama Model: {settings.ollama_model}")
    print(f"[*] Memory file: {settings.memory_file}")
    print("[*] Matching mode: normalized exact match")
    print("[*] Log mode: incremental reads (new content only)")
    print("[*] Press Ctrl+C to stop\n")

    run_watch_loop(settings.log_file, processor.process_log)


def run_analyze(args):
    response = ask_llm(args.error, model=args.model, api_url=args.api_url)
    print(response)


def run_memory_list(args):
    entries = load_memory(Path(args.memory_file))
    if not entries:
        print("No memory entries found.")
        return

    for index, entry in enumerate(entries, start=1):
        print(f"{index}. {entry['error']}")
        print(f"   Timestamp: {entry.get('timestamp')}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "watch":
        run_watch(args)
    elif args.command == "analyze":
        run_analyze(args)
    elif args.command == "memory" and args.action == "list":
        run_memory_list(args)


if __name__ == "__main__":
    main()
