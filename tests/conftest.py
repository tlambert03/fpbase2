from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from fpbase2.main import app


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    """Create a database engine for testing, and connect a session to it."""
    # create in-memory database with "sqlite://"
    # we need to also tell SQLAlchemy that we want to be able to use the same
    # in-memory database object from different threads.
    # We tell it that with the poolclass=StaticPool parameter.
    # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
    engine = create_engine(
        "sqlite://",
        # connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        # echo="-v" in sys.argv,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # init_db(session)
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
