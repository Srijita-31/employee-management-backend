"""
SQLAlchemy ORM models for the database schema.
Defines the Employee table structure.
"""
from sqlalchemy import Column, Integer, String, Date, Enum as SQLEnum
from database import Base
from datetime import date
import enum


class DepartmentEnum(str, enum.Enum):
    """Allowed department values."""
    HR = "HR"
    ENGINEERING = "Engineering"
    SALES = "Sales"


class RoleEnum(str, enum.Enum):
    """Allowed role values."""
    MANAGER = "Manager"
    DEVELOPER = "Developer"
    ANALYST = "Analyst"


class Employee(Base):
    """
    Employee model representing a company employee.
    
    Attributes:
        id: Primary key, auto-generated
        name: Employee name (required)
        email: Employee email, must be unique (required)
        department: Department assignment (optional)
        role: Job role (optional)
        date_joined: Date employee was hired, auto-set to today
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    department = Column(SQLEnum(DepartmentEnum), nullable=True)
    role = Column(SQLEnum(RoleEnum), nullable=True)
    date_joined = Column(Date, default=date.today, nullable=False)
