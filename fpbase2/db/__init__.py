from __future__ import annotations

from collections.abc import Iterator

from sqlmodel import Session, SQLModel

from ._engine import engine

__all__ = ["create_db_and_tables", "get_session", "engine"]


def create_db_and_tables() -> None:
    # it's important to evaluate all SQLModels before creating the tables
    from .. import models  # noqa

    # this is the line that creates the database.db file
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
