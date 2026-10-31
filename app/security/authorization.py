from collections.abc import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.data.models import User
from app.services.auth import get_auth_session


bearer_scheme = HTTPBearer(auto_error=False)


def authentication_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise authentication_error("Authentication required")
    if credentials.scheme.lower() != "bearer":
        raise authentication_error("Invalid authentication scheme")

    session = get_auth_session(db, credentials.credentials)
    if session is None:
        raise authentication_error("Invalid or expired session")
    return session.user


def user_permission_codes(user: User) -> set[str]:
    if user.role is None:
        return set()
    return {permission.code for permission in user.role.permissions}


def require_permission(permission_code: str) -> Callable[..., User]:
    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if permission_code not in user_permission_codes(current_user):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {permission_code}",
            )
        return current_user

    return permission_dependency


def require_any_permission(*permission_codes: str) -> Callable[..., User]:
    if not permission_codes:
        raise ValueError("At least one permission code is required")

    def permission_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if user_permission_codes(current_user).isdisjoint(permission_codes):
            required = ", ".join(permission_codes)
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: one of {required}",
            )
        return current_user

    return permission_dependency
