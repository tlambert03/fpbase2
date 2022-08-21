from datetime import datetime

from sqlmodel import Field

from .mixins import TimestampModel


class Reference(TimestampModel):
    doi: str
    pmid: str
    title: str
    journal: str
    pages: str
    volume: str
    issue: str
    firstauthor: str
    citation: str
    date: datetime
    year: int = Field(ge=1960, le=datetime.now().year + 1)
    summary: str
    # authors
