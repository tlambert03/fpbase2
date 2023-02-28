from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlmodel import Field

from fpbase2._vendored import SQLModel


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


