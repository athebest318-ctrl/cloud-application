import asyncio
import logging
import time

import httpx

from app.config import settings
from app.request_context import get_request_id

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    pass


class NotificationServiceUnavailable(NotificationServiceError):
    pass


class NotificationServiceTimeout(NotificationServiceError):
    pass


class NotificationServiceBadResponse(NotificationServiceError):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"Notification service returned HTTP {status_code}")


async def send_notification(recipient: str, message: str) -> dict:
    url = f"{settings.notification_service_url.rstrip('/')}/notifications"
    payload = {"recipient": recipient, "message": message}
    timeout = httpx.Timeout(settings.notification_timeout_seconds)
    max_attempts = settings.notification_max_attempts

    fields = {"service": "cloud-application", "target_service": "notification"}
    logger.info(
        "Notification request started",
        extra={**fields, "event": "notification_request_started"},
    )
    for attempt in range(1, max_attempts + 1):
        logger.debug(
            "Notification request attempt",
            extra={
                **fields,
                "event": "notification_request_attempt",
                "attempt": attempt,
            },
        )
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url, json=payload, headers={"X-Request-ID": get_request_id()}
                )
                response.raise_for_status()
                logger.info(
                    "Notification request completed",
                    extra={
                        **fields,
                        "event": "notification_request_completed",
                        "attempt": attempt,
                        "status_code": response.status_code,
                        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    },
                )
                return response.json()
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            if attempt == max_attempts:
                logger.error(
                    "Notification service unavailable",
                    extra={
                        **fields,
                        "event": "notification_service_unavailable",
                        "attempt": attempt,
                        "error_type": type(exc).__name__,
                    },
                )
                raise NotificationServiceUnavailable() from exc
            logger.warning(
                "Notification request retry",
                extra={
                    **fields,
                    "event": "notification_request_retry",
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                },
            )
            delay = settings.notification_retry_delay_seconds * (2 ** (attempt - 1))
            await asyncio.sleep(delay)
        except httpx.TimeoutException as exc:
            logger.error(
                "Notification service timeout",
                extra={
                    **fields,
                    "event": "notification_service_timeout",
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                },
            )
            raise NotificationServiceTimeout() from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Notification service returned error",
                extra={
                    **fields,
                    "event": "notification_service_bad_response",
                    "attempt": attempt,
                    "status_code": exc.response.status_code,
                    "error_type": type(exc).__name__,
                },
            )
            raise NotificationServiceBadResponse(exc.response.status_code) from exc
        except httpx.RequestError as exc:
            logger.error(
                "Notification service unavailable",
                extra={
                    **fields,
                    "event": "notification_service_unavailable",
                    "attempt": attempt,
                    "error_type": type(exc).__name__,
                },
            )
            raise NotificationServiceUnavailable() from exc

    raise NotificationServiceUnavailable()


async def get_notification(notification_id: int) -> dict:
    url = f"{settings.notification_service_url.rstrip('/')}/notifications/{notification_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()
