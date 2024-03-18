import secrets
from functools import partial

from faker import Faker
from pydantic_factories import ModelFactory

from fpbase2.models.protein import Protein

AA_LETTERS: str = "ARNDCEQGHILKMFPSTWYV"
fake = Faker()


def n_random_letters(n: int) -> str:
    return "".join(secrets.choice(AA_LETTERS) for _ in range(n))


class ProteinFactory(ModelFactory):
    __model__ = Protein

    name: str = fake.first_name
    seq = partial(n_random_letters, 200)
    chromophore = partial(n_random_letters, 3)
