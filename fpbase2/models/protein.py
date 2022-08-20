from __future__ import annotations

from enum import Enum
from random import choices
from typing import TYPE_CHECKING, Any, Container, Sequence

from sqlmodel import JSON, Column, Field, text

from .._typed_sa import on_before_save
from ..utils.text import slugify
from ..validators import UNIPROT_REGEX
from .mixins import TimestampModel

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


UNIQUE: Any = {"sa_column_kwargs": {"unique": True}}


def new_id(
    k: int = 5,
    opts: Sequence[str] = "ABCDEFGHJKLMNOPQRSTUVWXYZ123456789",
    existing: Container[str] = (),
) -> str:
    i = 0
    while (i := i + 1) < 100:
        if (_uuid := "".join(choices(opts, k=k))) not in existing:
            return _uuid
    raise RuntimeError("Could not generate unique uuid after 100 tries")


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
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    agg: OligomerizationTendency | None = None
    seq: str | None = None
    seq_comment: str | None = Field(max_length=512)
    seq_validated: bool = False
    chromophore: str | None = Field(None, max_length=5)
    cofactor: FluorescenceCofactor | None = None
    switch_type: SwitchingType = SwitchingType.BASIC
    blurb: str | None = Field(max_length=512)
    pdb: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    genbank: str | None = Field(None, max_length=12, **UNIQUE)
    uniprot: str | None = Field(None, max_length=10, regex=UNIPROT_REGEX, **UNIQUE)
    ipg_id: str | None = Field(None, max_length=12, **UNIQUE)


class ProteinCreate(ProteinBase):
    pass


class ProteinRead(ProteinBase):
    id: int
    uuid: str
    slug: str
    seq_validated: bool


class ProteinUpdate(ProteinBase):
    seq_validated: bool = False


class Protein(ProteinBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # TODO: allow_mutation = False
    uuid: str | None = Field(default=None, index=True, max_length=5, **UNIQUE)
    slug: str | None = Field(default=None, **UNIQUE)
    seq_validated: bool = False

    @on_before_save
    def _on_before_save(self, _: Any, conn: Connection) -> None:
        if self.uuid is None:
            result = conn.execute(text("SELECT uuid FROM protein"))
            self.uuid = new_id(existing={i[0] for i in result if i[0]})
        self.slug = slugify(self.name)
