from collections.abc import Iterator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from fpbase2.core.config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    # double check whether any of these are necessary
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# can't remember why I did this
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # it's important to evaluate all SQLModels before creating the tables
    from fpbase2 import models  # noqa F401

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
