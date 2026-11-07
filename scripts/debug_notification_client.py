"""Reproduce retry exhaustion against a local, unavailable endpoint."""

import argparse
import asyncio
import os
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts must be positive")
    with socket.socket() as probe:
        probe.settimeout(0.2)
        if probe.connect_ex(("127.0.0.1", 9999)) == 0:
            raise RuntimeError("Port 9999 is in use; choose a free test endpoint")
    os.environ.update(
        {
            "NOTIFICATION_SERVICE_URL": "http://127.0.0.1:9999",
            "NOTIFICATION_TIMEOUT_SECONDS": "0.5",
            "NOTIFICATION_MAX_ATTEMPTS": str(args.attempts),
            "NOTIFICATION_RETRY_DELAY_SECONDS": "0.1",
            "LOG_LEVEL": "DEBUG",
        }
    )
    from app.config import settings
    from app.integrations.notification_client import (
        NotificationServiceUnavailable,
        send_notification,
    )
    from app.logging_config import configure_logging

    configure_logging(settings.log_level)
    print(f"Configured max attempts: {settings.notification_max_attempts}")
    try:
        asyncio.run(send_notification("debug@cloud.local", "LR32 debug"))
    except NotificationServiceUnavailable:
        print("EXPECTED_RESULT: service unavailable")
    else:
        raise RuntimeError("Unexpected success")


if __name__ == "__main__":
    main()
