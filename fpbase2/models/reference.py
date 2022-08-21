from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from ..validators import DOI_REGEX
from .mixins import Authorable, QueryMixin, TimestampModel

if TYPE_CHECKING:
    from .protein import Protein


class ReferenceBase(Authorable, TimestampModel):
    # TODO: fix server side regex
    doi: str = Field(sa_column_kwargs={"unique": True})
    pmid: str | None = Field(None, max_length=50, sa_column_kwargs={"unique": True})
    title: str | None = Field(max_length=512)
    journal: str | None = None
    pages: str | None = None
    volume: str | None = None
    issue: str | None = None
    citation: str | None = None
    year: int = Field(ge=1960, le=datetime.now().year + 1)
    summary: str
    firstauthor: str | None = None
    date: datetime | None = None


class Reference(ReferenceBase, QueryMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proteins: Optional["Protein"] = Relationship(back_populates="primary_reference")


class ReferenceCreate(SQLModel):
    doi: str = Field(..., regex=DOI_REGEX, sa_column_kwargs={"unique": True})
    pmid: str | None = Field(None, max_length=50)


class ReferenceRead(ReferenceBase):
    id: int


class ReferenceUpdate(ReferenceCreate):
    pass
