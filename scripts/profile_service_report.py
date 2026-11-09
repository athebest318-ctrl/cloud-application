"""Measure the deterministic service-report scenario used in laboratory 34."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.reporting import build_service_report


def create_dataset(
    service_count: int,
    type_count: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Create stable input data without randomness."""
    service_types: list[dict[str, object]] = [
        {"id": type_id, "name": f"type-{type_id}"}
        for type_id in range(1, type_count + 1)
    ]
    statuses = ("running", "maintenance", "stopped")
    services: list[dict[str, object]] = [
        {
            "id": service_id,
            "name": f"service-{service_id}",
            "type_id": ((service_id * 37) % type_count) + 1,
            "status": statuses[service_id % len(statuses)],
        }
        for service_id in range(1, service_count + 1)
    ]
    return services, service_types


def result_digest(report: list[dict[str, object]]) -> str:
    """Return a stable digest for functional-equivalence checks."""
    payload = json.dumps(
        report,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def measure(service_count: int, type_count: int, repeats: int) -> dict[str, object]:
    """Measure the current implementation several times on one dataset."""
    services, service_types = create_dataset(service_count, type_count)
    times: list[float] = []
    last_report: list[dict[str, object]] = []

    for _ in range(repeats):
        started = time.perf_counter()
        last_report = build_service_report(services, service_types)
        times.append(time.perf_counter() - started)

    return {
        "service_count": service_count,
        "type_count": type_count,
        "repeats": repeats,
        "times": times,
        "mean": statistics.mean(times),
        "best": min(times),
        "records": len(last_report),
        "digest": result_digest(last_report),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-count", type=int, default=20_000)
    parser.add_argument("--type-count", type=int, default=200)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = measure(args.service_count, args.type_count, args.repeats)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return

    for run_number, elapsed in enumerate(result["times"], start=1):
        print(f"run={run_number} time={elapsed:.6f}s")
    print(f"records: {result['records']}")
    print(f"digest: {result['digest']}")
    print(f"mean: {result['mean']:.6f}s")
    print(f"best: {result['best']:.6f}s")


if __name__ == "__main__":
    main()
