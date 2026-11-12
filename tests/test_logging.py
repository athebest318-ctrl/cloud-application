import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.logging_config import JsonFormatter
from app.middleware.request_logging import register_request_logging
from app.request_context import get_request_id


def test_request_id_and_sensitive_path_are_safe(caplog):
    app = FastAPI()
    register_request_logging(app, "test")

    @app.get("/sessions/{token}")
    def endpoint(token: str):
        return {"ok": True}

    with caplog.at_level(logging.INFO, logger="app.middleware.request_logging"):
        response = TestClient(app).get("/sessions/private-token?password=hidden", headers={"X-Request-ID": "request-123"})
    assert response.headers["X-Request-ID"] == "request-123"
    record = next(r for r in caplog.records if getattr(r, "event", None) == "http_request_completed")
    assert record.path == "/sessions/{token}"
    assert "private-token" not in record.path
    assert get_request_id() == "-"


def test_invalid_request_id_is_replaced():
    app = FastAPI()
    register_request_logging(app, "test")

    @app.get("/")
    def endpoint():
        return {}

    response = TestClient(app).get("/", headers={"X-Request-ID": "unsafe value"})
    assert response.headers["X-Request-ID"] != "unsafe value"
    assert len(response.headers["X-Request-ID"]) == 32


def test_formatter_outputs_json():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "message", (), None)
    record.event = "sample"
    payload = json.loads(JsonFormatter().format(record))
    assert payload["event"] == "sample"
    assert payload["request_id"] == "-"
    assert payload["level"] == "INFO"
