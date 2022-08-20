import sys

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from fpbase2.db import get_session
from fpbase2.main import app


@pytest.fixture
def session():
    """Create a database engine for testing, and connect a session to it."""
    # create in-memory database with "sqlite://"
    # we need to also tell SQLAlchemy that we want to be able to use the same
    # in-memory database object from different threads.
    # We tell it that with the poolclass=StaticPool parameter.
    # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo="-v" in sys.argv,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session: Session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()
