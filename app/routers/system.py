from fastapi import APIRouter
from app.config import settings

from app.services.services import count_services


router = APIRouter(
	tags=["System"]
)


@router.get("/status")
def status():
    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "debug": settings.debug,
        "api_prefix": settings.api_prefix
    }

@router.get(
	"/about",
	summary="Получить информацию о приложении"
)
def read_about():
	return {
		"name": settings.app_name,
		"version": settings.app_version
	}


@router.get(
	"/service-count",
	summary="Получить количество сервисов"
)
def read_service_count():
	return {
		"services": count_services()
	}
