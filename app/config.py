from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        secrets_dir=PROJECT_ROOT / "secrets",
        extra="ignore",
    )

    app_name: str = "Cloud Application"
    app_version: str = "1.0"
    app_env: Literal["development", "testing", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8010
    api_prefix: str = "/api"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cloud_application"
    db_user: str = "cloud_app"
    lab_db_password: SecretStr
    auth_secret: SecretStr
    https_enabled: bool = False
    https_port: int = 8443
    ssl_certfile: str = "certs/localhost.pem"
    ssl_keyfile: str = "certs/localhost-key.pem"
    storage_path: str = "storage/objects"
    max_upload_size: int = 5 * 1024 * 1024

    @property
    def database_url(self) -> str:
        return URL.create(
            "postgresql+psycopg", username=self.db_user,
            password=self.lab_db_password.get_secret_value(), host=self.db_host,
            port=self.db_port, database=self.db_name,
        ).render_as_string(hide_password=False)

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
