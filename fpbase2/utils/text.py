import re
import unicodedata
from collections.abc import Container, Sequence
from random import choices
from typing import Any


def slugify(value: Any, allow_unicode: bool = False) -> str:
    """Convert a `value` into a slug.

    - Convert to ASCII if 'allow_unicode' is False.
    - Convert spaces to hyphens.
    - Remove characters that aren't alphanumerics, underscores, or hyphens.
    - Convert to lowercase.
    - Strip leading and trailing whitespace.
    """

    v = str(value)
    if allow_unicode:
        v = unicodedata.normalize("NFKC", v)
    else:
        v = unicodedata.normalize("NFKD", v).encode("ascii", "ignore").decode("ascii")
    v = re.sub(r"[^\w\s-]", "", v).strip().lower()
    return re.sub(r"[-\s]+", "-", v)


def new_id(
    k: int = 5,
    opts: Sequence[str] = "ABCDEFGHJKLMNOPQRSTUVWXYZ123456789",
    existing: Container[str] = (),
) -> str:
    # in sqlite, this could be: `substr(hex(randomblob(3)), 1, 6)`
    i = 0
    while (i := i + 1) < 100:
        if (_uuid := "".join(choices(opts, k=k))) not in existing:
            return _uuid
    raise RuntimeError("Could not generate unique uuid.")  # pragma: no cover
