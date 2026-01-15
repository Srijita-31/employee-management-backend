"""
CRUD (Create, Read, Update, Delete) operations for employees.
Database interaction layer using SQLAlchemy.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Employee, DepartmentEnum, RoleEnum
from schemas import EmployeeCreate, EmployeeUpdate
from typing import Optional, List, Tuple
from datetime import date


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """
    Create a new employee in the database.
    
    Args:
        db: Database session
        employee: Employee data to create
        
    Returns:
        Created Employee object
    """
    db_employee = Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
        role=employee.role,
        date_joined=date.today()
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    """
    Retrieve a single employee by ID.
    
    Args:
        db: Database session
        employee_id: Employee ID to retrieve
        
    Returns:
        Employee object if found, None otherwise
    """
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(
    db: Session,
    department: Optional[DepartmentEnum] = None,
    role: Optional[RoleEnum] = None,
    page: int = 1,
    page_size: int = 10
) -> Tuple[List[Employee], int]:
    """
    Retrieve employees with optional filtering and pagination.
    
    Args:
        db: Database session
        department: Filter by department (optional)
        role: Filter by role (optional)
        page: Page number (1-based)
        page_size: Records per page (default: 10)
        
    Returns:
        Tuple of (employee list, total count)
    """
    query = db.query(Employee)
    
    # Apply filters
    if department:
        query = query.filter(Employee.department == department)
    if role:
        query = query.filter(Employee.role == role)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    employees = query.offset(skip).limit(page_size).all()
    
    return employees, total


def update_employee(
    db: Session,
    employee_id: int,
    employee_update: EmployeeUpdate
) -> Optional[Employee]:
    """
    Update an existing employee's information.
    Only updates fields that are provided (not None).
    
    Args:
        db: Database session
        employee_id: ID of employee to update
        employee_update: Updated employee data
        
    Returns:
        Updated Employee object if found, None otherwise
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not db_employee:
        return None
    
    # Update only provided fields
    update_data = employee_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    """
    Delete an employee from the database.
    
    Args:
        db: Database session
        employee_id: ID of employee to delete
        
    Returns:
        True if employee was deleted, False if not found
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not db_employee:
        return False
    
    db.delete(db_employee)
    db.commit()
    return True


def employee_exists_by_email(db: Session, email: str, exclude_id: Optional[int] = None) -> bool:
    """
    Check if an employee with given email already exists.
    Useful for validating email uniqueness.
    
    Args:
        db: Database session
        email: Email to check
        exclude_id: Employee ID to exclude from check (for updates)
        
    Returns:
        True if employee exists with that email, False otherwise
    """
    query = db.query(Employee).filter(Employee.email == email)
    
    if exclude_id:
        query = query.filter(Employee.id != exclude_id)
    
    return query.first() is not None
