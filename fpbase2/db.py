from __future__ import annotations

import os
from typing import Iterator

from sqlalchemy import orm
from sqlmodel import SQLModel, create_engine

DEFAULT_DB_URL = "sqlite:///database.db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)
Session = orm.sessionmaker(bind=engine)


def create_db_and_tables() -> None:
    # it's important to evaluate all SQLModels before creating the tables
    from . import models  # noqa

    # this is the line that creates the database.db file
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[orm.Session]:
    with Session() as session:
        yield session
