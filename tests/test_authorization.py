from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.data.database import Base, get_db
from app.data.models import ServiceType
from app.main import app
from app.schemas.access import RoleAssign
from app.schemas.auth import UserRegister
from app.services.access import assign_role, initialize_access_model
from app.services.auth import register_user


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with TestingSession() as db:
        initialize_access_model(db)
        db.add(ServiceType(name="monitoring", description="Monitoring"))
        db.commit()
        for username, role_name in (
            ("student01", "viewer"),
            ("student02", "operator"),
            ("student03", "administrator"),
            ("student04", "content_manager"),
        ):
            user = register_user(
                db,
                UserRegister(username=username, password="cloud12345"),
            )
            assert user is not None
            assign_role(db, user.id, role_name)

    def override_get_db() -> Generator[Session]:
        with TestingSession() as db:
            yield db

    monkeypatch.setattr(settings, "storage_path", str(tmp_path / "objects"))
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def login(client: TestClient, username: str) -> str:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": "cloud12345"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def service_payload(name: str) -> dict[str, str]:
    return {
        "name": name,
        "type": "monitoring",
        "status": "running",
        "description": "Authorization test",
    }


def test_missing_and_invalid_tokens_return_401(client: TestClient) -> None:
    missing = client.get("/services")
    invalid = client.get("/services", headers=auth("incorrect-token"))

    assert missing.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"
    assert invalid.status_code == 401


def test_viewer_can_read_but_cannot_write_or_administer(client: TestClient) -> None:
    token = login(client, "student01")

    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["role"] == "viewer"
    assert client.get("/services", headers=auth(token)).status_code == 200
    assert (
        client.post(
            "/services",
            headers=auth(token),
            json=service_payload("Viewer service"),
        ).status_code
        == 403
    )
    assert client.get("/objects", headers=auth(token)).status_code == 200
    assert client.get("/access/roles", headers=auth(token)).status_code == 403


def test_operator_can_write_services_and_objects_but_not_access_model(
    client: TestClient,
) -> None:
    token = login(client, "student02")
    created = client.post(
        "/services",
        headers=auth(token),
        json=service_payload("Operator service"),
    )
    uploaded = client.post(
        "/objects",
        headers=auth(token),
        files={"file": ("evidence.txt", b"authorized", "text/plain")},
    )

    assert created.status_code == 201
    assert uploaded.status_code == 201
    assert client.get("/access/roles", headers=auth(token)).status_code == 403
    assert (
        client.delete(
            f"/objects/{uploaded.json()['id']}",
            headers=auth(token),
        ).status_code
        == 200
    )


def test_administrator_changes_access_without_reissuing_token(
    client: TestClient,
) -> None:
    viewer_token = login(client, "student01")
    admin_token = login(client, "student03")
    viewer_id = client.get("/auth/me", headers=auth(viewer_token)).json()["id"]

    denied = client.post(
        "/services",
        headers=auth(viewer_token),
        json=service_payload("Before promotion"),
    )
    changed = client.put(
        f"/access/users/{viewer_id}/role",
        headers=auth(admin_token),
        json=RoleAssign(role_name="operator").model_dump(),
    )
    allowed = client.post(
        "/services",
        headers=auth(viewer_token),
        json=service_payload("After promotion"),
    )

    assert denied.status_code == 403
    assert changed.status_code == 200
    assert changed.json()["role"] == "operator"
    assert allowed.status_code == 201
    assert client.get("/access/summary", headers=auth(admin_token)).status_code == 200


def test_content_manager_and_revoked_session(client: TestClient) -> None:
    token = login(client, "student04")

    assert client.get("/services", headers=auth(token)).status_code == 200
    assert (
        client.post(
            "/services",
            headers=auth(token),
            json=service_payload("Forbidden service"),
        ).status_code
        == 403
    )
    uploaded = client.post(
        "/objects",
        headers=auth(token),
        files={"file": ("content.txt", b"content", "text/plain")},
    )
    assert uploaded.status_code == 201
    assert client.delete(f"/auth/session/{token}").status_code == 200
    assert client.get("/auth/me", headers=auth(token)).status_code == 401
