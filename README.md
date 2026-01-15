# Employee Management REST API

A production-quality REST API for managing employee records with JWT-based authentication, built with FastAPI, SQLAlchemy, and SQLite.

## Features

- **CRUD Operations**: Create, read, update, and delete employee records
- **JWT Authentication**: Secure token-based authentication for all endpoints
- **Filtering & Pagination**: Filter employees by department/role with paginated results
- **Validation**: Email uniqueness, input validation, and proper error handling
- **Testing**: Comprehensive pytest test suite with 30+ test cases
- **Documentation**: Automatic API documentation with Swagger/OpenAPI

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (json-web-token)
- **Testing**: pytest with TestClient
- **Password Hashing**: bcrypt via passlib
- **Validation**: Pydantic v2

## Project Structure

```
employee-management/
├── main.py                 # FastAPI application entry point
├── database.py            # SQLAlchemy configuration
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic request/response schemas
├── auth.py                # JWT authentication logic
├── crud.py                # Database operations
├── routes.py              # API endpoint handlers
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # pytest configuration
│   └── test_api.py        # Comprehensive test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone/Navigate to project directory**
   ```bash
   cd employee-management
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Start the development server:

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run main.py
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- **ReDoc (Alternative Docs)**: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_create_employee_success -v

# Run with coverage report
pytest --cov=. tests/
```

## Authentication

### Getting a Token

All employee endpoints require JWT authentication. First, obtain a token:

**Endpoint**: `POST /api/auth/login`

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the `Authorization` header for all requests:

```
Authorization: Bearer <access_token>
```

**Default Demo Credentials**:
- Username: `admin`
- Password: `admin123`

## API Endpoints

### Authentication

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Employees

#### Create Employee
```
POST /api/employees/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "role": "Developer"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "role": "Developer",
  "date_joined": "2024-01-15"
}
```

#### List Employees
```
GET /api/employees/?department=HR&role=Manager&page=1
Authorization: Bearer <token>
```

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "department": "Engineering",
      "role": "Developer",
      "date_joined": "2024-01-15"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

**Query Parameters**:
- `department`: Filter by department (HR, Engineering, Sales)
- `role`: Filter by role (Manager, Developer, Analyst)
- `page`: Page number (default: 1, 10 per page)

#### Get Employee by ID
```
GET /api/employees/1/
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "role": "Developer",
  "date_joined": "2024-01-15"
}
```

#### Update Employee
```
PUT /api/employees/1/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Smith",
  "department": "HR"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@example.com",
  "department": "HR",
  "role": "Developer",
  "date_joined": "2024-01-15"
}
```

#### Delete Employee
```
DELETE /api/employees/1/
Authorization: Bearer <token>
```

**Response** (204 No Content) - Empty body

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Employee retrieved/updated successfully |
| 201 | Created | Employee created successfully |
| 204 | No Content | Employee deleted successfully |
| 400 | Bad Request | Duplicate email, validation error |
| 401 | Unauthorized | Invalid/missing authentication token |
| 404 | Not Found | Employee not found |

## Error Responses

**Format**:
```json
{
  "detail": "Email already registered"
}
```

## Testing with Postman/Thunder Client

### 1. Get Authentication Token

**Method**: POST  
**URL**: `http://localhost:8000/api/auth/login`  
**Body** (raw JSON):
```json
{
  "username": "admin",
  "password": "admin123"
}
```

### 2. Create Employee

**Method**: POST  
**URL**: `http://localhost:8000/api/employees/`  
**Headers**:
```
Authorization: Bearer <token_from_step_1>
Content-Type: application/json
```
**Body** (raw JSON):
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "role": "Developer"
}
```

### 3. List Employees

**Method**: GET  
**URL**: `http://localhost:8000/api/employees/`  
**Headers**:
```
Authorization: Bearer <token_from_step_1>
```

With filters:
```
http://localhost:8000/api/employees/?department=Engineering&page=1
```

### 4. Get Specific Employee

**Method**: GET  
**URL**: `http://localhost:8000/api/employees/1/`  
**Headers**:
```
Authorization: Bearer <token_from_step_1>
```

### 5. Update Employee

**Method**: PUT  
**URL**: `http://localhost:8000/api/employees/1/`  
**Headers**:
```
Authorization: Bearer <token_from_step_1>
Content-Type: application/json
```
**Body** (raw JSON):
```json
{
  "department": "Sales",
  "role": "Manager"
}
```

### 6. Delete Employee

**Method**: DELETE  
**URL**: `http://localhost:8000/api/employees/1/`  
**Headers**:
```
Authorization: Bearer <token_from_step_1>
```

## Design Decisions

### 1. **Modular Structure**
Code is separated by responsibility: models, schemas, CRUD operations, authentication, and routes. This makes testing and maintenance easier.

### 2. **Dependency Injection**
FastAPI's `Depends()` is used for database sessions and authentication, making code testable and flexible.

### 3. **JWT Authentication**
Stateless authentication using JWT allows the API to scale horizontally without shared session storage.

### 4. **Validation at Multiple Levels**
- Pydantic schemas validate input format
- Email uniqueness checked in database
- HTTP status codes follow REST conventions

### 5. **Pagination for Large Datasets**
Lists return 10 items per page to handle large datasets efficiently without overwhelming clients.

### 6. **Comprehensive Testing**
Test suite covers:
- Happy path scenarios
- Validation errors (400 Bad Request)
- Not found errors (404)
- Authentication failures (401)
- Pagination and filtering

## Database

The API uses SQLite with SQLAlchemy ORM. Database is automatically created on first run.

**Database File**: `employees.db`

**Employee Table Schema**:
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(20),
    role VARCHAR(20),
    date_joined DATE NOT NULL DEFAULT CURRENT_DATE
);
```

## Common Issues

### 1. **Port Already in Use**
```bash
# Use different port
uvicorn main:app --port 8001
```

### 2. **Module Not Found Error**
Ensure you're in the project directory and have installed dependencies:
```bash
pip install -r requirements.txt
```

### 3. **401 Unauthorized Error**
- Ensure you're including the `Authorization: Bearer <token>` header
- Token may have expired (default: 30 minutes)
- Get a new token from `/api/auth/login`

### 4. **Email Already Registered**
Email addresses must be unique. Use a different email when creating employees.

## Performance Considerations

1. **Indexing**: Employee name and email are indexed for faster queries
2. **Pagination**: Prevents loading entire datasets into memory
3. **Connection Pooling**: SQLAlchemy handles connection management
4. **Filtering at Database Level**: Reduces data transfer

## Security Notes

**For Production**:
1. Change `SECRET_KEY` in `auth.py`
2. Use environment variables for secrets
3. Implement user database instead of hardcoded credentials
4. Use HTTPS
5. Implement rate limiting
6. Add CORS restrictions
7. Use database backups
8. Implement audit logging


