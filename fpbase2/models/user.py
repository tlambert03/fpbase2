from datetime import datetime

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    # password: str
    last_login: datetime | None = None
    is_superuser: bool | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    is_staff: bool | None = None
    is_active: bool | None = None
    date_joined: datetime | None = None
    groups: list[str] | None = None
    name: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
