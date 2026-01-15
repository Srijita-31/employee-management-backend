"""
Pytest test suite for Employee Management API.
Tests cover authentication, CRUD operations, validation, and error handling.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import date

from main import app
from database import Base, get_db
from models import Employee, DepartmentEnum, RoleEnum
from auth import create_access_token

# Use in-memory SQLite database for testing with proper connection pooling
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create tables in the test database
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency to use test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_token():
    """Generate a valid JWT token for testing."""
    token = create_access_token(data={"sub": "testuser"})
    return token


@pytest.fixture
def auth_headers(valid_token):
    """Return authorization headers with valid token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_login_success():
    """Test successful login with correct credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login fails with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_missing_username():
    """Test login fails when username is missing."""
    response = client.post(
        "/api/auth/login",
        json={"password": "admin123"}
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# EMPLOYEE CREATION TESTS
# ============================================================================

def test_create_employee_success(auth_headers):
    """Test successful employee creation."""
    response = client.post(
        "/api/employees/",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "department": "Engineering",
            "role": "Developer"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["department"] == "Engineering"
    assert data["role"] == "Developer"
    assert "id" in data
    assert data["date_joined"] == str(date.today())


def test_create_employee_minimal(auth_headers):
    """Test employee creation with only required fields."""
    response = client.post(
        "/api/employees/",
        json={
            "name": "Jane Smith",
            "email": "jane@example.com"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert data["department"] is None
    assert data["role"] is None


def test_create_employee_duplicate_email(auth_headers):
    """Test that duplicate email returns 400 Bad Request."""
    # Create first employee
    client.post(
        "/api/employees/",
        json={
            "name": "John Doe",
            "email": "john@example.com"
        },
        headers=auth_headers
    )
    
    # Try to create second employee with same email
    response = client.post(
        "/api/employees/",
        json={
            "name": "Jane Doe",
            "email": "john@example.com"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_create_employee_empty_name(auth_headers):
    """Test that empty name returns validation error."""
    response = client.post(
        "/api/employees/",
        json={
            "name": "",
            "email": "john@example.com"
        },
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_create_employee_invalid_email(auth_headers):
    """Test that invalid email returns validation error."""
    response = client.post(
        "/api/employees/",
        json={
            "name": "John Doe",
            "email": "invalid-email"
        },
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


def test_create_employee_no_auth():
    """Test that creating employee without auth token fails."""
    response = client.post(
        "/api/employees/",
        json={
            "name": "John Doe",
            "email": "john@example.com"
        }
    )
    assert response.status_code == 401  # Unauthorized (missing credentials)


# ============================================================================
# EMPLOYEE RETRIEVAL TESTS
# ============================================================================

def test_get_employee_success(auth_headers):
    """Test retrieving a single employee."""
    # Create employee first
    create_response = client.post(
        "/api/employees/",
        json={"name": "John Doe", "email": "john@example.com"},
        headers=auth_headers
    )
    employee_id = create_response.json()["id"]
    
    # Retrieve employee
    response = client.get(
        f"/api/employees/{employee_id}/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_id
    assert data["name"] == "John Doe"


def test_get_employee_not_found(auth_headers):
    """Test that getting non-existent employee returns 404."""
    response = client.get(
        "/api/employees/9999/",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_employees_empty(auth_headers):
    """Test listing employees when none exist."""
    response = client.get(
        "/api/employees/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


def test_list_employees_pagination(auth_headers):
    """Test employee listing with pagination."""
    # Create 15 employees
    for i in range(15):
        client.post(
            "/api/employees/",
            json={
                "name": f"Employee {i}",
                "email": f"emp{i}@example.com"
            },
            headers=auth_headers
        )
    
    # Get first page (should have 10)
    response = client.get(
        "/api/employees/?page=1",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["total_pages"] == 2
    
    # Get second page (should have 5)
    response = client.get(
        "/api/employees/?page=2",
        headers=auth_headers
    )
    data = response.json()
    assert len(data["items"]) == 5


def test_list_employees_filter_by_department(auth_headers):
    """Test filtering employees by department."""
    # Create employees in different departments
    client.post(
        "/api/employees/",
        json={
            "name": "John",
            "email": "john@example.com",
            "department": "HR"
        },
        headers=auth_headers
    )
    client.post(
        "/api/employees/",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "department": "Engineering"
        },
        headers=auth_headers
    )
    
    # Filter by HR
    response = client.get(
        "/api/employees/?department=HR",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["department"] == "HR"


def test_list_employees_filter_by_role(auth_headers):
    """Test filtering employees by role."""
    # Create employees with different roles
    client.post(
        "/api/employees/",
        json={
            "name": "John",
            "email": "john@example.com",
            "role": "Manager"
        },
        headers=auth_headers
    )
    client.post(
        "/api/employees/",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "role": "Developer"
        },
        headers=auth_headers
    )
    
    # Filter by Developer
    response = client.get(
        "/api/employees/?role=Developer",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["role"] == "Developer"


# ============================================================================
# EMPLOYEE UPDATE TESTS
# ============================================================================

def test_update_employee_success(auth_headers):
    """Test successful employee update."""
    # Create employee
    create_response = client.post(
        "/api/employees/",
        json={"name": "John Doe", "email": "john@example.com"},
        headers=auth_headers
    )
    employee_id = create_response.json()["id"]
    
    # Update employee
    response = client.put(
        f"/api/employees/{employee_id}/",
        json={"name": "John Smith", "department": "HR"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["department"] == "HR"
    assert data["email"] == "john@example.com"  # Unchanged


def test_update_employee_not_found(auth_headers):
    """Test updating non-existent employee returns 404."""
    response = client.put(
        "/api/employees/9999/",
        json={"name": "Updated Name"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_update_employee_duplicate_email(auth_headers):
    """Test that updating to duplicate email returns 400."""
    # Create two employees
    client.post(
        "/api/employees/",
        json={"name": "John", "email": "john@example.com"},
        headers=auth_headers
    )
    response2 = client.post(
        "/api/employees/",
        json={"name": "Jane", "email": "jane@example.com"},
        headers=auth_headers
    )
    jane_id = response2.json()["id"]
    
    # Try to update Jane's email to John's email
    response = client.put(
        f"/api/employees/{jane_id}/",
        json={"email": "john@example.com"},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


# ============================================================================
# EMPLOYEE DELETE TESTS
# ============================================================================

def test_delete_employee_success(auth_headers):
    """Test successful employee deletion returns 204 No Content."""
    # Create employee
    create_response = client.post(
        "/api/employees/",
        json={"name": "John Doe", "email": "john@example.com"},
        headers=auth_headers
    )
    employee_id = create_response.json()["id"]
    
    # Delete employee
    response = client.delete(
        f"/api/employees/{employee_id}/",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify employee is deleted
    get_response = client.get(
        f"/api/employees/{employee_id}/",
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_employee_not_found(auth_headers):
    """Test deleting non-existent employee returns 404."""
    response = client.delete(
        "/api/employees/9999/",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_employee_no_auth():
    """Test that deleting employee without auth token fails."""
    response = client.delete("/api/employees/1/")
    assert response.status_code == 401


# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_health_check():
    """Test API health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test API root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
