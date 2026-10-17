from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select, text


PROJECT_PATH = Path(__file__).resolve().parents[1]
if str(PROJECT_PATH) not in sys.path:
    sys.path.insert(0, str(PROJECT_PATH))

from app.config import PROJECT_ROOT
from app.data.database import SessionLocal
from app.data.models import User
from app.services.access import get_roles, get_user_access
from app.services.auth import get_user_by_username


EXPECTED_PERMISSIONS = {
    "viewer": ["objects.read", "services.read"],
    "operator": [
        "objects.read",
        "objects.write",
        "services.read",
        "services.write",
    ],
    "administrator": [
        "objects.read",
        "objects.write",
        "roles.manage",
        "services.read",
        "services.write",
        "users.manage",
    ],
    "content_manager": ["objects.read", "objects.write", "services.read"],
}


def require(response: httpx.Response, *codes: int) -> httpx.Response:
    if response.status_code not in codes:
        raise RuntimeError(
            f"{response.request.method} {response.request.url} returned "
            f"{response.status_code}: {response.text}"
        )
    return response


def user_id(username: str) -> int:
    with SessionLocal() as db:
        user = get_user_by_username(db, username)
        if user is None:
            raise RuntimeError(f"User {username} was not created")
        return user.id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8010")
    args = parser.parse_args()

    records: list[dict[str, Any]] = []
    assignments = {
        "student01": "viewer",
        "student02": "operator",
        "student03": "administrator",
        "student04": "content_manager",
    }

    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        roles_response = require(client.get("/access/roles"), 200)
        roles = roles_response.json()
        role_permissions = {
            role["name"]: role["permissions"] for role in roles
        }
        if role_permissions != EXPECTED_PERMISSIONS:
            raise RuntimeError(f"Unexpected role model: {role_permissions}")
        records.append({"check": "roles", "status": 200, "body": roles})

        for username, role_name in assignments.items():
            credentials = {"username": username, "password": "cloud12345"}
            registration = client.post("/auth/register", json=credentials)
            require(registration, 201, 409)

            current_user_id = user_id(username)
            assignment = require(
                client.put(
                    f"/access/users/{current_user_id}/role",
                    json={"role_name": role_name},
                ),
                200,
            )
            access = require(
                client.get(f"/access/users/{current_user_id}"),
                200,
            )
            login = require(client.post("/auth/login", json=credentials), 200)

            if access.json()["permissions"] != EXPECTED_PERMISSIONS[role_name]:
                raise RuntimeError(f"Unexpected permissions for {username}")
            records.append(
                {
                    "check": username,
                    "role": role_name,
                    "assignment_status": assignment.status_code,
                    "access": access.json(),
                    "login_status": login.status_code,
                }
            )

        invalid = require(
            client.put(
                f"/access/users/{user_id('student01')}/role",
                json={"role_name": "superuser"},
            ),
            404,
        )
        records.append(
            {
                "check": "unknown role",
                "status": invalid.status_code,
                "body": invalid.json(),
            }
        )

        service = require(
            client.post(
                "/services",
                json={
                    "name": "Lab 20 Authorization Experiment",
                    "type": "application",
                    "status": "running",
                    "description": "Viewer request is not blocked in laboratory 20",
                },
            ),
            201,
        )
        service_id = service.json()["id"]
        require(client.delete(f"/services/{service_id}"), 200)
        records.append(
            {
                "check": "unprotected endpoint",
                "status": service.status_code,
                "result": "POST /services remains available before laboratory 21",
            }
        )

    with SessionLocal() as db:
        database = {
            "alembic_revision": db.scalar(
                text("SELECT version_num FROM alembic_version")
            ),
            "roles": [
                {
                    "name": role.name,
                    "permissions": sorted(
                        permission.code for permission in role.permissions
                    ),
                }
                for role in get_roles(db)
            ],
            "users": [
                get_user_access(db, user.id)
                for user in db.scalars(select(User).order_by(User.id)).all()
            ],
        }

    evidence_dir = Path(PROJECT_ROOT) / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    output = evidence_dir / "access_results.json"
    output.write_text(
        json.dumps(
            {"http_checks": records, "database": database},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "checks": len(records),
                "roles": list(assignments.values()),
                "alembic_revision": database["alembic_revision"],
                "evidence": str(output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
