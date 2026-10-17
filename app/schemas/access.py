from pydantic import BaseModel, Field, field_validator


class RoleAssign(BaseModel):
    role_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["operator"],
    )

    @field_validator("role_name", mode="before")
    @classmethod
    def normalize_role_name(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: list[str]


class UserAccessResponse(BaseModel):
    user_id: int
    username: str
    role: str | None
    permissions: list[str]
