import sqlalchemy
from rich import print, traceback
from sqlmodel import Session

from fpbase2.core.db import engine
from fpbase2.models._manager import Manager
from fpbase2.models.protein import Protein

traceback.install(suppress=[sqlalchemy])

session = Session(engine)
Manager.set_session(session)
# init_db(session)
# statement = select(Protein).select_from(Protein)
# result = session.exec(statement)
# print(result.all())

p = Protein.objects.get_or_create(name="Scott")
p.switch_type = p.SwitchingType.TIMER
p.save()
p.delete()
print(p)
