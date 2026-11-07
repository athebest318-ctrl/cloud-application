import logging
import re
import time
from uuid import uuid4

from fastapi import FastAPI, Request

from app.request_context import request_id_var

logger = logging.getLogger(__name__)
VALID_ID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")


def register_request_logging(app: FastAPI, service_name: str) -> None:
    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        supplied = request.headers.get("X-Request-ID", "")
        request_id = supplied if VALID_ID.fullmatch(supplied) else uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            route = request.scope.get("route")
            logger.info(
                "HTTP request completed",
                extra={
                    "service": service_name,
                    "event": "http_request_completed",
                    "method": request.method,
                    "path": getattr(route, "path", "<unmatched>"),
                    "status_code": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            route = request.scope.get("route")
            logger.error(
                "Unhandled request exception",
                extra={
                    "service": service_name,
                    "event": "http_request_failed",
                    "method": request.method,
                    "path": getattr(route, "path", "<unmatched>"),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "error_type": type(exc).__name__,
                },
            )
            raise
        finally:
            request_id_var.reset(token)
