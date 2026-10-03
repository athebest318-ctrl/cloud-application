from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    app_name: str = "Cloud Application"
    app_version: str = "1.0"

    app_description: str = (
        "Учебное серверное приложение для изучения "
        "разработки программного обеспечения облачных систем."
    )

    app_env: Literal[
    "development",
    "testing",
    "production"
    ] = "development"

    app_host: str = "127.0.0.1"
    app_port: int = 8000
    api_prefix: str = "/api"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
