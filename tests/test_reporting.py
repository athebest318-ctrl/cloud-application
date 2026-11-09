from app.services.reporting import build_service_report


def test_build_service_report_adds_type_name_and_keeps_unknown() -> None:
    services = [
        {"id": 1, "name": "api", "status": "running", "type_id": 2},
        {"id": 2, "name": "worker", "status": "stopped", "type_id": 9},
    ]
    service_types = [{"id": 2, "name": "web"}]

    assert build_service_report(services, service_types) == [
        {"id": 1, "name": "api", "status": "running", "type": "web"},
        {"id": 2, "name": "worker", "status": "stopped", "type": "unknown"},
    ]
