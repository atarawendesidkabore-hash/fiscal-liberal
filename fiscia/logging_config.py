"""
Structured JSON logging with request correlation IDs for FiscIA Pro.
"""
import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

# Context variable for per-request correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


def get_correlation_id() -> str:
    return correlation_id_var.get()


def new_correlation_id() -> str:
    cid = str(uuid.uuid4())
    correlation_id_var.set(cid)
    return cid


class JSONFormatter(logging.Formatter):
    """Emits log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get(),
        }
        if record.name.startswith("fiscia"):
            log_entry["module"] = record.module
            log_entry["function"] = record.funcName
            log_entry["line"] = record.lineno
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Attach extra structured fields if present
        for key in ("method", "path", "status_code", "duration_ms", "client_ip", "siren", "user_id"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Configure root + fiscia loggers with JSON output to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy libraries
    for name in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.getLogger("fiscia").setLevel(getattr(logging, level.upper(), logging.INFO))
