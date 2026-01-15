"""
Pydantic schemas for request/response validation.
These schemas validate and serialize data for API endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from enum import Enum


class DepartmentEnum(str, Enum):
    """Allowed department values for API requests."""
    HR = "HR"
    ENGINEERING = "Engineering"
    SALES = "Sales"


class RoleEnum(str, Enum):
    """Allowed role values for API requests."""
    MANAGER = "Manager"
    DEVELOPER = "Developer"
    ANALYST = "Analyst"


class EmployeeCreate(BaseModel):
    """
    Schema for creating a new employee.
    Name and email are required. Department and role are optional.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Employee name")
    email: EmailStr = Field(..., description="Valid email address")
    department: Optional[DepartmentEnum] = Field(None, description="Employee department")
    role: Optional[RoleEnum] = Field(None, description="Employee role")


class EmployeeUpdate(BaseModel):
    """
    Schema for updating an employee.
    All fields are optional - only provided fields will be updated.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    department: Optional[DepartmentEnum] = None
    role: Optional[RoleEnum] = None


class EmployeeResponse(BaseModel):
    """
    Schema for API responses containing employee data.
    Includes all employee fields and is used for both list and detail endpoints.
    """
    id: int
    name: str
    email: str
    department: Optional[DepartmentEnum] = None
    role: Optional[RoleEnum] = None
    date_joined: date

    model_config = {"from_attributes": True}  # Allows conversion from SQLAlchemy ORM objects


class TokenResponse(BaseModel):
    """
    Schema for JWT token response from login endpoint.
    """
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """
    Schema for login endpoint request.
    Uses simple username/password for demo purposes.
    """
    username: str
    password: str


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    Provides consistent error format across API.
    """
    detail: str
    status_code: int
