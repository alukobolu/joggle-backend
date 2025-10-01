# Todo App API Documentation

This document describes the REST API endpoints for the Todo application with projects and tasks.

## Important Notes

- **UUIDs**: All models use UUID (Universally Unique Identifier) as primary keys instead of sequential integers. UUIDs are returned as strings in JSON responses.
- **Authentication**: All endpoints require JWT authentication.
- **Auto-update**: All task GET endpoints automatically update `suggested_todo_datetime` to today if it has passed and the task is not completed. This preserves the original time while moving it to the current date.

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Base URL
```
http://localhost:8000/main/api/
```

## Projects

### Get All Projects
- **GET** `/projects/`
- Returns all projects for the authenticated user
- **Note**: If the user has no projects, a default "Personal" project is automatically created
- **Response:**
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

### Create Project
- **POST** `/projects/`
- **Body:**
```json
{
  "name": "Work Tasks",
  "description": "Work-related tasks and projects",
  "color_code": "#EF4444"
}
```

### Get Single Project
- **GET** `/projects/{uuid}/`
- Note: `{uuid}` is the UUID string of the project

### Update Project
- **PUT** `/projects/{uuid}/` or **PATCH** `/projects/{uuid}/`
- Note: `{uuid}` is the UUID string of the project

### Delete Project
- **DELETE** `/projects/{uuid}/`
- Note: `{uuid}` is the UUID string of the project

### Get Project with Tasks
- **GET** `/projects/with_tasks/`
- Returns all projects with their associated tasks

### Get Tasks for Specific Project
- **GET** `/projects/{uuid}/tasks/`
- Returns all tasks for a specific project
- Note: `{uuid}` is the UUID string of the project

## Tasks

### Get All Tasks
- **GET** `/tasks/`
- Returns all tasks for the authenticated user

### Create Task
- **POST** `/tasks/`
- **Body:**
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
- **Response:** Returns the created task with UUID
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "title": "Complete project report",
  "description": "Write the quarterly project report",
  "priority": "high",
  "deadline": "2024-01-15T17:00:00Z",
  "suggested_todo_datetime": "2024-01-14T09:00:00Z",
  "project": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Get Single Task
- **GET** `/tasks/{uuid}/`
- Note: `{uuid}` is the UUID string of the task

### Update Task
- **PUT** `/tasks/{uuid}/` or **PATCH** `/tasks/{uuid}/`
- Note: `{uuid}` is the UUID string of the task

### Delete Task
- **DELETE** `/tasks/{uuid}/`
- Note: `{uuid}` is the UUID string of the task

### Get Today's Tasks
- **GET** `/tasks/today/`
- Returns tasks scheduled for today, with today's deadline, or created today

### Get Tasks by Date
- **GET** `/tasks/by_date/?date=2024-01-15`
- Returns tasks for a specific date (YYYY-MM-DD format)

### Get Tasks by Project
- **GET** `/tasks/by_project/?project_id={uuid}`
- Returns all tasks for a specific project
- **Parameters**: `project_id` - UUID string of the project
- **Example**: `/tasks/by_project/?project_id=123e4567-e89b-12d3-a456-426614174000`

### Get Pending Tasks
- **GET** `/tasks/pending/`
- Returns all incomplete tasks

### Get Completed Tasks
- **GET** `/tasks/completed/`
- Returns all completed tasks

### Toggle Task Done Status
- **POST** `/tasks/{uuid}/toggle_done/`
- Toggles the done status of a task and automatically sets/clears datetime_done
- Note: `{uuid}` is the UUID string of the task

### Get Upcoming Deadlines
- **GET** `/tasks/upcoming_deadlines/`
- Returns tasks with deadlines in the next 7 days

### Reorder Tasks (Custom Arrangement)
- **POST** `/tasks/reorder/`
- Allows users to set custom ordering for tasks in different contexts
- **Body:**
```json
{
  "context": "all_tasks",
  "reference": "",
  "task_ids": [
    "task-uuid-1",
    "task-uuid-2",
    "task-uuid-3"
  ]
}
```
- **Context Types:**
  - `all_tasks`: Custom order for all tasks list (reference should be empty or null)
  - `by_project`: Custom order for tasks within a specific project (reference = project UUID)
  - `today`: Custom order for today's tasks (reference should be empty or null)
  - `by_date`: Custom order for tasks on a specific date (reference = date in YYYY-MM-DD format)
