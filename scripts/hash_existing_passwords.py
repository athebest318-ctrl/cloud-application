from sqlalchemy import select

from app.data.database import SessionLocal
from app.data.models import User
from app.security.passwords import hash_password


def main() -> None:
    with SessionLocal() as db:
        converted = 0
        for user in db.scalars(select(User)):
            if not user.password_hash.startswith("$argon2"):
                user.password_hash = hash_password(user.password_hash)
                converted += 1
        db.commit()
    print(f"Passwords converted: {converted}")


if __name__ == "__main__":
    main()
