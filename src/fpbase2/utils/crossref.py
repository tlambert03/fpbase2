from datetime import datetime
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

API_BASE = "https://api.crossref.org"
MAIL_TO = "talley.lambert+fpbase@gmail.org"


@lru_cache
def crossref_work(doi: str) -> "Work":
    import httpx

    from fpbase2 import __version__

    url = f"{API_BASE}/works/{doi}"
    ua = f"python-httpx/{httpx.__version__}"
    ua += f" FPBase/{__version__} (https://fpbase.org/ mailto:{MAIL_TO})"
    r = httpx.get(url, headers={"User-Agent": ua, "X-USER-AGENT": ua}, timeout=10)
    r.raise_for_status()
    return Work.model_validate(r.json()["message"])


class Reference(BaseModel):
    key: str
    doi: str | None = None
    unstructured: str | None = None


class Date(BaseModel):
    date_parts: list[list[int]] = Field(..., alias="date-parts")
    date_time: datetime = Field(..., alias="date-time")
    timestamp: int


class DateParts(BaseModel):
    date_parts: list[list[int]] = Field(..., alias="date-parts")


class Author(BaseModel):
    ORCID: str | None = None
    suffix: str | None = None
    given: str | None = None
    family: str
    name: str | None = None
    authenticated_orcid: bool | None = Field(None, alias="authenticated-orcid")
    prefix: str | None = None
    sequence: Literal["first", "additional"] | None = None
    # affiliation: List[Affiliation]


class Work(BaseModel):
    DOI: str = Field(..., description="The DOI identifier associated with the work")
    prefix: str

    reference_count: int = Field(..., alias="reference-count")

    publisher: str
    container_title: list[str] | None = Field(None, alias="container-title")
    title: list[str]
    abstract: str | None = None
    page: str | None = None
    volume: str | None = None
    issue: str | None = None
    author: list[Author]
    type: str
    created: Date
    source: str

    accepted: DateParts | None = None
    approved: DateParts | None = None
    published_online: DateParts | None = Field(None, alias="published-online")
    published_print: DateParts | None = Field(None, alias="published-print")
    content_updated: DateParts | None = Field(None, alias="content-updated")
    edition_number: str | None = Field(None, alias="edition-number")
    posted: DateParts | None = None

    # reference: Reference | list[Reference] | None = None

    # group_title: list[str] | str | None = Field(None, alias="group-title")
    # content_created: DateParts | None = Field(None, alias="content-created")
    # language: str | None = None
    # deposited: Date
    # score: int
    # degree: str | None = None
    # subtitle: list[str] | None = None
    # editor: list[Author] | None = None
    # short_title: list[str] | None = Field(None, alias="short-title")
    # issued: DateParts
    # references_count: int = Field(..., alias="references-count")
    # part_number: str | None = Field(None, alias="part-number")
    # alternative_id: list[str] | None = Field(None, alias="alternative-id")
    # URL: str
    # ISSN: list[str] | None = None
    # subject: list[str] | None = None
    # published_other: DateParts | None = Field(None, alias="published-other")
    # subtype: str | None = None


class WorkMessage(BaseModel):
    status: str
    message_type: Literal["work"] = "work"
    message_version: str = Field(..., alias="message-version")
    message: Work
