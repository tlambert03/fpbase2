from datetime import datetime
from typing import Any, Sequence, TypeVar

from sqlalchemy import text
from sqlmodel import Field

from .._vendored import SQLModel
from ..core.config import settings
from ..db._query import QueryManager


class TimeStampedModel(SQLModel):
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

    def __repr_args__(self) -> Sequence[tuple[str | None, Any]]:
        args = super().__repr_args__()
        return [i for i in args if i[0] not in TimeStampedModel.__fields__]


class Authorable(SQLModel):
    created_by_id: int | None = Field(default=None, foreign_key="user.id")
    updated_by_id: int | None = Field(default=None, foreign_key="user.id")

    def __repr_args__(self) -> Sequence[tuple[str | None, Any]]:
        args = super().__repr_args__()
        return [i for i in args if i[0] not in Authorable.__dict__]


M = TypeVar("M", bound="QueryMixin")


class QueryMixin(SQLModel):
    _qm: QueryManager | None = None

    @classmethod
    @property
    def q(cls: type[M]) -> QueryManager[M]:
        if cls._qm is None:
            if not settings.ALLOW_QM:
                raise RuntimeError("QueryMixin is disabled, use ALLOW_QM=1 to enable")
            cls._qm = QueryManager(cls)
        return cls._qm
