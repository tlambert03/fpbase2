from __future__ import annotations

from enum import Enum
from typing import Any

from sqlmodel import JSON, Column, Field

from .._typed_sa import on_before_save
from ..utils.text import slugify
from .mixins import TimestampModel

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


class FluorescenceCofactor(str, Enum):
    BILIRUBIN = "br"
    BILIVERDIN = "bv"
    FLAVIN = "fl"
    PHYCOCYANOBILIN = "pc"


class SwitchingType(str, Enum):
    BASIC = "b"
    PHOTOACTIVATABLE = "pa"
    PHOTOSWITCHABLE = "ps"
    PHOTOCONVERTIBLE = "pc"
    MULTIPHOTOCHROMIC = "mp"
    TIMER = "t"
    OTHER = "o"


class ProteinBase(TimestampModel):
    name: str = Field(index=True, max_length=128)
    aliases: list[str] = Field(default_factory=list, **LIST_COLUMN)
    agg: OligomerizationTendency | None = None
    seq: str | None = None
    seq_comment: str | None = Field(max_length=512)
    seq_validated: bool = False
    chromophore: str | None = Field(None, max_length=5)
    cofactor: FluorescenceCofactor | None = None
    switch_type: SwitchingType = SwitchingType.BASIC
    blurb: str | None = Field(max_length=512)


class ProteinCreate(ProteinBase):
    pass


class ProteinRead(ProteinBase):
    id: int
    slug: str
    seq_validated: bool


class ProteinUpdate(ProteinBase):
    seq_validated: bool = False


class Protein(ProteinBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None, **UNIQUE)
    seq_validated: bool = False

    @on_before_save
    def _on_before_save(self) -> None:
        self.slug = slugify(self.name)
