# Custom Task Ordering - User Guide

## How It Works

Every task retrieval endpoint now automatically checks for custom ordering and applies it if it exists. If no custom order is set, tasks are returned in default order (most recent first).

## The Magic Function: `apply_custom_ordering()`

This function is called by every task retrieval endpoint. Here's what it does:

```
1. Check if custom order exists for this context
   ├─ YES → Apply user's custom order
   └─ NO  → Return tasks in default order (most recent first)
```

## Supported Endpoints

### 1. GET All Tasks (`GET /tasks/`)
- **Context**: `all_tasks`
- **Reference**: None
- **Behavior**: 
  - ✅ If custom order set → Returns tasks in your order
  - ❌ If no custom order → Returns tasks by creation date (newest first)

**Example:**
```bash
# First request (no custom order)
GET /tasks/
Response: [Task-D (newest), Task-C, Task-B, Task-A (oldest)]

# Set custom order
POST /tasks/reorder/
{
  "context": "all_tasks",
  "task_ids": ["Task-A", "Task-C", "Task-D", "Task-B"]
}

# Second request (custom order applied)
GET /tasks/
Response: [Task-A, Task-C, Task-D, Task-B]
```

### 2. GET Today's Tasks (`GET /tasks/today/`)
- **Context**: `today`
- **Reference**: None
- **Behavior**: 
  - ✅ If custom order set → Returns today's tasks in your order
  - ❌ If no custom order → Returns tasks by creation date (newest first)

**Example:**
```bash
# Set custom order for today's tasks
POST /tasks/reorder/
{
  "context": "today",
  "task_ids": ["urgent-task", "important-task", "normal-task"]
}

# Get today's tasks (custom order applied)
GET /tasks/today/
Response: [urgent-task, important-task, normal-task, ...]
```

### 3. GET Tasks by Date (`GET /tasks/by_date/?date=YYYY-MM-DD`)
- **Context**: `by_date`
- **Reference**: Date string (YYYY-MM-DD)
- **Behavior**: 
  - ✅ If custom order set for this date → Returns tasks in your order
  - ❌ If no custom order → Returns tasks by creation date (newest first)
- **Note**: Each date has its own independent ordering

**Example:**
```bash
# Set custom order for January 15
POST /tasks/reorder/
{
  "context": "by_date",
  "reference": "2024-01-15",
  "task_ids": ["task-1", "task-2", "task-3"]
}

# Get tasks for January 15 (custom order applied)
GET /tasks/by_date/?date=2024-01-15
Response: [task-1, task-2, task-3]

# Get tasks for January 16 (no custom order, returns default)
GET /tasks/by_date/?date=2024-01-16
Response: [newest-task, older-task, ...]
```

### 4. GET Tasks by Project (`GET /tasks/by_project/?project_id=UUID`)
- **Context**: `by_project`
- **Reference**: Project UUID
- **Behavior**: 
  - ✅ If custom order set for this project → Returns tasks in your order
  - ❌ If no custom order → Returns tasks by creation date (newest first)
- **Note**: Each project has its own independent ordering

**Example:**
```bash
# Set custom order for Project A
POST /tasks/reorder/
{
  "context": "by_project",
  "reference": "project-a-uuid",
  "task_ids": ["task-1", "task-2", "task-3"]
}

# Get tasks for Project A (custom order applied)
GET /tasks/by_project/?project_id=project-a-uuid
Response: [task-1, task-2, task-3]

# Get tasks for Project B (no custom order, returns default)
GET /tasks/by_project/?project_id=project-b-uuid
Response: [newest-task, older-task, ...]
```

## Flow Diagram

```
User Request: GET /tasks/
        ↓
Apply custom ordering function
        ↓
Check database: Does custom order exist?
        ↓
    ┌───┴───┐
    ↓       ↓
   YES      NO
    ↓       ↓
Order by    Order by
position    created_at DESC
    ↓       ↓
    └───┬───┘
        ↓
Return ordered tasks
```

## Complete Workflow Example

### Scenario: Ordering Project Tasks

