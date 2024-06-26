from collections.abc import Iterator
from typing import TypeVar

from sqlmodel import Session, SQLModel, create_engine, text

from fpbase2.core import db
from fpbase2.models.protein import Protein
from fpbase2.models.reference import Author, Reference, ReferenceAuthorLink
from fpbase2.models.user import User
from fpbase2.utils import crossref_work

URL = "postgresql+psycopg:///fpbase"
fpb_engine = create_engine(URL, echo=True)

M = TypeVar("M", bound=SQLModel)
QUERIES: dict[type[SQLModel], str] = {
    User: "SELECT * FROM users_user ORDER BY date_joined LIMIT :limit",
    Protein: "SELECT * FROM proteins_protein ORDER BY created LIMIT :limit",
    Reference: "SELECT * FROM references_reference ORDER BY created LIMIT :limit",
}


def iter_fpb_table(Model: type[M], n: int = 10) -> Iterator[M]:
    with fpb_engine.connect() as conn:
        conn = conn.execution_options(
            isolation_level="SERIALIZABLE",
            postgresql_readonly=True,
            postgresql_deferrable=True,
        )
        with conn.begin():
            result = conn.execute(text(QUERIES[Model]), {"limit": n})
            for row in result.mappings():
                yield Model(**row)


def add_fpb_objects(model: type[M], n: int = 10) -> None:
    objects: list[SQLModel]
    objects = list(iter_fpb_table(model, n))
    with Session(db.engine) as session:
        for obj in objects:
            session.add(obj)
        session.commit()


def add_fpb_proteins(n: int = 200) -> None:
    add_fpb_objects(Protein, n)


def add_fpb_users(n: int = 10) -> None:
    add_fpb_objects(User, n)


def add_fpb_references(n: int = 10) -> None:
    with Session(db.engine) as session:
        # for every reference currently in FPbase
        for db_ref in iter_fpb_table(Reference, n):
            print("adding reference", db_ref.doi)
            # look up the reference in CrossRef
            work = crossref_work(db_ref.doi)
            # for each author in the reference
            _db_authors: list[tuple[Author, str]] = []
            for author in work.author:
                # create an fpbase2 author object
                db_author = Author.objects.where(
                    (Author.given == author.given) & (Author.family == author.family),
                    limit=1,
                )
                if not db_author:
                    db_author = Author.model_validate(author)
                    session.add(db_author)
                _db_authors.append((db_author, author.sequence))  # type: ignore
            session.add(db_ref)
            session.commit()

            for i, (db_author, seq) in enumerate(_db_authors):
                # create a link table object
                link = ReferenceAuthorLink(
                    author_id=db_author.id,
                    reference_id=db_ref.id,
                    author_idx=i,
                    author_sequence=seq,
                )
                # add the objects to the session
                session.add(link)
                session.commit()
