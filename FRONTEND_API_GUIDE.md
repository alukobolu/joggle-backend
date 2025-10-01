# Joggle API - Frontend Integration Guide

Simple API reference for frontend developers. All endpoints require JWT authentication unless marked as public.

## Base URLs

- **Account:** `http://localhost:8000/account/`
- **Main API:** `http://localhost:8000/main/api/`

## Authentication Header

For protected endpoints, include:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 🔐 Authentication Endpoints

### 1. Sign Up (Public)
**POST** `/account/signup/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "firstname": "John",
  "lastname": "Doe"
}
```

**Response:**
```json
{
  "message": "User registered successfully. You can now login.",
  "user_id": "123e4567-e89b-12d3-a456-426614174001",
  "email": "user@example.com",
  "verified": true
}
```

---

### 2. Login (Public)
**POST** `/account/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "email": "user@example.com",
    "verified": true,
    "firstname": "John",
    "lastname": "Doe",
    "is_blocked": false
  }
}
```

---

### 3. Refresh Token (Public)
**POST** `/account/token/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Logout (Protected)
**POST** `/account/logout/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

### 5. Get User Profile (Protected)
**GET** `/account/profile/`

**Request:** No body required

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "email": "user@example.com",
  "firstname": "John",
  "lastname": "Doe",
  "is_blocked": false,
  "is_loggedin": true,
  "verified": true
}
```

---

### 6. Update User Profile (Protected)
**PATCH** `/account/profile/update/`

**Request:**
```json
{
  "firstname": "Jane",
  "lastname": "Smith"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "email": "user@example.com",
  "firstname": "Jane",
  "lastname": "Smith"
}
```

---

### 7. Change Password (Protected)
**POST** `/account/change-password/`

**Request:**
```json
{
  "old_password": "oldPassword123",
  "new_password": "newPassword456"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

---

### 8. Request Password Reset (Public)
**POST** `/account/request-password-reset/`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset OTP sent to your email"
}
```

---

### 9. Confirm Password Reset (Public)
**POST** `/account/confirm-password-reset/`

**Request:**
```json
{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "newSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully"
}
```

---

### 10. Get User Status (Protected)
**GET** `/account/status/`

**Request:** No body required

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174001",
  "email": "user@example.com",
  "verified": true,
  "is_loggedin": true,
  "is_blocked": false,
  "firstname": "John",
  "lastname": "Doe"
}
```

---

## 📁 Project Endpoints

### 11. Get All Projects (Protected)
**GET** `/main/api/projects/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Personal",
    "description": "Your personal tasks and todos",
    "color_code": "#3B82F6",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_default": true,
    "task_count": 5
  }
]
```

---

### 12. Create Project (Protected)
**POST** `/main/api/projects/`

**Request:**
```json
{
  "name": "Work Tasks",
  "description": "Work-related tasks and projects",
  "color_code": "#EF4444"
}
```

**Response:**
```json
{
  "id": "223e4567-e89b-12d3-a456-426614174000",
  "name": "Work Tasks",
  "description": "Work-related tasks and projects",
  "color_code": "#EF4444",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-02T10:30:00Z",
  "updated_at": "2024-01-02T10:30:00Z",
  "is_default": false,
  "task_count": 0
}
```

---

### 13. Get Single Project (Protected)
**GET** `/main/api/projects/{project_id}/`

