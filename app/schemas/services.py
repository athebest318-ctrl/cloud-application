from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ServiceStatus(str, Enum):
    running = "running"
    maintenance = "maintenance"
    stopped = "stopped"


class ServiceCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Название облачного сервиса",
        examples=["Monitoring Service"],
    )
    type: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Тип облачного сервиса",
        examples=["monitoring"],
    )
    status: ServiceStatus = Field(
        ...,
        description="Текущее состояние сервиса",
        examples=["running"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="Описание сервиса",
    )

    @field_validator("name", "type", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ServiceEndpointUpdate(BaseModel):
    endpoint_url: str = Field(..., min_length=8, max_length=255)

    @field_validator("endpoint_url", mode="before")
    @classmethod
    def normalize_endpoint_url(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ServiceResponse(BaseModel):
    id: int
    name: str
    type: str
    status: ServiceStatus
    description: str | None = None
    endpoint_url: str | None = None
