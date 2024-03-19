from functools import partial

from polyfactory.factories.pydantic_factory import ModelFactory
from sqlmodel import Session

from fpbase2 import crud
from fpbase2.models import Protein
from fpbase2.models.protein import ProteinCreate

from .utils import n_random_aa


class ProteinFactory(ModelFactory[ProteinCreate]):
    # __random_seed__ = 0  # deterministic tests

    seq = partial(n_random_aa, 200)
    chromophore = partial(n_random_aa, 3)

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.unique.first_name()  # type: ignore


def create_random_protein(db: Session) -> Protein:
    protein = ProteinFactory.build()
    return crud.create_protein(session=db, protein_in=protein)