**Request:** No body required

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Personal",
  "description": "Your personal tasks and todos",
  "color_code": "#3B82F6",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_default": true,
  "task_count": 5
}
```

---

### 14. Update Project (Protected)
**PATCH** `/main/api/projects/{project_id}/`

**Request:**
```json
{
  "name": "Updated Project Name",
  "color_code": "#10B981"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Updated Project Name",
  "description": "Your personal tasks and todos",
  "color_code": "#10B981",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T11:00:00Z",
  "is_default": true,
  "task_count": 5
}
```

---

### 15. Delete Project (Protected)
**DELETE** `/main/api/projects/{project_id}/`

**Request:** No body required

**Response:** 204 No Content

---

### 16. Get All Projects with Tasks (Protected)
**GET** `/main/api/projects/with_tasks/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Personal",
    "description": "Your personal tasks and todos",
    "color_code": "#3B82F6",
    "is_default": true,
    "task_count": 2,
    "tasks": [
      {
        "id": "323e4567-e89b-12d3-a456-426614174002",
        "title": "Buy groceries",
        "description": "Get milk, bread, and eggs",
        "priority": "medium",
        "priority_color": "#F59E0B",
        "is_done": false,
        "deadline": null,
        "suggested_todo_datetime": "2024-01-02T09:00:00Z"
      }
    ]
  }
]
```

---

### 17. Get Tasks for Specific Project (Protected)
**GET** `/main/api/projects/{project_id}/tasks/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Buy groceries",
    "description": "Get milk, bread, and eggs",
    "priority": "medium",
    "priority_color": "#F59E0B",
    "deadline": null,
    "suggested_todo_datetime": "2024-01-02T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Personal",
    "project_color": "#3B82F6",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T08:00:00Z",
    "updated_at": "2024-01-02T08:00:00Z"
  }
]
```

---

## ✅ Task Endpoints

### 18. Get All Tasks (Protected)
**GET** `/main/api/tasks/`

**Query Parameters (Optional):**
- `is_done` - Filter by completion status (values: `true`, `false`, `1`, or `0`)

**Request:** No body required

**Examples:**
- Get all tasks: `/main/api/tasks/`
- Get only completed tasks: `/main/api/tasks/?is_done=true`
- Get only incomplete tasks: `/main/api/tasks/?is_done=false`

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Complete project report",
    "description": "Write the quarterly project report",
    "priority": "high",
    "priority_color": "#EF4444",
    "deadline": "2024-01-15T17:00:00Z",
    "suggested_todo_datetime": "2024-01-14T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Work Tasks",
    "project_color": "#EF4444",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### 19. Create Task (Protected)
**POST** `/main/api/tasks/`

**Request:**
```json
{
  "title": "Complete project report",
  "description": "Write the quarterly project report",
  "priority": "high",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "project": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174002",
  "title": "Complete project report",
  "description": "Write the quarterly project report",
  "priority": "high",
  "priority_color": "#EF4444",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "is_done": false,
  "datetime_done": null,
  "project": "123e4567-e89b-12d3-a456-426614174000",
  "project_name": "Work Tasks",
  "project_color": "#EF4444",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-02T12:00:00Z",
  "updated_at": "2024-01-02T12:00:00Z"
}
```

---

### 20. Get Single Task (Protected)
**GET** `/main/api/tasks/{task_id}/`

**Request:** No body required

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174002",
  "title": "Complete project report",
  "description": "Write the quarterly project report",
  "priority": "high",
  "priority_color": "#EF4444",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "is_done": false,
  "datetime_done": null,
  "project": "123e4567-e89b-12d3-a456-426614174000",
  "project_name": "Work Tasks",
  "project_color": "#EF4444",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-02T12:00:00Z",
  "updated_at": "2024-01-02T12:00:00Z"
}
```

---

### 21. Update Task (Protected)
**PATCH** `/main/api/tasks/{task_id}/`

**Request:**
```json
{
  "title": "Updated task title",
  "priority": "urgent"
}
```

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174002",
  "title": "Updated task title",
  "description": "Write the quarterly project report",
  "priority": "urgent",
  "priority_color": "#DC2626",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "is_done": false,
  "datetime_done": null,
  "project": "123e4567-e89b-12d3-a456-426614174000",
  "project_name": "Work Tasks",
  "project_color": "#EF4444",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-02T12:00:00Z",
  "updated_at": "2024-01-02T13:00:00Z"
}
```

---

### 22. Delete Task (Protected)
**DELETE** `/main/api/tasks/{task_id}/`

**Request:** No body required

**Response:** 204 No Content

---

### 23. Toggle Task Done Status (Protected)
**POST** `/main/api/tasks/{task_id}/toggle_done/`

**Request:** No body required

**Response:**
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174002",
  "title": "Complete project report",
  "description": "Write the quarterly project report",
  "priority": "high",
  "priority_color": "#EF4444",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "is_done": true,
  "datetime_done": "2024-01-02T14:30:00Z",
  "project": "123e4567-e89b-12d3-a456-426614174000",
  "project_name": "Work Tasks",
  "project_color": "#EF4444",
  "user": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-02T12:00:00Z",
  "updated_at": "2024-01-02T14:30:00Z"
}
```

