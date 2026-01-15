"""
Database configuration and session management.
Uses SQLAlchemy ORM with SQLite database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import os

# SQLite database URL - creates 'employees.db' 
# On Railway: uses /tmp for ephemeral storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./employees.db")

# For Railway compatibility, handle both sqlite and postgresql
if "sqlite" in DATABASE_URL:
    # Ensure SQLite works on Railway
    create_engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }
else:
    create_engine_kwargs = {}

# Create engine with SQLite
engine = create_engine(
    DATABASE_URL,
    **create_engine_kwargs
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
