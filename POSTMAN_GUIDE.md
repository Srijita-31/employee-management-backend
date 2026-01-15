# POSTMAN/THUNDER CLIENT QUICK REFERENCE

## Authentication

### 1. Login to Get Token

**Request:**
```
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwMDAwMDAwMH0.xxxxx",
  "token_type": "bearer"
}
```

**Save the `access_token` value** - you'll use it for all subsequent requests.

---

## API Endpoints

All requests (except login) require:
```
Authorization: Bearer <access_token>
```

### CREATE EMPLOYEE

**Request:**
```
POST http://localhost:8000/api/employees/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "role": "Developer"
}
```

**Valid Departments:** HR, Engineering, Sales  
**Valid Roles:** Manager, Developer, Analyst

**Expected Response:** 201 Created
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "role": "Developer",
  "date_joined": "2024-01-15"
}
```

---

### GET ALL EMPLOYEES (with pagination & filtering)

**Request:**
```
GET http://localhost:8000/api/employees/?page=1
Authorization: Bearer <token>
```

**With Filters:**
```
GET http://localhost:8000/api/employees/?department=Engineering&role=Developer&page=1
Authorization: Bearer <token>
```

**Query Parameters:**
- `department` - Filter by department (HR, Engineering, Sales)
- `role` - Filter by role (Manager, Developer, Analyst)
- `page` - Page number (default: 1, 10 items per page)

**Expected Response:** 200 OK
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@company.com",
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

---

### GET SINGLE EMPLOYEE

**Request:**
```
GET http://localhost:8000/api/employees/1/
Authorization: Bearer <token>
```

**Expected Response:** 200 OK
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "role": "Developer",
  "date_joined": "2024-01-15"
}
```

**If not found:** 404 Not Found
```json
{
  "detail": "Employee with ID 999 not found"
}
```

---

### UPDATE EMPLOYEE

**Request:**
```
PUT http://localhost:8000/api/employees/1/
Authorization: Bearer <token>
Content-Type: application/json

{
  "department": "Sales",
  "role": "Manager"
}
```

**Notes:**
- Only send fields you want to update
- Email must be unique (if updating email)

**Expected Response:** 200 OK
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "Sales",
  "role": "Manager",
  "date_joined": "2024-01-15"
}
```

---

### DELETE EMPLOYEE

**Request:**
```
DELETE http://localhost:8000/api/employees/1/
Authorization: Bearer <token>
```

**Expected Response:** 204 No Content (empty body)

**Verify deletion:**
```
GET http://localhost:8000/api/employees/1/
Authorization: Bearer <token>
```

Will return 404 Not Found

---

## Common Error Responses

### 400 Bad Request (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### 400 Bad Request (Duplicate Email)
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized (Missing/Invalid Token)
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Employee with ID 999 not found"
}
```

---

## Test Workflow in Postman

1. **Create Login Request**
   - Method: POST
   - URL: http://localhost:8000/api/auth/login
   - Body (raw JSON):
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```
   - Click Send
   - Copy the `access_token` from response

2. **Set Global Variable for Token** (Optional but recommended)
   - In Postman, go to Collections → Variables
   - Create new variable: `token`
   - Paste the token value
   - Or: Select response → click "Bearer Token" → paste token

3. **Create Employee Request**
   - Method: POST
   - URL: http://localhost:8000/api/employees/
   - Auth Tab → Type: Bearer Token → Token: `{{token}}`
   - Body (raw JSON):
     ```json
     {
       "name": "Alice Smith",
       "email": "alice.smith@company.com",
       "department": "HR",
       "role": "Manager"
     }
     ```

4. **List Employees**
   - Method: GET
   - URL: http://localhost:8000/api/employees/
   - Auth Tab → Type: Bearer Token → Token: `{{token}}`

5. **Get Specific Employee**
   - Method: GET
   - URL: http://localhost:8000/api/employees/1/
   - Auth Tab → Type: Bearer Token

6. **Update Employee**
   - Method: PUT
   - URL: http://localhost:8000/api/employees/1/
   - Auth Tab → Type: Bearer Token
   - Body: Update fields as needed

7. **Delete Employee**
   - Method: DELETE
   - URL: http://localhost:8000/api/employees/1/
   - Auth Tab → Type: Bearer Token

---

## Swagger UI (Interactive Documentation)

While server is running, visit:
```
http://localhost:8000/docs
```

This provides:
- Interactive API documentation
- "Try it out" feature to test endpoints
- Request/response schemas
- Built-in authentication

---

## Health Check Endpoints

```
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy"
}
```

```
GET http://localhost:8000/
```

Response:
```json
{
  "message": "Employee Management API",
  "status": "running",
  "version": "1.0.0",
  "docs": "/docs"
}
```
