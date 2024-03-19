import datetime
from collections.abc import Sequence
from typing import Any

from sqlalchemy import text
from sqlmodel import Field

from fpbase2._vendored import SQLModel


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class TimeStampedModel(SQLModel):
    created: datetime.datetime = Field(
        default_factory=_now,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp")},
    )

    modified: datetime.datetime = Field(
        default_factory=_now,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("current_timestamp"),
            "onupdate": text("current_timestamp"),
        },
    )

    def __repr_args__(self) -> Sequence[tuple[str | None, Any]]:
        args = super().__repr_args__()
        return [i for i in args if i[0] not in TimeStampedModel.model_fields]
