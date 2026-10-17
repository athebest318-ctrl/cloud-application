from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.data.models import Permission, Role, User


PERMISSIONS = {
    "services.read": "Просмотр сервисов",
    "services.write": "Создание, изменение и удаление сервисов",
    "objects.read": "Просмотр и скачивание объектов",
    "objects.write": "Загрузка и удаление объектов",
    "users.manage": "Управление пользовательскими учётными записями",
    "roles.manage": "Назначение ролей пользователям",
}

ROLE_MODEL = {
    "viewer": {
        "description": "Просмотр данных",
        "permissions": ["services.read", "objects.read"],
    },
    "operator": {
        "description": "Работа с сервисами и объектами",
        "permissions": [
            "services.read",
            "services.write",
            "objects.read",
            "objects.write",
        ],
    },
    "administrator": {
        "description": "Полное управление приложением",
        "permissions": [
            "services.read",
            "services.write",
            "objects.read",
            "objects.write",
            "users.manage",
            "roles.manage",
        ],
    },
    "content_manager": {
        "description": "Управление файлами и объектами",
        "permissions": ["objects.read", "objects.write", "services.read"],
    },
}


def initialize_access_model(db: Session) -> None:
    permissions: dict[str, Permission] = {}

    for code, description in PERMISSIONS.items():
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if permission is None:
            permission = Permission(code=code, description=description)
            db.add(permission)
            db.flush()
        else:
            permission.description = description
        permissions[code] = permission

    for role_name, role_data in ROLE_MODEL.items():
        role = db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role = Role(name=role_name, description=role_data["description"])
            db.add(role)
            db.flush()
        else:
            role.description = role_data["description"]
        role.permissions = [permissions[code] for code in role_data["permissions"]]

    db.commit()


def assign_default_roles(db: Session) -> int:
    viewer = get_role_by_name(db, "viewer")
    if viewer is None:
        return 0

    users = db.scalars(select(User).where(User.role_id.is_(None))).all()
    for user in users:
        user.role_id = viewer.id
    db.commit()
    return len(users)


def get_roles(db: Session) -> list[Role]:
    return list(
        db.scalars(
            select(Role)
            .options(selectinload(Role.permissions))
            .order_by(Role.id)
        ).all()
    )


def get_role_by_name(db: Session, role_name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == role_name))


def assign_role(
    db: Session,
    user_id: int,
    role_name: str,
) -> tuple[User | None, str | None]:
    user = db.get(User, user_id)
    if user is None:
        return None, "user"

    role = get_role_by_name(db, role_name)
    if role is None:
        return None, "role"

    user.role_id = role.id
    db.commit()
    db.refresh(user)
    return user, None


def get_user_access(db: Session, user_id: int) -> dict[str, object] | None:
    user = db.scalar(
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    if user is None:
        return None

    role_name = user.role.name if user.role is not None else None
    permissions = (
        sorted(permission.code for permission in user.role.permissions)
        if user.role is not None
        else []
    )
    return {
        "user_id": user.id,
        "username": user.username,
        "role": role_name,
        "permissions": permissions,
    }
