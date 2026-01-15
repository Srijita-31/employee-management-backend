"""
Database configuration and session management.
Uses SQLAlchemy ORM with SQLite database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import os

# SQLite database URL - creates 'employees.db' in /tmp for Railway compatibility
# On local: uses project root. On Railway: uses /tmp (ephemeral storage)
db_path = os.getenv("DATABASE_URL", "sqlite:///./employees.db")
if not db_path.startswith("postgresql"):
    # Ensure SQLite uses absolute path for Railway
    if "sqlite" in db_path:
        db_path = db_path.replace("./", "/tmp/")

DATABASE_URL = db_path

# Create engine with SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency injection function for FastAPI.
    Provides database session to route handlers and closes after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