```bash
# Step 1: Get tasks for a project (no custom order yet)
GET /tasks/by_project/?project_id=abc-123

Response:
[
  {"id": "task-5", "title": "Fifth task", "created_at": "2024-01-05"},
  {"id": "task-4", "title": "Fourth task", "created_at": "2024-01-04"},
  {"id": "task-3", "title": "Third task", "created_at": "2024-01-03"},
  {"id": "task-2", "title": "Second task", "created_at": "2024-01-02"},
  {"id": "task-1", "title": "First task", "created_at": "2024-01-01"}
]
# ✅ Returned in default order (newest first)

# Step 2: User decides to reorder tasks
POST /tasks/reorder/
{
  "context": "by_project",
  "reference": "abc-123",
  "task_ids": ["task-1", "task-3", "task-5", "task-2", "task-4"]
}

Response:
{
  "message": "Task order updated successfully",
  "context": "by_project",
  "reference": "abc-123",
  "tasks_ordered": 5
}

# Step 3: Get tasks again (custom order now applied)
GET /tasks/by_project/?project_id=abc-123

Response:
[
  {"id": "task-1", "title": "First task"},    # Position 0
  {"id": "task-3", "title": "Third task"},    # Position 1
  {"id": "task-5", "title": "Fifth task"},    # Position 2
  {"id": "task-2", "title": "Second task"},   # Position 3
  {"id": "task-4", "title": "Fourth task"}    # Position 4
]
# ✅ Returned in custom order!

# Step 4: Add a new task
POST /tasks/
{
  "title": "Sixth task",
  "project": "abc-123"
}

# Step 5: Get tasks again
GET /tasks/by_project/?project_id=abc-123

Response:
[
  {"id": "task-1", "title": "First task"},    # Position 0
  {"id": "task-3", "title": "Third task"},    # Position 1
  {"id": "task-5", "title": "Fifth task"},    # Position 2
  {"id": "task-2", "title": "Second task"},   # Position 3
  {"id": "task-4", "title": "Fourth task"},   # Position 4
  {"id": "task-6", "title": "Sixth task"}     # New task, appears after ordered tasks
]
# ✅ Custom order preserved, new task appears at the end

# Step 6: Update the order to include the new task
POST /tasks/reorder/
{
  "context": "by_project",
  "reference": "abc-123",
  "task_ids": ["task-6", "task-1", "task-3", "task-5", "task-2", "task-4"]
}

# Step 7: Get tasks again
GET /tasks/by_project/?project_id=abc-123

Response:
[
  {"id": "task-6", "title": "Sixth task"},    # Now in position 0!
  {"id": "task-1", "title": "First task"},    # Position 1
  {"id": "task-3", "title": "Third task"},    # Position 2
  {"id": "task-5", "title": "Fifth task"},    # Position 3
  {"id": "task-2", "title": "Second task"},   # Position 4
  {"id": "task-4", "title": "Fourth task"}    # Position 5
]
# ✅ New order applied!
```

## Checking Current Order

You can check what custom order is currently set for any context:

```bash
GET /tasks/get_order/?context=by_project&reference=abc-123

Response:
{
  "context": "by_project",
  "reference": "abc-123",
  "orders": [
    {
      "id": 1,
      "task_id": "task-1",
      "task_title": "First task",
      "position": 0
    },
    {
      "id": 2,
      "task_id": "task-3",
      "task_title": "Third task",
      "position": 1
    },
    ...
  ]
}
```

## Important Notes

### 1. Context Independence
Each context maintains its own separate ordering:
- `all_tasks` order is independent from `today` order
- Each project has its own order
- Each date has its own order

### 2. New Tasks
When you create a new task:
- It appears **after** all custom-ordered tasks
- Sorted by creation date with other unordered tasks
- You can reorder to include it in your custom order

### 3. Deleted Tasks
When you delete a task:
- It's automatically removed from all custom orders
- No manual cleanup needed
- Other tasks maintain their relative positions

### 4. No Order = Default Order
If you've never set a custom order for a context:
- Tasks are returned in default order (most recent first)
- This is the same behavior as before custom ordering was added

### 5. Order Persistence
Custom orders are:
- ✅ Saved in the database
- ✅ Maintained across sessions
- ✅ User-specific (each user has their own orders)
- ✅ Applied automatically on every request

## Summary

**You don't need to do anything special to use custom ordering!**

1. **Get tasks** → Automatically checks for custom order
2. **Has custom order?** → Uses it
3. **No custom order?** → Returns default order (newest first)

The system seamlessly handles both scenarios without requiring any changes to your existing API calls.

