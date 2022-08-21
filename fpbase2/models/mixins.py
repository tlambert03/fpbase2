import uuid as uuid_pkg
from datetime import datetime
from typing import TypeVar

from sqlalchemy import text
from sqlmodel import Field

from .._vendored import SQLModel
from ._query import QueryManager

M = TypeVar("M", bound=SQLModel)


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


class QueryMixin(SQLModel):
    @classmethod
    @property
    def q(cls: type[M]) -> QueryManager[M]:
        return QueryManager(cls)
