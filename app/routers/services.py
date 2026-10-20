from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.data.models import User
from app.security import require_permission
from app.schemas.services import ServiceCreate, ServiceResponse, ServiceStatus
from app.services.services import (
    create_service,
    delete_service,
    get_all_services,
    get_service_by_id,
    service_to_dict,
    update_service,
)


router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "",
    response_model=list[ServiceResponse],
    summary="Получить список сервисов",
    description="Возвращает все сервисы или фильтрует их по состоянию.",
)
def read_services(
    status: ServiceStatus | None = Query(
        default=None,
        description="Фильтр по состоянию сервиса",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("services.read")),
):
    return [service_to_dict(item) for item in get_all_services(db, status)]


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Получить сервис по идентификатору",
    description="Возвращает сервис с указанным идентификатором.",
    responses={404: {"description": "Сервис не найден"}},
)
def read_service(
    service_id: int = Path(..., description="Идентификатор сервиса", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("services.read")),
):
    service = get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_to_dict(service)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=201,
    summary="Создать новый сервис",
    description="Создаёт облачный сервис и сохраняет его в PostgreSQL.",
)
def create_service_endpoint(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("services.write")),
):
    try:
        return service_to_dict(create_service(db, service))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Изменить сервис",
    description="Изменяет существующий сервис и фиксирует смену состояния.",
    responses={404: {"description": "Сервис не найден"}},
)
def update_service_endpoint(
    service_id: int,
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("services.write")),
):
    try:
        updated = update_service(db, service_id, service)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if updated is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_to_dict(updated)


@router.delete(
    "/{service_id}",
    summary="Удалить сервис",
    responses={404: {"description": "Сервис не найден"}},
)
def delete_service_endpoint(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("services.write")),
):
    if not delete_service(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted", "id": service_id}
