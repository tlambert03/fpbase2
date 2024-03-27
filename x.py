from rich import print
from sqlmodel import Session, select

from fpbase2.core.db import engine
from fpbase2.models.protein import Protein

with Session(engine) as session:
    statement = select(Protein).select_from(Protein)
    result = session.exec(statement)
    # print(result.all())

p = Protein.objects.get_or_create(name="mCherry")

print(p)
