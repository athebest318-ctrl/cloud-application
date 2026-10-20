import argparse
import json
from pathlib import Path
import sys

import httpx
from sqlalchemy import select


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.database import SessionLocal
from app.data.models import ServiceType, User
from app.schemas.auth import UserRegister
from app.services.access import assign_role, initialize_access_model
from app.services.auth import register_user


PASSWORD = "cloud12345"
USERS = {
    "student01": "viewer",
    "student02": "operator",
    "student03": "administrator",
    "student04": "content_manager",
}


def prepare_database() -> None:
    with SessionLocal() as db:
        initialize_access_model(db)
        if db.scalar(select(ServiceType).where(ServiceType.name == "monitoring")) is None:
            db.add(ServiceType(name="monitoring", description="Monitoring services"))
            db.commit()

        for username, role_name in USERS.items():
            user = db.scalar(select(User).where(User.username == username))
            if user is None:
                user = register_user(
                    db,
                    UserRegister(username=username, password=PASSWORD),
                )
            assert user is not None
            user.password = PASSWORD
            db.commit()
            assign_role(db, user.id, role_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify laboratory work 21")
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    prepare_database()

    results: list[dict[str, object]] = []

    def record(label: str, response: httpx.Response, expected: int) -> None:
        results.append(
            {
                "check": label,
                "expected": expected,
                "actual": response.status_code,
                "passed": response.status_code == expected,
            }
        )
        if response.status_code != expected:
            raise RuntimeError(
                f"{label}: expected {expected}, got {response.status_code}: "
                f"{response.text}"
            )

    def bearer(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        record("No token", client.get("/services"), 401)
        record(
            "Incorrect token",
            client.get("/services", headers=bearer("incorrect-token")),
            401,
        )

        tokens: dict[str, str] = {}
        user_ids: dict[str, int] = {}
        for username, role_name in USERS.items():
            login = client.post(
                "/auth/login",
                json={"username": username, "password": PASSWORD},
            )
            record(f"Login {username}", login, 200)
            token = login.json()["access_token"]
            tokens[username] = token
            me = client.get("/auth/me", headers=bearer(token))
            record(f"Current user {username}", me, 200)
            if me.json()["role"] != role_name:
                raise RuntimeError(f"Unexpected role for {username}: {me.json()}")
            user_ids[username] = me.json()["id"]

        viewer = bearer(tokens["student01"])
        operator = bearer(tokens["student02"])
        admin = bearer(tokens["student03"])
        content_manager = bearer(tokens["student04"])
        payload = {
            "name": "Authorization demo service",
            "type": "monitoring",
            "status": "running",
            "description": "Created by laboratory work 21 verification",
        }

        record("Viewer reads services", client.get("/services", headers=viewer), 200)
        record("Viewer cannot create service", client.post("/services", headers=viewer, json=payload), 403)
        record("Viewer cannot list roles", client.get("/access/roles", headers=viewer), 403)

        created = client.post("/services", headers=operator, json=payload)
        record("Operator creates service", created, 201)
        service_id = created.json()["id"]
        record("Operator cannot list roles", client.get("/access/roles", headers=operator), 403)

        record("Administrator lists roles", client.get("/access/roles", headers=admin), 200)
        record(
            "Administrator reads user access",
            client.get(f"/access/users/{user_ids['student01']}", headers=admin),
            200,
        )
        record("Administrator reads access summary", client.get("/access/summary", headers=admin), 200)

        record("Content manager reads services", client.get("/services", headers=content_manager), 200)
        record("Content manager cannot create service", client.post("/services", headers=content_manager, json=payload), 403)
        uploaded = client.post(
            "/objects",
            headers=content_manager,
            files={"file": ("authorization-demo.txt", b"authorized", "text/plain")},
        )
        record("Content manager uploads object", uploaded, 201)
        object_id = uploaded.json()["id"]
        record(
            "Content manager cannot assign role",
            client.put(
                f"/access/users/{user_ids['student01']}/role",
                headers=content_manager,
                json={"role_name": "operator"},
            ),
            403,
        )

        promoted = client.put(
            f"/access/users/{user_ids['student01']}/role",
            headers=admin,
            json={"role_name": "operator"},
        )
        record("Administrator promotes viewer", promoted, 200)
        promoted_create = client.post("/services", headers=viewer, json=payload)
        record("Same token works after promotion", promoted_create, 201)
        promoted_service_id = promoted_create.json()["id"]
        record(
            "Administrator restores viewer role",
            client.put(
                f"/access/users/{user_ids['student01']}/role",
                headers=admin,
                json={"role_name": "viewer"},
            ),
            200,
        )

        record(
            "Content manager deletes object",
            client.delete(f"/objects/{object_id}", headers=content_manager),
            200,
        )
        record(
            "Operator deletes service",
            client.delete(f"/services/{service_id}", headers=operator),
            200,
        )
        record(
            "Operator deletes promoted service",
            client.delete(f"/services/{promoted_service_id}", headers=operator),
            200,
        )

        record(
            "Close viewer session",
            client.delete(f"/auth/session/{tokens['student01']}"),
            200,
        )
        record("Revoked token", client.get("/auth/me", headers=viewer), 401)

    evidence_path = Path(__file__).resolve().parents[1] / "evidence" / "authorization_results.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(
            {
                "base_url": base_url,
                "checks": len(results),
                "passed": sum(bool(item["passed"]) for item in results),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"{len(results)} authorization checks passed")
    print(f"Evidence: {evidence_path}")


if __name__ == "__main__":
    main()
