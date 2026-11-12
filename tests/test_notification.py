import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.integrations import notification_client
from app.integrations.notification_client import (
    NotificationServiceBadResponse,
    NotificationServiceTimeout,
    NotificationServiceUnavailable,
)
from app.notification_service.main import app as notification_app, notifications
from app.security.authorization import get_current_user


def test_notification_service_contract():
    notifications.clear()
    with TestClient(notification_app) as client:
        assert client.get('/status').json() == {'service': 'notification', 'status': 'running'}
        result = client.post('/notifications', json={'recipient': 'a@b', 'message': 'hello'})
        assert result.status_code == 201
        assert result.json() == {'id': 1, 'recipient': 'a@b', 'message': 'hello', 'status': 'accepted'}
        assert client.get('/notifications/1').json() == result.json()
        assert client.get('/notifications/2').status_code == 404
        assert client.post('/notifications', json={'recipient': 'x', 'message': ''}).status_code == 422
        assert client.get('/test/error/503').status_code == 503
        assert client.get('/test/error/400').status_code == 400


def test_integration_checks_permission_and_forwards_json(monkeypatch):
    notifications.clear()
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: original_client(transport=httpx.ASGITransport(app=notification_app), **kwargs))
    user = SimpleNamespace(role=SimpleNamespace(permissions=[]))
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        with TestClient(app) as client:
            payload = {'recipient': 'student@cloud.local', 'message': 'hello'}
            assert client.post('/integration/notifications', json=payload).status_code == 403
            assert notifications == []
            user.role.permissions = [SimpleNamespace(code='services.write')]
            result = client.post('/integration/notifications', json=payload, headers={"X-Request-ID": "lr31-correlation"})
            assert result.headers["X-Request-ID"] == "lr31-correlation"
            assert result.status_code == 200
            assert result.json() == {'id': 1, **payload, 'status': 'accepted'}
            assert notifications[0].message == 'hello'
    finally:
        app.dependency_overrides.clear()


def test_connect_errors_retry_with_backoff(monkeypatch):
    attempts = 0
    delays = []

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json, headers=None):
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise httpx.ConnectError("unavailable")
            return httpx.Response(
                201,
                request=httpx.Request("POST", url),
                json={"id": 1, **json, "status": "accepted"},
            )

    async def fake_sleep(delay):
        delays.append(delay)

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    result = asyncio.run(notification_client.send_notification("a@b", "hello"))

    assert result["status"] == "accepted"
    assert attempts == 3
    assert delays == [0.5, 1.0]


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (NotificationServiceUnavailable(), 503),
        (NotificationServiceTimeout(), 504),
        (NotificationServiceBadResponse(503), 502),
    ],
)
def test_integration_maps_service_errors(monkeypatch, error, expected_status):
    async def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr("app.routers.integration.send_notification", fail)
    user = SimpleNamespace(
        role=SimpleNamespace(permissions=[SimpleNamespace(code="services.write")])
    )
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        with TestClient(app) as client:
            response = client.post(
                "/integration/notifications",
                json={"recipient": "a@b", "message": "hello"},
            )
            assert response.status_code == expected_status
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("failure", ["timeout", "bad_response"])
def test_non_connect_failures_are_not_retried(monkeypatch, failure):
    attempts = []

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json, headers=None):
            attempts.append(headers)
            if failure == "timeout":
                raise httpx.ReadTimeout("test")
            return httpx.Response(503, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
    expected = NotificationServiceTimeout if failure == "timeout" else NotificationServiceBadResponse
    with pytest.raises(expected):
        asyncio.run(notification_client.send_notification("a@b", "message"))
    assert len(attempts) == 1
