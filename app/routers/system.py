from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import APP_NAME, settings
from app.data.database import get_db
from app.services.services import count_services


router = APIRouter(tags=["System"])


@router.get("/status", summary="Проверить состояние приложения")
def read_status():
    return {
        "status": "ok",
        "service": APP_NAME,
        "environment": settings.app_env,
        "host": settings.app_host,
        "port": settings.app_port,
        "api_prefix": settings.api_prefix,
    }


@router.get("/about", summary="Получить информацию о приложении")
def read_about():
    return {
        "name": APP_NAME,
        "type": "server application",
        "language": "Python",
        "framework": "FastAPI",
    }


@router.get("/course", summary="Получить информацию о дисциплине")
def read_course():
    return {
        "discipline": (
            "Управление работами и разработка программного "
            "обеспечения облачных систем"
        ),
        "laboratory": 2,
        "project": APP_NAME,
    }


@router.get("/service-count", summary="Получить количество сервисов")
def read_service_count(db: Session = Depends(get_db)):
    return {"services": count_services(db)}
