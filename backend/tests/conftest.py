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

from app.main import app  # noqa: E402
from app.database import engine  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402


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
