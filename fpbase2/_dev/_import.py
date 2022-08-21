import os
from typing import Iterator, TypeVar

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, text

from fpbase2 import db
from fpbase2.models.protein import Protein
from fpbase2.models.reference import Reference
from fpbase2.models.user import User

load_dotenv()

PRODUCTION_DB_URL = os.getenv("PRODUCT_DATABASE_URL", "postgresql:///fpbase")
fpb_engine = create_engine(PRODUCTION_DB_URL, echo=True)
M = TypeVar("M", bound=SQLModel)

QUERIES: dict[type[SQLModel], str] = {
    User: "SELECT * FROM users_user ORDER BY date_joined LIMIT :limit",
    Protein: "SELECT * FROM proteins_protein ORDER BY created LIMIT :limit",
    Reference: "SELECT * FROM references_reference ORDER BY created LIMIT :limit",
}


def iter_fpb_table(Model: type[M], n: int = 10) -> Iterator[M]:
    with fpb_engine.connect() as conn:
        for row in conn.execute(text(QUERIES[Model]), {"limit": n}):
            yield Model(**row)


def add_fpb_objects(model: type[M], n: int = 10) -> None:
    objects: list[SQLModel]
    objects = list(iter_fpb_table(model, n))
    with Session(db.engine) as session:
        for obj in objects:
            session.add(obj)
        session.commit()


def add_fpb_proteins(n: int = 10) -> None:
    add_fpb_objects(Protein, n)


def add_fpb_users(n: int = 10) -> None:
    add_fpb_objects(User, n)


def add_fpb_references(n: int = 10) -> None:
    add_fpb_objects(Reference, n)
