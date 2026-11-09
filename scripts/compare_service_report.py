"""Compare linear and dictionary lookups for laboratory 34."""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.reporting import build_service_report
from scripts.profile_service_report import create_dataset, result_digest

ReportFunction = Callable[
    [list[dict[str, object]], list[dict[str, object]]],
    list[dict[str, object]],
]


def build_service_report_linear(
    services: list[dict[str, object]],
    service_types: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Keep the original linear implementation for controlled comparison."""
    report: list[dict[str, object]] = []
    for service in services:
        type_name = "unknown"
        for service_type in service_types:
            if service_type["id"] == service["type_id"]:
                type_name = str(service_type["name"])
                break
        report.append(
            {
                "id": service["id"],
                "name": service["name"],
                "status": service["status"],
                "type": type_name,
            }
        )
    return report


def measure(
    function: ReportFunction,
    services: list[dict[str, object]],
    service_types: list[dict[str, object]],
    repeats: int = 5,
) -> tuple[float, str]:
    times: list[float] = []
    report: list[dict[str, object]] = []
    for _ in range(repeats):
        started = time.perf_counter()
        report = function(services, service_types)
        times.append(time.perf_counter() - started)
    return statistics.mean(times), result_digest(report)


def compare(service_count: int, type_count: int) -> dict[str, object]:
    services, service_types = create_dataset(service_count, type_count)
    before, digest_before = measure(
        build_service_report_linear,
        services,
        service_types,
    )
    after, digest_after = measure(
        build_service_report,
        services,
        service_types,
    )
    return {
        "service_count": service_count,
        "type_count": type_count,
        "before": before,
        "after": after,
        "speedup": before / after,
        "digest_equal": digest_before == digest_after,
    }


def main() -> None:
    results = {
        "service_count": [compare(count, 200) for count in (5_000, 20_000, 50_000)],
        "type_count": [compare(20_000, count) for count in (20, 200, 1_000)],
    }
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
