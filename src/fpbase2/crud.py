# just a note to self.
# most fastapi projects have a crud.py
# i've put the query stuff in core/_query.py
from sqlmodel import Session

from fpbase2.models.protein import Protein, ProteinCreate


def create_protein(*, session: Session, protein_in: ProteinCreate) -> Protein:
    db_item = Protein.model_validate(protein_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
