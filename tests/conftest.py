from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from fpbase2.core.db import engine, init_db
from fpbase2.main import app


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """Create a database engine for testing, and connect a session to it."""
    with Session(engine) as session:
        init_db(session)
        yield session
        # statement = delete(Item)
        # session.execute(statement)
        # statement = delete(User)
        # session.execute(statement)
        # session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
