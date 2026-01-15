"""
FastAPI route handlers for the Employee Management API.
Implements all CRUD endpoints with proper error handling and status codes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from database import get_db
from schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    TokenResponse, LoginRequest, DepartmentEnum, RoleEnum
)
from models import DepartmentEnum as ModelDepartmentEnum, RoleEnum as ModelRoleEnum
from crud import (
    create_employee, get_employee, get_employees,
    update_employee, delete_employee, employee_exists_by_email
)
from auth import (
    verify_token, create_access_token, authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(credentials: LoginRequest):
    """
    Login endpoint to obtain JWT token.
    
    Default credentials for demo:
    - username: admin
    - password: admin123
    
    Response includes access token to use in Authorization header.
    """
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(access_token=access_token)


# ============================================================================
# EMPLOYEE ENDPOINTS
# ============================================================================

@router.post("/api/employees/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, tags=["Employees"])
def create_employee_endpoint(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    Create a new employee.
    
    Returns:
    - 201 Created: Employee successfully created
    - 400 Bad Request: Validation error or duplicate email
    - 401 Unauthorized: Invalid or missing authentication token
    """
    # Check if email already exists
    if employee_exists_by_email(db, employee.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_employee = create_employee(db, employee)
    return db_employee


@router.get("/api/employees/", response_model=dict, tags=["Employees"])
def list_employees(
    department: Optional[str] = Query(None, description="Filter by department (HR, Engineering, Sales)"),
    role: Optional[str] = Query(None, description="Filter by role (Manager, Developer, Analyst)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    List all employees with optional filtering and pagination.
    
    Query Parameters:
    - department: Filter by department
    - role: Filter by role
    - page: Page number (default: 1)
    
    Returns paginated list with metadata.
    """
    # Convert string filters to enum if provided
    department_enum = None
    role_enum = None
    
    if department:
        try:
            department_enum = ModelDepartmentEnum[department.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid department. Must be one of: HR, Engineering, Sales"
            )
    
    if role:
        try:
            role_enum = ModelRoleEnum[role.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: Manager, Developer, Analyst"
            )
    
    employees, total = get_employees(
        db,
        department=department_enum,
        role=role_enum,
        page=page,
        page_size=10
    )
    
    return {
        "items": [EmployeeResponse.model_validate(emp) for emp in employees],
        "total": total,
        "page": page,
        "page_size": 10,
        "total_pages": (total + 9) // 10  # Ceiling division
    }


@router.get("/api/employees/{employee_id}/", response_model=EmployeeResponse, tags=["Employees"])
def get_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    Retrieve a specific employee by ID.
    
    Returns:
    - 200 OK: Employee found and returned
    - 404 Not Found: Employee with given ID does not exist
    - 401 Unauthorized: Invalid or missing authentication token
    """
    db_employee = get_employee(db, employee_id)
    
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    return db_employee


@router.put("/api/employees/{employee_id}/", response_model=EmployeeResponse, tags=["Employees"])
def update_employee_endpoint(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    Update an existing employee's information.
    Only provided fields will be updated (partial updates supported).
    
    Returns:
    - 200 OK: Employee successfully updated
    - 400 Bad Request: Validation error or email already in use
    - 404 Not Found: Employee with given ID does not exist
    - 401 Unauthorized: Invalid or missing authentication token
    """
    # Check if employee exists
    if not get_employee(db, employee_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # If email is being updated, check for duplicates
    if employee_update.email and employee_exists_by_email(db, employee_update.email, exclude_id=employee_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_employee = update_employee(db, employee_id, employee_update)
    return db_employee


@router.delete("/api/employees/{employee_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Employees"])
def delete_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """
    Delete an employee from the system.
    
    Returns:
    - 204 No Content: Employee successfully deleted
    - 404 Not Found: Employee with given ID does not exist
    - 401 Unauthorized: Invalid or missing authentication token
    """
    if not delete_employee(db, employee_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # 204 No Content responses don't return a body
    return None
