from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool

from fpbase2.core.config import settings

engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
