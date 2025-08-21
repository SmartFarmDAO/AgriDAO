import os
from sqlmodel import SQLModel, create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agri.db")
# Enable pool_pre_ping for better connection handling in prod Postgres
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def init_db() -> None:
    # Database schema is now managed via Alembic migrations.
    # This function intentionally does nothing to avoid implicit schema drift.
    # Run migrations via: `alembic upgrade head` (see backend/README.md)
    return

