from fastapi import APIRouter

from app.config import APP_NAME, APP_VERSION
from app.services.services import count_services


router = APIRouter(
	tags=["System"]
)


@router.get(
	"/status",
	summary="Проверить состояние приложения"
)
def read_status():
	return {
		"status": "ok"
	}


@router.get(
	"/about",
	summary="Получить информацию о приложении"
)
def read_about():
	return {
		"name": APP_NAME,
		"version": APP_VERSION
	}


@router.get(
	"/service-count",
	summary="Получить количество сервисов"
)
def read_service_count():
	return {
		"services": count_services()
	}
