import os
import shutil
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Configure a temp SQLite DB before importing the app
TEST_DB_DIR = tempfile.mkdtemp(prefix="agri_test_")
TEST_DB_PATH = os.path.join(TEST_DB_DIR, "test_agri.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["STRIPE_API_KEY"] = "sk_test_dummy"
os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_dummy"
os.environ["GOOGLE_CLIENT_ID"] = "dummy_client_id"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy_client_secret"
os.environ["JWT_SECRET"] = "test_secret"

from app.main import app  # noqa: E402
from app.database import engine  # noqa: E402
from app.models import User, UserRole  # noqa: E402
from sqlmodel import SQLModel, Session  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db() -> Generator[None, None, None]:
    # Create all tables for tests
    SQLModel.metadata.create_all(engine)
    try:
        yield
    finally:
        # Cleanup temp dir
        shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def _cleanup_db():
    """Clean up database between tests to avoid UNIQUE constraint violations."""
    yield
    # Clean up after each test
    with Session(engine) as session:
        # Delete all users to avoid conflicts
        session.exec(SQLModel.metadata.tables['user'].delete())
        session.commit()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a database session for tests."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user for testing."""
    user = User(
        email="admin@example.com",
        name="Admin User",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session: Session):
    """Create a regular user for testing."""
    user = User(
        email="user@example.com",
        name="Regular User",
        role=UserRole.BUYER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
