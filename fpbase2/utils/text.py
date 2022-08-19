import re
import unicodedata
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
