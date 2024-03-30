import datetime
from collections.abc import Sequence
from contextlib import suppress
from typing import Any, ClassVar, Self, TypeVar

from sqlalchemy import orm, text
from sqlalchemy.exc import InvalidRequestError
from sqlmodel import Field, SQLModel

from ._manager import Manager

M = TypeVar("M", bound=SQLModel)


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class FPBaseModel(SQLModel):
    @orm.declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        from fpbase2.core.config import settings

        name = cls.__name__.lower()
        if str(settings.SQLALCHEMY_DATABASE_URI).endswith("/fpbase"):
            prefix = {
                "user": "users_",
                "reference": "references_",
                "author": "references_",
                "referenceauthorlink": "references_",
            }.get(name, "proteins_")
            name = f"{prefix}{name.removesuffix('link')}"
        return name

    objects: ClassVar[Manager[Self]] = Manager()

    def save(self) -> Self:
        session = type(self).objects._session
        session.add(self)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            with suppress(InvalidRequestError):
                session.refresh(self)
        return self

    def delete(self) -> None:
        session = type(self).objects._session
        session.delete(self)
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.refresh(self)

    # def exists(self) -> bool: ...
    # def update(self, **kwargs: Any) -> Self: ...


class TimeStampedModel(FPBaseModel):
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
