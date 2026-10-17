import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.data.database import SessionLocal
from app.services.access import assign_default_roles, initialize_access_model


def main() -> None:
    db = SessionLocal()
    try:
        initialize_access_model(db)
        assigned = assign_default_roles(db)
        print(f"Access model initialized; default roles assigned: {assigned}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
