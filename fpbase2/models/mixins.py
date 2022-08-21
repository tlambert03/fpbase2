import os
import uuid as uuid_pkg
from datetime import datetime
from typing import TypeVar

from sqlalchemy import text
from sqlmodel import Field

from .._vendored import SQLModel
from ..db._query import QueryManager


class UUIDModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
    )


class TimestampModel(SQLModel):
    created: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp")},
    )

    modified: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp"),
            "onupdate": text("current_timestamp"),
        },
    )


class Authorable(SQLModel):
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    updated_by_id: int | None = Field(default=None, foreign_key="user.id")


M = TypeVar("M", bound="QueryMixin")


class QueryMixin(SQLModel):
    _qm: QueryManager | None = None

    @classmethod
    @property
    def q(cls: type[M]) -> QueryManager[M]:
        if cls._qm is None:
            if os.getenv("ALLOW_QM") != "1":
                raise RuntimeError("QueryMixin is disabled, use ALLOW_QM=1 to enable")
            cls._qm = QueryManager(cls)
        return cls._qm
