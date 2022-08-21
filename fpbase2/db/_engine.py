from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()


DEBUG = os.getenv("DEBUG", "0") != "0"
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")

engine = create_engine(
    DATABASE_URL, echo=DEBUG, connect_args={"check_same_thread": False}
)
