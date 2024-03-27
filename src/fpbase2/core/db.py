from collections.abc import Iterator

from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from fpbase2.core.config import settings

# The `engine` is the core interface to the database,
# responsible for managing the connection pool and serving as the gateway for
# executing SQL commands. It translates high-level SQLAlchemy commands into
# database-specific SQL and routes them to the database, returning results.
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    # Allow sqlite connections to be used across threads
    connect_args={"check_same_thread": False} if settings.DB_SQLITE_PATH else {},
    # The StaticPool class is designed for situations where you need a simple
    # connection pool that maintains a single connection for all requests.
    # This pool does not support multiple connections and does not close the
    # connection until the process ends.
    poolclass=StaticPool if settings.DB_SQLITE_PATH else None,
)


def get_session() -> Iterator[Session]:
    """Yield a session to the caller, and close it when the caller is done.

    A Session manages a "unit of work" with the database. It tracks all changes
    to any objects associated with it and flushes changes to the database at the
    appropriate time. It also provides a transactional scope for the changes.

    This function is usually used with dependency injection to provide a session.
    """
    with Session(engine) as session:
        yield session


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # it's important to evaluate all SQLModels before creating the tables
    import fpbase2.models  # noqa F401

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)