- **Response:**
```json
{
  "message": "Task order updated successfully",
  "context": "all_tasks",
  "reference": "",
  "tasks_ordered": 3
}
```

### Get Current Task Order
- **GET** `/tasks/get_order/?context={context}&reference={reference}`
- Returns the current custom ordering for a specific context
- **Parameters:**
  - `context` (required): One of `all_tasks`, `by_project`, `today`, `by_date`
  - `reference` (optional): Required for `by_project` (project UUID) and `by_date` (date string)
- **Example**: `/tasks/get_order/?context=by_project&reference=123e4567-e89b-12d3-a456-426614174000`
- **Response:**
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
      "task_title": "Task 1",
      "position": 0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Task Response Format

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
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
```

## Priority Levels

Tasks can have the following priority levels with associated colors:

- **low**: Green (#10B981)
- **medium**: Amber (#F59E0B) - Default
- **high**: Red (#EF4444)
- **urgent**: Dark Red (#DC2626)

## Default Project

When a new user is created, a default "Personal" project is automatically created with:
- Name: "Personal"
- Description: "Your personal tasks and todos"
- Color: Blue (#3B82F6)
- is_default: true

## Custom Task Ordering

The system supports custom ordering of tasks for different contexts. Users can manually arrange tasks in their preferred order, which will be preserved across sessions.

### How It Works

1. **Set Custom Order**: Use the `/tasks/reorder/` endpoint to define your preferred task order
2. **Automatic Application**: When retrieving tasks, the custom order is automatically applied if it exists
3. **Context-Specific**: Different orderings can be maintained for:
   - All tasks list
   - Tasks within each project
   - Today's tasks
   - Tasks for each specific date

### Order Persistence

- Custom orders are stored per user, per context
- If no custom order exists, tasks are returned in default order (most recent first)
- New tasks without a custom position appear after ordered tasks
- Deleting a task automatically removes it from all custom orders

### Example Workflow

1. Get tasks for a project:
   ```
   GET /tasks/by_project/?project_id=abc-123
   ```

2. Reorder them to your preference:
   ```
   POST /tasks/reorder/
   {
     "context": "by_project",
     "reference": "abc-123",
     "task_ids": ["task-3", "task-1", "task-2"]
   }
   ```

3. Future requests will return tasks in your custom order:
   ```
   GET /tasks/by_project/?project_id=abc-123
   Returns: [task-3, task-1, task-2, ...]
   ```

## Suggested Todo DateTime Auto-Update

The system automatically updates expired `suggested_todo_datetime` values for all task GET endpoints:

- **When**: If `suggested_todo_datetime` date is in the past and the task is not completed
- **What happens**: The date is updated to today while preserving the original time
- **Example**: If a task was suggested for "2024-01-10 09:00" and today is "2024-01-15", it becomes "2024-01-15 09:00"
- **Endpoints affected**: All task retrieval endpoints (GET /tasks/, /tasks/today/, /tasks/by_date/, etc.)
- **Purpose**: Keeps overdue suggested times relevant while maintaining the user's preferred time of day

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

- **400 Bad Request**: Invalid data or missing required parameters
- **401 Unauthorized**: Missing or invalid authentication token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Example error response:
```json
{
  "error": "Project not found"
}
```

## Example Usage

### Creating a new task in the Personal project:

1. First, get the Personal project ID:
   ```
   GET /projects/
   ```

2. Create a task:
   ```
   POST /tasks/
   {
     "title": "Buy groceries",
     "description": "Get milk, bread, and eggs",
     "priority": "medium",
     "project": "123e4567-e89b-12d3-a456-426614174000"
   }
   ```

3. Get today's tasks:
   ```
   GET /tasks/today/
   ```

4. Mark task as done:
   ```
   POST /tasks/123e4567-e89b-12d3-a456-426614174002/toggle_done/
   ```
