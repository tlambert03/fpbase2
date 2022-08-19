from fastapi import Depends, FastAPI, Query
from sqlmodel import Session, select

from fpbase2.db import create_db_and_tables, get_session
from fpbase2.models.protein import Protein, ProteinCreate, ProteinRead, ProteinUpdate

from .utils import create_object, delete_object, read_or_404, update_object

app = FastAPI()


class URL:
    ADMIN = "/admin"
    PROTEINS = "/proteins/"
    PROTEIN = "/proteins/{protein_id}"


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.post(URL.PROTEINS, response_model=ProteinRead)
def create_protein(
    *, session: Session = Depends(get_session), protein: ProteinCreate
) -> Protein:
    """Create a new protein."""
    return create_object(session, Protein, protein)


@app.get(URL.PROTEINS, response_model=list[Protein])
def read_proteins(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> list[Protein]:
    """Return all proteins in the database (paginated)."""
    return session.exec(select(Protein).offset(offset).limit(limit)).all()


@app.get(URL.PROTEIN, response_model=ProteinRead)
def read_protein(
    *, session: Session = Depends(get_session), protein_id: int
) -> Protein:
    """Return a protein by ID."""
    return read_or_404(session, Protein, protein_id)


@app.patch(URL.PROTEIN, response_model=ProteinRead)
def update_protein(
    *, session: Session = Depends(get_session), protein_id: int, protein: ProteinUpdate
) -> Protein:
    """Update a protein by ID."""
    return update_object(session, Protein, protein_id, protein)


@app.delete(URL.PROTEIN)
def delete_protein(*, session: Session = Depends(get_session), protein_id: int) -> dict:
    """Delete a protein by ID."""
    return delete_object(session, Protein, protein_id)
