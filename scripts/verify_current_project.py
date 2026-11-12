"""Integration checks for an isolated test deployment (creates demo accounts)."""

import argparse
import json
import sys
from pathlib import Path

import httpx
from sqlalchemy import text

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.database import SessionLocal
from scripts.verify_authorization import PASSWORD, USERS, prepare_database


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=Path("evidence/lr34/smoke.json"))
    args = parser.parse_args()
    prepare_database()
    results = []

    def check(label, response, expected):
        results.append(
            {"check": label, "expected": expected, "actual": response.status_code}
        )
        assert response.status_code == expected, f"{label}: {response.status_code}"
        return response

    with httpx.Client(base_url=args.base_url, timeout=20) as client:
        for path in [
            "/",
            "/status",
            "/docs",
            "/about",
            "/course",
            "/connection",
            "/service-count",
        ]:
            check(path, client.get(path), 200)
        check("anonymous denied", client.get("/services"), 401)
        headers = {}
        tokens = {}
        for name, role in USERS.items():
            login = check(
                f"login {role}",
                client.post(
                    "/auth/login", json={"username": name, "password": PASSWORD}
                ),
                200,
            )
            tokens[role] = login.json()["access_token"]
            headers[role] = {"Authorization": f"Bearer {tokens[role]}"}
            me = check(
                f"identity {role}", client.get("/auth/me", headers=headers[role]), 200
            )
            assert me.json()["role"] == role
        check(
            "bad password",
            client.post(
                "/auth/login",
                json={"username": "student01", "password": "wrongpassword"},
            ),
            401,
        )
        payload = {
            "name": "LR34 smoke service",
            "type": "monitoring",
            "status": "running",
            "description": "Integration test",
        }
        check(
            "viewer cannot write",
            client.post("/services", headers=headers["viewer"], json=payload),
            403,
        )
        check(
            "operator cannot administer",
            client.get("/access/roles", headers=headers["operator"]),
            403,
        )
        check(
            "admin roles",
            client.get("/access/roles", headers=headers["administrator"]),
            200,
        )
        check(
            "admin summary",
            client.get("/access/summary", headers=headers["administrator"]),
            200,
        )
        operator = headers["operator"]
        created = check(
            "create service",
            client.post("/services", headers=operator, json=payload),
            201,
        ).json()
        path = f"/services/{created['id']}"
        check("read service", client.get(path, headers=operator), 200)
        payload["status"] = "maintenance"
        check("update service", client.put(path, headers=operator, json=payload), 200)
        filtered = check(
            "filter services",
            client.get("/services?status=maintenance", headers=operator),
            200,
        ).json()
        assert any(s["id"] == created["id"] for s in filtered)
        assert all(s["status"] == "maintenance" for s in filtered)
        check(
            "invalid status",
            client.get("/services?status=unknown", headers=operator),
            422,
        )
        check("delete service", client.delete(path, headers=operator), 200)
        check("deleted service absent", client.get(path, headers=operator), 404)
        content = b"LR34 roundtrip test"
        obj = check(
            "upload",
            client.post(
                "/objects",
                headers=headers["content_manager"],
                files={"file": ("lr34.txt", content, "text/plain")},
            ),
            201,
        ).json()
        download = check(
            "download",
            client.get(f"/objects/{obj['id']}/download", headers=headers["viewer"]),
            200,
        )
        assert download.content == content
        check(
            "delete object",
            client.delete(f"/objects/{obj['id']}", headers=operator),
            200,
        )
        check(
            "deleted object absent",
            client.get(f"/objects/{obj['id']}", headers=operator),
            404,
        )
        check(
            "upload limit",
            client.post(
                "/objects",
                headers=operator,
                files={"file": ("large.bin", b"x" * (5 * 1024 * 1024 + 1))},
            ),
            413,
        )
        notification = {"recipient": "lr34-demo", "message": "Integration test"}
        check(
            "viewer notification denied",
            client.post(
                "/integration/notifications",
                headers=headers["viewer"],
                json=notification,
            ),
            403,
        )
        check(
            "notification accepted",
            client.post(
                "/integration/notifications", headers=operator, json=notification
            ),
            201,
        )
        check("logout", client.delete(f"/auth/session/{tokens['viewer']}"), 200)
        check("revoked session", client.get("/auth/me", headers=headers["viewer"]), 401)
    with SessionLocal() as db:
        revision = db.scalar(text("SELECT version_num FROM alembic_version"))
        assert revision == "008_password_hash"
        assert (
            db.scalar(
                text(
                    "SELECT count(*) FROM users WHERE password_hash NOT LIKE '$argon2%'"
                )
            )
            == 0
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "checks": results,
                "migration": revision,
                "passwords": "argon2 hashes only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{len(results)} HTTP checks passed; migration {revision}; Argon2 verified")


if __name__ == "__main__":
    main()
