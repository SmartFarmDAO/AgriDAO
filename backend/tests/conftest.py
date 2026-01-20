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


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    with Session(engine) as session:
        user = User(
            email="admin@example.com",
            name="Admin User",
            role=UserRole.ADMIN,
            # hashed_password removed as it's not in the model
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def regular_user():
    """Create a regular user for testing."""
    with Session(engine) as session:
        user = User(
            email="user@example.com",
            name="Regular User",
            role=UserRole.BUYER,
            # hashed_password removed as it's not in the model
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
