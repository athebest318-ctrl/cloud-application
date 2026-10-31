from app.config import settings


def main() -> None:
    for name in ("lab_db_password", "auth_secret"):
        value = getattr(settings, name)
        if not value.get_secret_value().strip():
            raise RuntimeError(f"{name} must not be empty")
        print(f"{name}: configured {value}")


if __name__ == "__main__":
    main()
