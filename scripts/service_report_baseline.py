"""Unoptimized reference from LR34, retained for reproducible comparisons."""


def build_service_report(services: list[dict], service_types: list[dict]) -> list[dict]:
    report = []
    for service in services:
        type_name = "unknown"
        for service_type in service_types:
            if service_type["id"] == service["type_id"]:
                type_name = service_type["name"]
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
