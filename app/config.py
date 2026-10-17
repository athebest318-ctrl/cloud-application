from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Cloud Application"
    app_version: str = "1.0"
    app_env: Literal["development", "testing", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8010
    api_prefix: str = "/api"
    database_url: str = (
        "postgresql+psycopg://cloud_app:change_me@localhost:5432/"
        "cloud_application"
    )
    storage_path: str = "storage/objects"
    max_upload_size: int = 5 * 1024 * 1024

    @property
    def storage_directory(self) -> Path:
        path = Path(self.storage_path)
        return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
APP_NAME = settings.app_name
APP_VERSION = settings.app_version
