from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_and_status() -> None:
    root = client.get("/")
    status = client.get("/status")
    assert root.status_code == 200
    assert root.json()["status"] == "running"
    assert status.status_code == 200
    assert status.json()["environment"] in {"development", "testing", "production"}


def test_openapi_contains_final_routes() -> None:
    schema = client.get("/openapi.json").json()
    expected = {
        "/services",
        "/objects",
        "/auth/register",
        "/auth/login",
        "/auth/me",
        "/access/roles",
        "/access/summary",
        "/access/users/{user_id}",
        "/access/users/{user_id}/role",
        "/status",
    }
    assert expected.issubset(schema["paths"])
    assert "HTTPBearer" in schema["components"]["securitySchemes"]
