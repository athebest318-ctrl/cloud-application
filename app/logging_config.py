import json
import logging
import logging.config
from datetime import datetime, timezone

from app.request_context import get_request_id

EXTRA_FIELDS = (
    "service",
    "event",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "user_id",
    "username",
    "permission",
    "target_service",
    "attempt",
    "error_type",
    "notification_id",
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        payload.update(
            {
                field: getattr(record, field)
                for field in EXTRA_FIELDS
                if getattr(record, field, None) is not None
            }
        )
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"level": level.upper(), "handlers": ["console"]},
            "loggers": {
                "httpx": {"level": "WARNING"},
                "httpcore": {"level": "WARNING"},
                "uvicorn.access": {"handlers": [], "propagate": False},
            },
        }
    )
