from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, text

from ._base import FPBaseModel

if TYPE_CHECKING:
    from .protein import Protein
# TODO replace email str with EmailStr when sqlmodel supports it


class UserBase(FPBaseModel):
    username: str = Field(index=True, max_length=150, sa_column_kwargs={"unique": True})
    password: str
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    email: str = Field(unique=True, index=True)

    last_login: datetime | None = None
    date_joined: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp")},
    )

    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    proteins_created: list["Protein"] = Relationship(
        back_populates="created_by",
        sa_relationship_kwargs={
            "primaryjoin": "Protein.created_by_id==User.id",
            "lazy": "joined",
        },
    )
    proteins_updated: list["Protein"] = Relationship(
        back_populates="updated_by",
        sa_relationship_kwargs={
            "primaryjoin": "Protein.updated_by_id==User.id",
            "lazy": "joined",
        },
    )
