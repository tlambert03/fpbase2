import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

# use in-memory SQLite for testing
# must be here before settings are imported
os.environ["DB_SQLITE_PATH"] = ":memory:"

from fpbase2.core.db import engine, init_db  # noqa: E402
from fpbase2.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)  # type: ignore
def db() -> Generator[Session, None, None]:
    """Create a database engine for testing, and connect a session to it."""
    with Session(engine) as session:
        init_db(session)
        yield session


# @pytest.fixture(scope="function")
# def rollback_session():
#     with Session(engine) as session:
#         init_db(session)
#         transaction = session.begin()
#         yield session
#         session.rollback()
#         transaction.close()


@pytest.fixture(scope="module")  # type: ignore
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
