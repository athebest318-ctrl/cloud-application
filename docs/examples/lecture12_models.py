"""Учебные модели из задания лекции 12. Подключение к БД не выполняется."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ServiceType(Base):
    __tablename__ = "service_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    services: Mapped[list["Service"]] = relationship(back_populates="service_type")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20))
    type_id: Mapped[int] = mapped_column(ForeignKey("service_types.id"))
    service_type: Mapped[ServiceType] = relationship(back_populates="services")


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    status: Literal["running", "maintenance", "stopped"]
    type_id: int = Field(gt=0)


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
