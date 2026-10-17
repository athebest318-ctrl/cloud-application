from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.data.models import Service, ServiceStatusHistory, ServiceType
from app.schemas.services import ServiceCreate, ServiceStatus


def service_to_dict(service: Service) -> dict[str, object]:
    return {
        "id": service.id,
        "name": service.name,
        "type": service.service_type.name,
        "status": service.status,
        "description": service.description,
        "endpoint_url": service.endpoint_url,
    }


def count_services(db: Session) -> int:
    return db.scalar(select(func.count(Service.id))) or 0


def get_all_services(
    db: Session,
    status: ServiceStatus | None = None,
) -> list[Service]:
    statement = select(Service).options(joinedload(Service.service_type))
    if status is not None:
        statement = statement.where(Service.status == status.value)
    statement = statement.order_by(Service.id)
    return list(db.scalars(statement).unique().all())


def get_service_by_id(db: Session, service_id: int) -> Service | None:
    statement = (
        select(Service)
        .options(joinedload(Service.service_type))
        .where(Service.id == service_id)
    )
    return db.scalar(statement)


def get_service_type(db: Session, type_name: str) -> ServiceType | None:
    statement = select(ServiceType).where(ServiceType.name == type_name)
    return db.scalar(statement)


def create_service(db: Session, service: ServiceCreate) -> Service:
    service_type = get_service_type(db, service.type)
    if service_type is None:
        raise ValueError(f"Unknown service type: {service.type}")

    new_service = Service(
        name=service.name,
        type_id=service_type.id,
        status=service.status.value,
        description=service.description,
    )
    db.add(new_service)
    db.flush()
    db.add(
        ServiceStatusHistory(
            service_id=new_service.id,
            status=new_service.status,
        )
    )
    db.commit()
    return get_service_by_id(db, new_service.id)  # type: ignore[return-value]


def update_service(
    db: Session,
    service_id: int,
    service: ServiceCreate,
) -> Service | None:
    current = db.get(Service, service_id)
    if current is None:
        return None

    service_type = get_service_type(db, service.type)
    if service_type is None:
        raise ValueError(f"Unknown service type: {service.type}")

    status_changed = current.status != service.status.value
    current.name = service.name
    current.type_id = service_type.id
    current.status = service.status.value
    current.description = service.description
    if status_changed:
        db.add(
            ServiceStatusHistory(
                service_id=current.id,
                status=current.status,
            )
        )
    db.commit()
    return get_service_by_id(db, current.id)


def delete_service(db: Session, service_id: int) -> bool:
    service = db.get(Service, service_id)
    if service is None:
        return False
    db.delete(service)
    db.commit()
    return True
