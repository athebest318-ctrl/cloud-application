import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.data.database import Base
from app.data.models import Permission, Role, User
from app.schemas.auth import UserRegister
from app.services.access import (
    assign_default_roles,
    assign_role,
    get_roles,
    get_user_access,
    initialize_access_model,
)
from app.services.auth import register_user


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    engine.dispose()


def test_access_model_is_idempotent(db: Session) -> None:
    initialize_access_model(db)
    initialize_access_model(db)

    assert db.scalar(select(func.count()).select_from(Role)) == 4
    assert db.scalar(select(func.count()).select_from(Permission)) == 6
    assert [role.name for role in get_roles(db)] == [
        "viewer",
        "operator",
        "administrator",
        "content_manager",
    ]


def test_registered_user_receives_viewer_role(db: Session) -> None:
    initialize_access_model(db)
    user = register_user(
        db,
        UserRegister(username="student04", password="cloud12345"),
    )

    assert user is not None
    access = get_user_access(db, user.id)
    assert access == {
        "user_id": user.id,
        "username": "student04",
        "role": "viewer",
        "permissions": ["objects.read", "services.read"],
    }


def test_existing_user_gets_default_role_and_can_be_promoted(db: Session) -> None:
    user = User(username="student01", password="cloud12345")
    db.add(user)
    db.commit()
    db.refresh(user)

    initialize_access_model(db)
    assert assign_default_roles(db) == 1
    assert get_user_access(db, user.id)["role"] == "viewer"

    updated, error = assign_role(db, user.id, "operator")
    assert error is None
    assert updated is not None
    assert get_user_access(db, user.id)["permissions"] == [
        "objects.read",
        "objects.write",
        "services.read",
        "services.write",
    ]


def test_unknown_role_does_not_change_user(db: Session) -> None:
    initialize_access_model(db)
    user = register_user(
        db,
        UserRegister(username="student02", password="cloud12345"),
    )
    assert user is not None

    updated, error = assign_role(db, user.id, "superuser")
    assert updated is None
    assert error == "role"
    assert get_user_access(db, user.id)["role"] == "viewer"
