from sqlalchemy import select

from app.data.database import SessionLocal
from app.data.models import User


def main() -> None:
    with SessionLocal() as db:
        for user in db.scalars(select(User).order_by(User.id)):
            state = "HASHED" if user.password_hash.startswith("$argon2") else "LEGACY"
            print(f"{user.username}: {state}")


if __name__ == "__main__":
    main()
