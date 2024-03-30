import re
import secrets
import unicodedata
from collections.abc import Container, Sequence
from typing import Any

from sqlalchemy import Connection, text


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
) -> str:
    # in sqlite, this could be: `substr(hex(randomblob(3)), 1, 6)`
    return "".join(secrets.choice(opts) for _ in range(k))


def new_unique_id(
    conn: Connection | None = None, existing: Container[str] = (), tries: int = 1000
) -> str:
    if conn is None:
        if not existing:
            raise ValueError("Must provide existing uuids if no connection is given.")
        for _ in range(tries):
            if (_uuid := new_id()) not in existing:
                return _uuid
    else:
        for _ in range(tries):
            _uuid = new_id()
            result = conn.execute(
                text("SELECT 1 FROM protein WHERE uuid = :uuid"), {"uuid": _uuid}
            )
            if result.scalar() is None:
                return _uuid

    raise RuntimeError(f"Could not generate unique uuid after {tries} tries.")
