from __future__ import annotations

from enum import Enum
from typing import Any

from sqlmodel import JSON, Column, Field, Session, SQLModel

from ..utils.text import slugify

UNIQUE: Any = {"sa_column_kwargs": {"unique": True}}
LIST_COLUMN: Any = {"sa_column": Column(JSON)}


class RecordStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    HIDDEN = "hidden"


class OligomerizationTendency(str, Enum):
    MONOMER = "m"
    DIMER = "d"
    TANDEM_DIMER = "td"
    WEAK_DIMER = "wd"
    TETRAMER = "t"


class _ProteinBase(SQLModel):
    name: str = Field(index=True, max_length=128)
    aliases: list[str] = Field(default_factory=list, **LIST_COLUMN)
    agg: OligomerizationTendency | None = None
    sequence: str | None = None


class ProteinCreate(_ProteinBase):
    pass


class ProteinRead(_ProteinBase):
    id: int
    slug: str


class ProteinUpdate(SQLModel):
    name: str | None = None


class Protein(_ProteinBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, **UNIQUE)

    def before_flush(self, session: Session, flush_context: Any) -> None:
        self.slug = slugify(self.name)

        if self in session.dirty:
            # updating
            ...
        if self in session.new:
            # inserting
            ...
