from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx
import psycopg


PROJECT_PATH = Path(__file__).resolve().parents[1]
if str(PROJECT_PATH) not in sys.path:
    sys.path.insert(0, str(PROJECT_PATH))

from app.config import PROJECT_ROOT, settings


BASE_URL = f"http://{settings.app_host}:{settings.app_port}"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        result = {key: redact(item) for key, item in value.items()}
        token = result.get("access_token")
        if isinstance(token, str):
            result["access_token"] = f"{token[:8]}...{token[-4:]}"
        return result
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def response_record(response: httpx.Response) -> dict[str, Any]:
    try:
        body: Any = response.json()
    except ValueError:
        body = f"{len(response.content)} bytes"
    return {
        "method": response.request.method,
        "url": str(response.request.url),
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "body": redact(body),
    }


def require(response: httpx.Response, *codes: int) -> httpx.Response:
    if response.status_code not in codes:
        raise RuntimeError(
            f"{response.request.method} {response.request.url} returned "
            f"{response.status_code}: {response.text}"
        )
    return response


def database_evidence() -> dict[str, Any]:
    url = settings.database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    queries = {
        "tables": (
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' ORDER BY table_name"
        ),
        "service_constraints": (
            "SELECT conname, contype FROM pg_constraint "
            "WHERE conrelid='services'::regclass ORDER BY conname"
        ),
        "type_constraints": (
            "SELECT conname, contype FROM pg_constraint "
            "WHERE conrelid='service_types'::regclass ORDER BY conname"
        ),
        "counts": (
            "SELECT "
            "(SELECT count(*) FROM services), "
            "(SELECT count(*) FROM stored_objects), "
            "(SELECT count(*) FROM users), "
            "(SELECT count(*) FROM auth_sessions)"
        ),
        "alembic": "SELECT version_num FROM alembic_version",
    }
    result: dict[str, Any] = {}
    with psycopg.connect(url) as connection:
        with connection.cursor() as cursor:
            for name, query in queries.items():
                cursor.execute(query)
                result[name] = cursor.fetchall()
    return result


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    tokens: dict[str, str] = {}

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for path in ["/", "/status", "/about", "/course", "/services", "/docs"]:
            response = require(client.get(path), 200)
            records.append(response_record(response))

        records.append(response_record(require(client.get("/services?status=running"), 200)))
        records.append(response_record(require(client.get("/services?status=unknown"), 422)))

        service_payload = {
            "name": "Monitoring API",
            "type": "monitoring",
            "status": "running",
            "description": "Integration check for laboratory work 15",
        }
        created = require(client.post("/services", json=service_payload), 201)
        records.append(response_record(created))
        service_id = created.json()["id"]
        records.append(response_record(require(client.get(f"/services/{service_id}"), 200)))
        service_payload["status"] = "maintenance"
        records.append(
            response_record(require(client.put(f"/services/{service_id}", json=service_payload), 200))
        )
        records.append(response_record(require(client.delete(f"/services/{service_id}"), 200)))
        records.append(response_record(require(client.get(f"/services/{service_id}"), 404)))

        sample_paths = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "LR 8.docx",
            PROJECT_ROOT / "app.zip",
        ]
        object_ids: list[int] = []
        for sample in sample_paths:
            with sample.open("rb") as source:
                response = require(
                    client.post(
                        "/objects",
                        files={"file": (sample.name, source, "application/octet-stream")},
                    ),
                    201,
                )
            records.append(response_record(response))
            object_ids.append(response.json()["id"])
        records.append(response_record(require(client.get("/objects"), 200)))
        records.append(
            response_record(require(client.get(f"/objects/{object_ids[0]}/download"), 200))
        )
        records.append(response_record(require(client.delete(f"/objects/{object_ids[-1]}"), 200)))

        too_large = b"x" * (settings.max_upload_size + 1)
        records.append(
            response_record(
                require(
                    client.post(
                        "/objects",
                        files={"file": ("too-large.bin", too_large, "application/octet-stream")},
                    ),
                    413,
                )
            )
        )

        for username in ["student01", "student02", "student03"]:
            payload = {"username": username, "password": "cloud12345"}
            registration = client.post("/auth/register", json=payload)
            require(registration, 201, 409)
            records.append(response_record(registration))
            login = require(client.post("/auth/login", json=payload), 200)
            records.append(response_record(login))
            tokens[username] = login.json()["access_token"]
            records.append(
                response_record(require(client.get(f"/auth/session/{tokens[username]}"), 200))
            )

        for _ in range(2):
            extra_login = require(
                client.post(
                    "/auth/login",
                    json={"username": "student01", "password": "cloud12345"},
                ),
                200,
            )
            records.append(response_record(extra_login))

        records.append(
            response_record(
                require(
                    client.post(
                        "/auth/login",
                        json={"username": "student01", "password": "wrongpassword"},
                    ),
                    401,
                )
            )
        )
        records.append(
            response_record(
                require(
                    client.post(
                        "/auth/login",
                        json={"username": "unknown", "password": "cloud12345"},
                    ),
                    401,
                )
            )
        )
        records.append(response_record(require(client.delete(f"/auth/session/{tokens['student03']}"), 200)))
        records.append(response_record(require(client.get(f"/auth/session/{tokens['student03']}"), 401)))

    database = database_evidence()
    (EVIDENCE_DIR / "api_results.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "database_results.json").write_text(
        json.dumps(database, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "checks": len(records),
                "database": database,
                "evidence": str(EVIDENCE_DIR),
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
