from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["student01"])
    password: str = Field(..., min_length=6, max_length=100, examples=["cloud12345"])

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "session"


class SessionResponse(BaseModel):
    authenticated: bool
    user_id: int
    username: str
