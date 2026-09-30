from app.data.services import services_data
from app.schemas.services import ServiceCreate


def count_services():
    return len(services_data)


def get_all_services():
    return services_data


def get_service_by_id(service_id: int):
    for service in services_data:
        if service["id"] == service_id:
            return service

    return None

def create_service(service: ServiceCreate):
    new_id = max(
        (item["id"] for item in services_data),
        default=0
    ) + 1

    new_service = {
        "id": new_id,
        "name": service.name,
        "type": service.type,
        "status": service.status
    }

    services_data.append(new_service)

    return new_service

def update_service(
    service_id: int,
    service: ServiceCreate
):
    for item in services_data:
        if item["id"] == service_id:
            item["name"] = service.name
            item["type"] = service.type
            item["status"] = service.status

            return item

    return None

def delete_service(service_id: int):
    for item in services_data:
        if item["id"] == service_id:
            services_data.remove(item)
            return item

    return None

def get_services_by_status(status: str):
    return [
        service
        for service in services_data
        if service["status"] == status
    ]