---

### 24. Get Today's Tasks (Protected)
**GET** `/main/api/tasks/today/`

**Query Parameters (Optional):**
- `is_done` - Filter by completion status (values: `true`, `false`, `1`, or `0`)

**Request:** No body required

**Examples:**
- Get all today's tasks: `/main/api/tasks/today/`
- Get only completed tasks for today: `/main/api/tasks/today/?is_done=true`
- Get only incomplete tasks for today: `/main/api/tasks/today/?is_done=false`

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Buy groceries",
    "description": "Get milk, bread, and eggs",
    "priority": "medium",
    "priority_color": "#F59E0B",
    "deadline": null,
    "suggested_todo_datetime": "2024-01-02T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Personal",
    "project_color": "#3B82F6",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T08:00:00Z",
    "updated_at": "2024-01-02T08:00:00Z"
  }
]
```

---

### 25. Get Tasks by Date (Protected)
**GET** `/main/api/tasks/by_date/?date=2024-01-15`

**Query Parameters:**
- `date` - **Required.** Date to filter tasks (format: YYYY-MM-DD)
- `is_done` - **Optional.** Filter by completion status (values: `true`, `false`, `1`, or `0`)

**Request:** No body required

**Examples:**
- Get all tasks for a date: `/main/api/tasks/by_date/?date=2024-01-15`
- Get only completed tasks for a date: `/main/api/tasks/by_date/?date=2024-01-15&is_done=true`
- Get only incomplete tasks for a date: `/main/api/tasks/by_date/?date=2024-01-15&is_done=false`

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Complete project report",
    "description": "Write the quarterly project report",
    "priority": "high",
    "priority_color": "#EF4444",
    "deadline": "2024-01-15T17:00:00Z",
    "suggested_todo_datetime": "2024-01-15T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Work Tasks",
    "project_color": "#EF4444",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T12:00:00Z",
    "updated_at": "2024-01-02T12:00:00Z"
  }
]
```

---

### 26. Get Tasks by Project (Protected)
**GET** `/main/api/tasks/by_project/?project_id=123e4567-e89b-12d3-a456-426614174000`

**Query Parameters:**
- `project_id` - **Required.** UUID of the project to filter tasks
- `is_done` - **Optional.** Filter by completion status (values: `true`, `false`, `1`, or `0`)

**Request:** No body required

