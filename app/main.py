from fastapi import FastAPI, Path
from app.config import settings
# from app.config import APP_NAME, APP_VERSION

# import app.routers.services
# import app.routers.system
# import app.services.services
# import app.data.services
# import app.schemas.services

from app.routers.services import router as services_router
from app.routers.system import router as system_router

tags_metadata = [
    {
        "name": "Services",
        "description": (
            "Операции управления программными "
            "сервисами Cloud Application."
        )
    },
    {
        "name": "System",
        "description": "Системные маршруты приложения."
    }
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    debug=settings.debug,
    openapi_tags=tags_metadata
)

app.include_router(services_router)
app.include_router(system_router)

