from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar

from sqlmodel import JSON, Column, Field, Relationship, text

from fpbase2._typed_sa import on_before_save
from fpbase2.core._query import QueryDescriptor
from fpbase2.utils.text import new_id, slugify
from fpbase2.validators import UNIPROT_REGEX

from .mixins import Authorable, TimeStampedModel
from .reference import Reference
from .user import User

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


UNIQUE: Any = {"sa_column_kwargs": {"unique": True}}


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


class ProteinBase(Authorable, TimeStampedModel):
    name: str = Field(index=True, max_length=128)
    aliases: list[str] | None = Field(None, sa_column=Column(JSON))
    agg: OligomerizationTendency | None = None
    seq: str | None = None
    seq_comment: str | None = Field(None, max_length=512)
    seq_validated: bool = False
    chromophore: str | None = Field(None, max_length=5)
    cofactor: FluorescenceCofactor | None = None
    switch_type: SwitchingType = SwitchingType.BASIC
    blurb: str | None = Field(None, max_length=512)
    pdb: list[str] | None = Field(None, sa_column=Column(JSON))
    genbank: str | None = Field(None, max_length=12, **UNIQUE)
    uniprot: str | None = Field(None, max_length=10, regex=UNIPROT_REGEX, **UNIQUE)
    ipg_id: str | None = Field(None, max_length=12, **UNIQUE)

    primary_reference_id: int | None = Field(default=None, foreign_key="reference.id")
    # oser
    # parent_organism_id
    # default_state_id
    # mw
    # base_name
    # status
    # status_changed

    def slugified_name(self) -> str:
        return slugify(self.name)


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

    # created_by_id: int | None = Field(
    #     default=None, foreign_key="user.id", nullable=False
    # )
    # created_by: User | None = Relationship(back_populates="proteins")
    # updated_by_id: int | None = Field(
    #     default=None, foreign_key="user.id", nullable=False
    # )
    # updated_by: User | None = Relationship(back_populates="proteins_updated")
    # primary_reference: Reference | None = Relationship(back_populates="proteins")

    q: ClassVar[QueryDescriptor["Protein"]] = QueryDescriptor()

    @on_before_save
    def _on_before_save(self, _: Any, conn: "Connection") -> None:
        if self.uuid is None:
            result = conn.execute(text("SELECT uuid FROM protein"))
            self.uuid = new_id(existing={i[0] for i in result if i[0]})
        self.slug = self.slugified_name()
