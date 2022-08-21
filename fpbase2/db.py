from __future__ import annotations

import os
from typing import Iterator

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DEBUG = os.getenv("DEBUG", "0") != "0"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(
    DATABASE_URL, echo=DEBUG, connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    # it's important to evaluate all SQLModels before creating the tables
    from . import models  # noqa

    # this is the line that creates the database.db file
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
