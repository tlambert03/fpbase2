from __future__ import annotations

import os
from itertools import chain
from typing import TYPE_CHECKING, Any, Iterator

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

if TYPE_CHECKING:
    from sqlalchemy.orm.unitofwork import UOWTransaction


DEFAULT_DB_URL = "sqlite:///database.db"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables() -> None:
    # it's important to evaluate all SQLModels before creating the tables
    from . import models  # noqa

    # this is the line that creates the database.db file
    SQLModel.metadata.create_all(engine)


def _bind_listeners(session: Session) -> None:
    @event.listens_for(session, "before_flush")  # type: ignore
    def _before_flush(session: Session, context: UOWTransaction, _: Any) -> None:
        "listen for the 'before_flush' event"
        for obj in chain(session.new, session.dirty):
            if method := getattr(obj, "before_flush", None):
                method(session, context)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        _bind_listeners(session)
        yield session
