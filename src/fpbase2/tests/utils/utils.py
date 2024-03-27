import random
import string

AMINO_ACIDS = "ARNDCEQGHILKMFPSTWYV"


def n_random_letters(n: int, alphabet: str = string.ascii_lowercase) -> str:
    return "".join(random.choices(alphabet, k=n))


def n_random_aa(n: int) -> str:
    return n_random_letters(n, alphabet=AMINO_ACIDS)
