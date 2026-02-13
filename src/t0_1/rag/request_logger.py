import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


def _safe_filename(thread_id: str) -> str:
    """Replace filesystem-unsafe characters with underscores."""
    return re.sub(r"[^\w\-]", "_", thread_id)


def write_log_entry(
    thread_id: str, log_entry: dict, log_dir: str | Path
) -> None:
    try:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{_safe_filename(thread_id)}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")
    except Exception:
        logger.warning(
            f"Failed to write log entry for thread {thread_id}", exc_info=True
        )


def logged_stream(
    generator: Iterable[str],
    request_data: dict,
    thread_id: str,
    log_dir: str | Path,
) -> Iterable[str]:
    """Wrap a streaming generator to log the full request/response on completion.

    Yields every chunk unchanged. After the stream ends (or errors), writes a
    JSONL log entry to ``{log_dir}/{thread_id}.jsonl``.
    """
    chunks: list[str] = []
    start_time = time.monotonic()
    error = None
    status_code = 200

    try:
        for chunk in generator:
            chunks.append(chunk)
            yield chunk
    except GeneratorExit:
        error = "client_disconnected"
    except Exception as e:
        error = str(e)
        status_code = 500
        raise
    finally:
        duration = time.monotonic() - start_time
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/query_stream",
            "method": "POST",
            "request": request_data,
            "response": {
                "body": "".join(chunks),
                "status_code": status_code,
            },
            "duration_seconds": round(duration, 3),
            "error": error,
        }
        write_log_entry(thread_id, log_entry, log_dir)
