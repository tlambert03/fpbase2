import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from fpbase2.main import app, get_session


@pytest.fixture
def session():
    """Create a database engine for testing, and connect a session to it."""
    connect_args = {"check_same_thread": False}
    engine = create_engine("sqlite://", connect_args=connect_args, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()
