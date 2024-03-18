from datetime import datetime
from typing import ClassVar

from sqlmodel import Field, SQLModel, text

from fpbase2.core._query import QueryDescriptor

# TODO replace email str with EmailStr when sqlmodel supports it

class UserBase(SQLModel):
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

    q: ClassVar[QueryDescriptor["User"]] = QueryDescriptor()
