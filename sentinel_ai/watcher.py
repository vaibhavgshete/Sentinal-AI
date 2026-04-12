import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class LogWatcher(FileSystemEventHandler):
    """Watch the configured log file across modify/create/move events."""

    def __init__(self, watched_path: Path, callback):
        self.watched_path = watched_path.resolve()
        self.callback = callback

    def _matches_log_file(self, event: FileSystemEvent):
        candidate_paths = []
        for attr in ("src_path", "dest_path"):
            value = getattr(event, attr, None)
            if value:
                try:
                    candidate_paths.append(Path(value).resolve())
                except OSError:
                    pass
        return any(path == self.watched_path for path in candidate_paths)

    def on_modified(self, event):
        if not event.is_directory and self._matches_log_file(event):
            time.sleep(0.2)
            self.callback()

    def on_created(self, event):
        if not event.is_directory and self._matches_log_file(event):
            time.sleep(0.2)
            self.callback()

    def on_moved(self, event):
        if not event.is_directory and self._matches_log_file(event):
            time.sleep(0.2)
            self.callback()


def run_watch_loop(log_file: Path, callback):
    """Start the observer and run until interrupted."""
    observer = Observer()
    event_handler = LogWatcher(log_file, callback)
    watch_dir = str(log_file.resolve().parent)
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[*] Stopping agent...")
    observer.join()
