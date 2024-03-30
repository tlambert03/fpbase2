from typing import Any

from sqlalchemy import Engine

# Keywords that can potentially modify the database, along with possible contexts
# that qualify their use as modifying
MODIFYING_KEYWORDS: dict[str, list[str]] = {
    "alter": ["table"],
    "create": ["database", "table", "index", "view"],
    "delete": [],
    "grant": [],
    "revoke": [],
    "commit": [],
    "rollback": [],
    "savepoint": [],
    "drop": ["database", "index", "table"],
    "insert": ["into"],
    "truncate": ["table"],
    "update": [],
}


def can_modify_database(statement: str) -> bool:
    """Return True if a SQL statement can potentially modify the database."""
    statement = statement.lower().strip()

    # Split the statement into words to analyze context
    words = statement.split()

    # Iterate through each part of the statement to check for modifying keywords
    for i, word in enumerate(words):
        if word in MODIFYING_KEYWORDS:
            # If the keyword does not require specific context,
            # it's a modifying statement
            if not (contexts := MODIFYING_KEYWORDS[word]):
                return True

            # If the keyword has specific contexts,
            # check the next part of the statement for these contexts
            if i + 1 < len(words) and words[i + 1] in contexts:
                return True

    return False


def make_engine_read_only(engine: Engine) -> None:
    """Make an SQLAlchemy engine read-only."""
    from sqlalchemy import event
    from sqlalchemy.exc import StatementError

    @event.listens_for(engine, "before_cursor_execute", retval=False)
    def before_cursor_execute(
        conn: Any, cursor: Any, statement: str, parameters: Any, *_: Any, **__: Any
    ) -> None:
        if can_modify_database(statement):
            # Raise an exception if the statement is modifying the database
            raise StatementError(
                "Database is read-only. Cannot execute.", statement, parameters, None
            )
