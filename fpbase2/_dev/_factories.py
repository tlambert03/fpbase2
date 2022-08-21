import os
from random import choices
from typing import Iterator

from dotenv import load_dotenv
from faker import Faker
from pydantic_factories import ModelFactory
from sqlmodel import Session, create_engine, text

from fpbase2 import db
from fpbase2.models.protein import Protein

load_dotenv()

AA_LETTERS: str = "ARNDCEQGHILKMFPSTWYV"
fake = Faker()


class ProteinFactory(ModelFactory):
    __model__ = Protein

    name: str = fake.first_name
    seq = lambda: "".join(choices(AA_LETTERS, k=200))
    chromophore = lambda: "".join(choices(AA_LETTERS, k=3))


def iter_fpb_proteins(n: int = 10) -> Iterator[Protein]:
    DB_URL = os.getenv("PRODUCT_DATABASE_URL", "postgresql:///fpbase")
    fpb_engine = create_engine(DB_URL, echo=True)
    with fpb_engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM proteins_protein LIMIT :limit"), {"limit": n}
        )
        for row in result:
            yield Protein(**row)


def add_fpb_proteins(n: int = 10) -> None:
    proteins = list(iter_fpb_proteins(n))
    with Session(db.engine) as session:
        for protein in proteins:
            session.add(protein)
        session.commit()
