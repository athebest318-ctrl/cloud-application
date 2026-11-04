import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.integrations import notification_client as integration
from app.main import app
from app.security.authorization import get_current_user


@pytest.mark.parametrize('error,expected,attempts,delays', [
    (httpx.ConnectError, integration.NotificationServiceUnavailable, 3, [0.5, 1.0]),
    (httpx.ConnectTimeout, integration.NotificationServiceUnavailable, 3, [0.5, 1.0]),
    (httpx.ReadTimeout, integration.NotificationServiceTimeout, 1, []),
    (httpx.WriteTimeout, integration.NotificationServiceTimeout, 1, []),
    (httpx.PoolTimeout, integration.NotificationServiceTimeout, 1, []),
    (httpx.ReadError, integration.NotificationServiceUnavailable, 1, []),
])
def test_transport_policy(monkeypatch, error, expected, attempts, delays):
    calls = []
    original = httpx.AsyncClient
    def handler(request):
        calls.append(request)
        assert request.extensions['timeout'] == dict.fromkeys(['connect', 'read', 'write', 'pool'], 2.0)
        raise error('controlled failure', request=request)
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(handler), **kw))
    sleep = AsyncMock()
    monkeypatch.setattr(integration.asyncio, 'sleep', sleep)
    with pytest.raises(expected):
        asyncio.run(integration.send_notification('a@b', 'hello'))
    assert len(calls) == attempts
    assert [call.args[0] for call in sleep.call_args_list] == delays


@pytest.mark.parametrize('code', [400, 503])
def test_http_error_is_not_retried(monkeypatch, code):
    original = httpx.AsyncClient
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(code, json={'detail': 'private upstream detail'})
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(handler), **kw))
    with pytest.raises(integration.NotificationServiceBadResponse) as caught:
        asyncio.run(integration.send_notification('a@b', 'hello'))
    assert caught.value.status_code == code
    assert len(calls) == 1


def test_retry_recovers(monkeypatch):
    original = httpx.AsyncClient
    calls = []
    def handler(request):
        calls.append(request)
        if len(calls) < 3:
            raise httpx.ConnectError('starting', request=request)
        return httpx.Response(201, json={'status': 'accepted'})
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(transport=httpx.MockTransport(handler), **kw))
    monkeypatch.setattr(integration.asyncio, 'sleep', AsyncMock())
    assert asyncio.run(integration.send_notification('a@b', 'hello')) == {'status': 'accepted'}
    assert len(calls) == 3
    assert len({r.content for r in calls}) == 1


@pytest.mark.parametrize('error,code,detail', [
    (integration.NotificationServiceUnavailable(), 503, 'Notification service is unavailable'),
    (integration.NotificationServiceTimeout(), 504, 'Notification service response timeout'),
    (integration.NotificationServiceBadResponse(400), 502, 'Notification service returned an invalid response'),
])
def test_public_error_and_authorization(monkeypatch, error, code, detail):
    from app.routers import integration as router
    send = AsyncMock(side_effect=error)
    monkeypatch.setattr(router, 'send_notification', send)
    user = SimpleNamespace(role=SimpleNamespace(permissions=[]))
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        with TestClient(app) as client:
            payload = {'recipient': 'a@b', 'message': 'hello'}
            assert client.post('/integration/notifications', json=payload).status_code == 403
            send.assert_not_awaited()
            user.role.permissions = [SimpleNamespace(code='services.write')]
            result = client.post('/integration/notifications', json=payload)
            assert result.status_code == code
            assert result.json() == {'detail': detail}
    finally:
        app.dependency_overrides.clear()
