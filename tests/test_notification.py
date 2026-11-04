from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from app.main import app
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
            result = client.post('/integration/notifications', json=payload)
            assert result.status_code == 201
            assert result.json() == {'id': 1, **payload, 'status': 'accepted'}
            assert notifications[0].message == 'hello'
    finally:
        app.dependency_overrides.clear()
