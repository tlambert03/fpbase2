import os
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

# this unused import is required before calling create_all()!
from . import models  # noqa


DEFAULT_DB_URL = "sqlite:///database.db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    # this is the line that creates the database.db file
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
