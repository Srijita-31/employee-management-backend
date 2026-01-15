"""
Database configuration and session management.
Uses SQLAlchemy ORM with SQLite database.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator

# SQLite database URL - creates 'employees.db' in project root
DATABASE_URL = "sqlite:///./employees.db"

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
