"""Run reproducible LR34 timings and save real measurements and profiles."""

import argparse
import cProfile
import hashlib
import io
import json
import platform
import pstats
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.reporting import build_service_report
from scripts.service_report_baseline import build_service_report as baseline

SERVICE_COUNT = 20_000
TYPE_COUNT = 200
REPEATS = 5


def create_dataset(service_count=SERVICE_COUNT, type_count=TYPE_COUNT):
    service_types = [{"id": i, "name": f"type-{i}"} for i in range(1, type_count + 1)]
    statuses = ("running", "maintenance", "stopped")
    services = [
        {
            "id": i,
            "name": f"service-{i}",
            "type_id": (i * 37) % type_count + 1,
            "status": statuses[i % len(statuses)],
        }
        for i in range(1, service_count + 1)
    ]
    return services, service_types


def result_digest(report):
    payload = json.dumps(report, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def object_lookup(services, service_types):
    types_by_id = {}
    for item in service_types:
        types_by_id.setdefault(item["id"], item)
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "status": s["status"],
            "type": types_by_id.get(s["type_id"], {"name": "unknown"})["name"],
        }
        for s in services
    ]


def measure(function, dataset):
    times = []
    for _ in range(REPEATS):
        started = time.perf_counter()
        report = function(*dataset)
        times.append(time.perf_counter() - started)
    return {
        "times_seconds": times,
        "mean_seconds": statistics.mean(times),
        "best_seconds": min(times),
        "records": len(report),
        "digest": result_digest(report),
    }


def profile(function, dataset, path):
    profiler = cProfile.Profile()
    profiler.runcall(function, *dataset)
    profiler.dump_stats(str(path))
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative")
    stats.print_stats(20)
    path.with_suffix(".txt").write_text(stream.getvalue().rstrip() + "\n", encoding="utf-8")
    return {"total_calls": stats.total_calls, "total_seconds": stats.total_tt}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("evidence/lr34"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = {
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "repeats": REPEATS,
        "timing_scope": "Report construction only, including lookup dictionary creation",
        "cases": [],
    }
    for n, m in [(5000, 200), (20000, 200), (50000, 200), (20000, 20), (20000, 1000)]:
        dataset = create_dataset(n, m)
        assert baseline(*dataset) == build_service_report(*dataset)
        before = measure(baseline, dataset)
        after = measure(build_service_report, dataset)
        objects = measure(object_lookup, dataset)
        assert before["digest"] == after["digest"] == objects["digest"]
        case = {
            "service_count": n,
            "type_count": m,
            "before": before,
            "after": after,
            "object_lookup": objects,
            "speedup": before["mean_seconds"] / after["mean_seconds"],
            "reduction_percent": 100
            * (1 - after["mean_seconds"] / before["mean_seconds"]),
        }
        if (n, m) == (SERVICE_COUNT, TYPE_COUNT):
            case["profiles"] = {
                "before": profile(
                    baseline, dataset, args.output / "profile_before.prof"
                ),
                "after": profile(
                    build_service_report, dataset, args.output / "profile_after.prof"
                ),
            }
        results["cases"].append(case)
        print(f"services={n} types={m} speedup={case['speedup']:.2f}x digest=equal")
    (args.output / "measurements.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