**Examples:**
- Get all tasks for a project: `/main/api/tasks/by_project/?project_id=123e4567-e89b-12d3-a456-426614174000`
- Get only completed tasks for a project: `/main/api/tasks/by_project/?project_id=123e4567-e89b-12d3-a456-426614174000&is_done=true`
- Get only incomplete tasks for a project: `/main/api/tasks/by_project/?project_id=123e4567-e89b-12d3-a456-426614174000&is_done=false`

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Buy groceries",
    "description": "Get milk, bread, and eggs",
    "priority": "medium",
    "priority_color": "#F59E0B",
    "deadline": null,
    "suggested_todo_datetime": "2024-01-02T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Personal",
    "project_color": "#3B82F6",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T08:00:00Z",
    "updated_at": "2024-01-02T08:00:00Z"
  }
]
```

---

### 27. Get Pending Tasks (Protected)
**GET** `/main/api/tasks/pending/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Buy groceries",
    "description": "Get milk, bread, and eggs",
    "priority": "medium",
    "priority_color": "#F59E0B",
    "deadline": null,
    "suggested_todo_datetime": "2024-01-02T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Personal",
    "project_color": "#3B82F6",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T08:00:00Z",
    "updated_at": "2024-01-02T08:00:00Z"
  }
]
```

---

### 28. Get Completed Tasks (Protected)
**GET** `/main/api/tasks/completed/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "423e4567-e89b-12d3-a456-426614174003",
    "title": "Finish documentation",
    "description": "Complete API documentation",
    "priority": "high",
    "priority_color": "#EF4444",
    "deadline": "2024-01-01T17:00:00Z",
    "suggested_todo_datetime": "2024-01-01T09:00:00Z",
    "is_done": true,
    "datetime_done": "2024-01-01T16:30:00Z",
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Work Tasks",
    "project_color": "#EF4444",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-01T08:00:00Z",
    "updated_at": "2024-01-01T16:30:00Z"
  }
]
```

---

### 29. Get Upcoming Deadlines (Protected)
**GET** `/main/api/tasks/upcoming_deadlines/`

**Request:** No body required

**Response:**
```json
[
  {
    "id": "323e4567-e89b-12d3-a456-426614174002",
    "title": "Complete project report",
    "description": "Write the quarterly project report",
    "priority": "high",
    "priority_color": "#EF4444",
    "deadline": "2024-01-15T17:00:00Z",
    "suggested_todo_datetime": "2024-01-14T09:00:00Z",
    "is_done": false,
    "datetime_done": null,
    "project": "123e4567-e89b-12d3-a456-426614174000",
    "project_name": "Work Tasks",
    "project_color": "#EF4444",
    "user": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-02T12:00:00Z",
    "updated_at": "2024-01-02T12:00:00Z"
  }
]
```

---

### 30. Reorder Tasks (Protected)
**POST** `/main/api/tasks/reorder/`

**Request:**
```json
{
  "context": "by_project",
  "reference": "123e4567-e89b-12d3-a456-426614174000",
  "task_ids": [
    "task-uuid-3",
    "task-uuid-1",
    "task-uuid-2"
  ]
}
```

**Response:**
```json
{
  "message": "Task order updated successfully",
  "context": "by_project",
  "reference": "123e4567-e89b-12d3-a456-426614174000",
  "tasks_ordered": 3
}
```

**Context Types:**
- `all_tasks` - Custom order for all tasks list (reference should be empty)
- `by_project` - Custom order for tasks within a project (reference = project UUID)
- `today` - Custom order for today's tasks (reference should be empty)
- `by_date` - Custom order for tasks on a specific date (reference = YYYY-MM-DD)

---

### 31. Get Current Task Order (Protected)
**GET** `/main/api/tasks/get_order/?context=by_project&reference=123e4567-e89b-12d3-a456-426614174000`

**Request:** No body required

**Response:**
```json
{
  "context": "by_project",
  "reference": "123e4567-e89b-12d3-a456-426614174000",
  "orders": [
    {
      "id": 1,
      "context": "by_project",
      "reference": "123e4567-e89b-12d3-a456-426614174000",
      "task": "task-uuid-1",
      "task_id": "task-uuid-1",
      "task_title": "Complete project report",
      "position": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 📝 Important Notes

### Priority Levels
Tasks can have the following priority levels with colors:
- `low` - Green (#10B981)
- `medium` - Amber (#F59E0B) - Default
- `high` - Red (#EF4444)
- `urgent` - Dark Red (#DC2626)

### Auto-Created Default Project
When a user first creates an account, a default "Personal" project is automatically created with:
- Name: "Personal"
- Description: "Your personal tasks and todos"
- Color: Blue (#3B82F6)
- `is_default: true`

### Auto-Update of Suggested Todo DateTime
All task GET endpoints automatically update `suggested_todo_datetime` to today if it has passed and the task is not completed. The original time is preserved.

### Error Responses
All endpoints return appropriate HTTP status codes:
- `400` - Bad Request (invalid data)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (blocked account)
- `404` - Not Found
- `500` - Internal Server Error

Example error response:
```json
{
  "error": "Project not found"
}
```

---

## 🚀 Quick Start Example

```javascript
// 1. Sign up
const signupResponse = await fetch('http://localhost:8000/account/signup/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    firstname: 'John',
    lastname: 'Doe'
  })
});

// 2. Login
const loginResponse = await fetch('http://localhost:8000/account/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access, refresh } = await loginResponse.json();

// 3. Get all projects (includes auto-created "Personal" project)
const projectsResponse = await fetch('http://localhost:8000/main/api/projects/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const projects = await projectsResponse.json();

// 4. Create a task
const taskResponse = await fetch('http://localhost:8000/main/api/tasks/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Buy groceries',
    description: 'Get milk, bread, and eggs',
    priority: 'medium',
    project: projects[0].id
  })
});

// 5. Get today's tasks
const todayTasksResponse = await fetch('http://localhost:8000/main/api/tasks/today/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const todayTasks = await todayTasksResponse.json();
```

