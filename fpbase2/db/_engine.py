from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from fpbase2.core.config import settings

if not settings.DATABASE_URI:
    raise RuntimeError("DATABASE_URI is not set, cannot create engine")

engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
