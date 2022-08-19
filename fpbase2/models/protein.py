from __future__ import annotations

from sqlmodel import SQLModel, Field
from enum import Enum

UNIQUE: dict[str, dict[str, bool]] = {"sa_column_kwargs": {"unique": True}}


class RecordStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    HIDDEN = "hidden"


class OligomerizationTendency(Enum):
    MONOMER = "m"
    DIMER = "d"
    TANDEM_DIMER = "td"
    WEAK_DIMER = "wd"
    TETRAMER = "t"


class ProteinBase(SQLModel):
    name: str = Field(index=True, max_length=128)
    # aliases: list[str] = []
    # agg: OligomerizationTendency | None = None


class Protein(ProteinBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, **UNIQUE)


class ProteinCreate(ProteinBase):
    pass


class ProteinRead(ProteinBase):
    id: int
    # slug: str


class ProteinUpdate(SQLModel):
    name: str | None = None
