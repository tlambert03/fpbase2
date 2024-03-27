from datetime import datetime
from enum import Enum

from sqlmodel import Field, UniqueConstraint

from fpbase2.validators import DOI_REGEX

from ._base import FPBaseModel, TimeStampedModel


class AuthorSequence(str, Enum):
    FIRST = "first"
    ADDITIONAL = "additional"


class AuthorReferenceLink(FPBaseModel, table=True):
    author_id: int | None = Field(None, foreign_key="author.id", primary_key=True)
    reference_id: int | None = Field(None, foreign_key="reference.id", primary_key=True)
    author_idx: int = Field(ge=0)
    author_sequence: AuthorSequence | None = None

    # author: "Author" = Relationship(back_populates="reference_links")
    # reference: "Reference" = Relationship(back_populates="author_links")


class AuthorBase(TimeStampedModel):
    family: str | None = None
    given: str | None = None
    orcid: str | None = Field(None, sa_column_kwargs={"unique": True})


class Author(AuthorBase, table=True):
    __table_args__ = (UniqueConstraint("family", "given", name="_family_given_uc"),)
    id: int | None = Field(default=None, primary_key=True)

    # references: list["Reference"] = Relationship(
    #     back_populates="authors", link_model=AuthorReferenceLink
    # )
    # reference_links: list[AuthorReferenceLink] = Relationship(back_populates="author")


class AuthorCreate(AuthorBase): ...


class AuthorUpdate(AuthorBase):
    pass


class AuthorRead(AuthorBase):
    id: int


class ReferenceBase(TimeStampedModel):
    # TODO: fix doi regex validation
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


class Reference(ReferenceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # proteins: Optional["Protein"] = Relationship(back_populates="primary_reference")

    # authors: list[Author] = Relationship(
    #     back_populates="references", link_model=AuthorReferenceLink
    # )
    # author_links: list[AuthorReferenceLink] = Relationship(back_populates="reference")


class ReferenceCreate(FPBaseModel):
    doi: str = Field(..., regex=DOI_REGEX, sa_column_kwargs={"unique": True})
    pmid: str | None = Field(None, max_length=50)


class ReferenceUpdate(ReferenceCreate):
    pass


class ReferenceRead(ReferenceBase):
    id: int
