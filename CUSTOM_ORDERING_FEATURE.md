# Custom Task Ordering Feature

## Overview
Implemented a comprehensive custom task ordering system that allows users to manually arrange tasks in their preferred order across different contexts.

## What Was Implemented

### 1. TaskOrder Model (`main/models.py`)
- New model to store custom task ordering preferences
- Fields:
  - `user`: ForeignKey to User (who owns this order)
  - `context`: Choice field (all_tasks, by_project, today, by_date)
  - `reference`: Optional reference string (project_id for by_project, date for by_date)
  - `task`: ForeignKey to Task
  - `position`: Integer representing the order position
- Unique constraint on (user, context, reference, task) to prevent duplicates
- Indexed for optimal query performance

### 2. Serializers (`main/serializers.py`)
- `TaskOrderSerializer`: For viewing task orders
- `ReorderTasksSerializer`: For validating reorder requests

### 3. Helper Functions (`main/views.py`)
- `apply_custom_ordering(tasks, user, context, reference)`: Applies custom ordering to a queryset of tasks
- `create_or_update_task_order(user, context, reference, task_ids)`: Creates or updates task order

### 4. New API Endpoints

#### Reorder Tasks
- **POST** `/tasks/reorder/`
- Allows users to set custom task order for different contexts
- Request body:
```json
{
  "context": "all_tasks|by_project|today|by_date",
  "reference": "optional_reference",
  "task_ids": ["uuid1", "uuid2", "uuid3"]
}
```

#### Get Current Order
- **GET** `/tasks/get_order/?context={context}&reference={reference}`
- Returns the current custom ordering for a context

### 5. Updated Existing Endpoints
All task retrieval endpoints now support custom ordering:
- `GET /tasks/` - Uses 'all_tasks' context
- `GET /tasks/today/` - Uses 'today' context
- `GET /tasks/by_date/` - Uses 'by_date' context with date as reference
- `GET /tasks/by_project/` - Uses 'by_project' context with project_id as reference

### 6. Admin Interface (`main/admin.py`)
- Registered TaskOrder model in Django admin
- Added TaskAdmin and ProjectAdmin for better management

### 7. Database Migration
- Created and applied migration: `0004_alter_task_options_remove_task_custom_order_and_more.py`

## How It Works

### Setting Custom Order
1. User retrieves tasks for a context (e.g., all tasks, project tasks, today's tasks)
2. User reorders tasks in their preferred arrangement
3. Frontend sends POST request to `/tasks/reorder/` with new order
4. Backend stores the order in TaskOrder model

### Retrieving Ordered Tasks
1. User requests tasks for a context
2. Backend retrieves tasks using normal filters
3. `apply_custom_ordering()` checks if custom order exists for this context
4. If custom order exists, tasks are sorted according to saved positions
5. Tasks without custom positions appear after ordered tasks (sorted by created_at)

### Order Management
- Each context maintains its own independent ordering
- Example: Project A can have different order than Project B
- Today's tasks can have different order than all tasks
- Deleting a task automatically removes it from orders (CASCADE)

## Context Types

### 1. all_tasks
- Context for the main task list
- Reference: empty string or null
- Use case: User's general task inbox

### 2. by_project
- Context for tasks within a specific project
- Reference: project UUID
- Use case: Different ordering for each project

### 3. today
- Context for today's tasks
- Reference: empty string or null
- Use case: Daily task prioritization

### 4. by_date
- Context for tasks on a specific date
- Reference: date string (YYYY-MM-DD)
- Use case: Planning tasks for specific future dates

## Example Usage

### Example 1: Reorder All Tasks
```bash
POST /tasks/reorder/
{
  "context": "all_tasks",
  "task_ids": [
    "task-uuid-3",
    "task-uuid-1",
    "task-uuid-5",
    "task-uuid-2"
  ]
}
```

### Example 2: Reorder Project Tasks
```bash
POST /tasks/reorder/
{
  "context": "by_project",
  "reference": "project-uuid-123",
  "task_ids": [
    "task-uuid-a",
    "task-uuid-b",
    "task-uuid-c"
  ]
}
```

### Example 3: Reorder Today's Tasks
```bash
POST /tasks/reorder/
{
  "context": "today",
  "task_ids": [
    "urgent-task-uuid",
    "important-task-uuid",
    "normal-task-uuid"
  ]
}
```

### Example 4: Get Current Order
```bash
GET /tasks/get_order/?context=by_project&reference=project-uuid-123

Response:
{
  "context": "by_project",
  "reference": "project-uuid-123",
  "orders": [
    {
      "id": 1,
      "task_id": "task-uuid-a",
      "task_title": "Task A",
      "position": 0
    },
    {
      "id": 2,
      "task_id": "task-uuid-b",
      "task_title": "Task B",
      "position": 1
    }
  ]
}
```

## Benefits

1. **User Control**: Users can prioritize tasks in their own way
2. **Context-Aware**: Different contexts maintain separate orderings
3. **Persistent**: Order is saved and maintained across sessions
4. **Flexible**: Works with all existing task filtering/retrieval methods
5. **Performant**: Database-level ordering with indexes for speed
6. **Automatic Cleanup**: Deleting tasks automatically removes order entries

## Technical Details

### Database Performance
- Indexed on (user, context, reference, position) for fast lookups
- Bulk operations used for creating/updating orders
- Cascade deletion ensures no orphaned order records

### Ordering Algorithm
- Uses Django's `Case/When` for database-level ordering
- Tasks with custom positions: sorted by position (ascending)
- Tasks without custom positions: sorted by created_at (descending)
- Efficient single-query execution

### Validation
- Validates context choices
- Validates references (UUID format for projects, date format for dates)
- Verifies user ownership of tasks and projects
- Handles invalid/missing task IDs gracefully

## Future Enhancements (Optional)

1. **Drag-and-drop UI**: Frontend implementation for easy reordering
2. **Bulk reorder**: Reorder multiple contexts at once
3. **Order templates**: Save and reuse common orderings
4. **Order history**: Track changes to task ordering over time
5. **Auto-ordering**: AI-suggested optimal task order based on deadlines/priority

