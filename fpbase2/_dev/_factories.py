from random import choices

from faker import Faker
from pydantic_factories import ModelFactory

from fpbase2.models.protein import Protein

AA_LETTERS: str = "ARNDCEQGHILKMFPSTWYV"
fake = Faker()


class ProteinFactory(ModelFactory):
    __model__ = Protein

    name: str = fake.first_name
    seq = lambda: "".join(choices(AA_LETTERS, k=200))
    chromophore = lambda: "".join(choices(AA_LETTERS, k=3))
