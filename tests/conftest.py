import os
import sys
import pytest

# Ensure backend directory is on sys.path for imports (app.*)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.db.base import Base


@pytest.fixture(scope="session")
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)



@pytest.fixture
def db(engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    """Create a TestClient with overridden get_db dependency."""
    from fastapi.testclient import TestClient
    from app.db.session import get_db
    from app.main import app

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

