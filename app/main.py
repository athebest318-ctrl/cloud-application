from fastapi import FastAPI

from app.config import APP_NAME, APP_VERSION, settings
from app.logging_config import configure_logging
from app.middleware.request_logging import register_request_logging
from app.routers.access import router as access_router
from app.routers.auth import router as auth_router
from app.routers.integration import router as integration_router
from app.routers.objects import router as objects_router
from app.routers.services import router as services_router
from app.routers.system import router as system_router

tags_metadata = [
    {
        "name": "Services",
        "description": "Операции управления сервисами Cloud Application.",
    },
    {
        "name": "Objects",
        "description": "Загрузка и получение файлов из объектного хранилища.",
    },
    {
        "name": "Authentication",
        "description": "Регистрация, вход и управление учебными сеансами.",
    },
    {
        "name": "Access Model",
        "description": "Роли пользователей и эффективные разрешения.",
    },
    {
        "name": "System",
        "description": "Системные маршруты приложения.",
    },
]

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Учебное серверное приложение для изучения разработки "
        "программного обеспечения облачных систем."
    ),
    openapi_tags=tags_metadata,
)

configure_logging(settings.log_level)
register_request_logging(app, "cloud-application")

app.include_router(services_router)
app.include_router(objects_router)
app.include_router(auth_router)
app.include_router(access_router)
app.include_router(system_router)
app.include_router(integration_router)


@app.get("/", tags=["System"], summary="Получить основную информацию о приложении")
def root():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "Laboratory works 1-25 completed",
    }
