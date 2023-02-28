from collections.abc import Iterator

from rich import print
from sqlalchemy import create_engine, text

from fpbase2.models.protein import Protein

DB_URL = "postgresql:///fpbase"
engine = create_engine(DB_URL, echo=True, future=True)


def converted_proteins(limit: int | None = None) -> Iterator[Protein]:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM proteins_protein LIMIT :limit"), {"limit": limit}
        )
        for row in result:
            yield Protein(**row)


prots = list(converted_proteins())
for p in prots[::40]:
    print(repr(p))
