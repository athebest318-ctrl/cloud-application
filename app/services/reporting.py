"""Build compact reports for service records."""


def build_service_report(
    services: list[dict[str, object]],
    service_types: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Return service rows enriched with a human-readable type name."""
    types_by_id = {
        service_type["id"]: str(service_type["name"]) for service_type in service_types
    }
    report: list[dict[str, object]] = []

    for service in services:
        report.append(
            {
                "id": service["id"],
                "name": service["name"],
                "status": service["status"],
                "type": types_by_id.get(service["type_id"], "unknown"),
            }
        )

    return report
