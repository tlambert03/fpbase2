from functools import partial
from random import choices

from faker import Faker
from fpbase2.models.protein import Protein
from pydantic_factories import ModelFactory

AA_LETTERS: str = "ARNDCEQGHILKMFPSTWYV"
fake = Faker()


def n_random_letters(n: int) -> str:
    return "".join(choices(AA_LETTERS, k=n))


class ProteinFactory(ModelFactory):
    __model__ = Protein

    name: str = fake.first_name
    seq = partial(n_random_letters, 200)
    chromophore = partial(n_random_letters, 3)
