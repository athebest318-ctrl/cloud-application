"""Prepare service reports using a single lookup table per call."""


def build_service_report(services: list[dict], service_types: list[dict]) -> list[dict]:
    types_by_id = {}
    for item in service_types:
        # Preserve the reference's first-match behavior even for duplicate IDs.
        types_by_id.setdefault(item["id"], item["name"])
    return [
        {
            "id": service["id"],
            "name": service["name"],
            "status": service["status"],
            "type": types_by_id.get(service["type_id"], "unknown"),
        }
        for service in services
    ]
