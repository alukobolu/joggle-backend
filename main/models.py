from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

# Priority choices for tasks
PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

# Priority colors
PRIORITY_COLORS = {
    'low': '#10B981',      # Green
    'medium': '#F59E0B',   # Amber
    'high': '#EF4444',     # Red
    'urgent': '#DC2626',   # Dark Red
}

class Project(models.Model):
    """Project model for organizing tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)  # For personal project

    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Ensure only one default project per user
        if self.is_default:
            Project.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Task(models.Model):
    """Task model for individual todo items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(blank=True, null=True)
    suggested_todo_datetime = models.DateTimeField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    datetime_done = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    def save(self, *args, **kwargs):
        # Set datetime_done when task is marked as done
        if self.is_done and not self.datetime_done:
            self.datetime_done = timezone.now()
        elif not self.is_done and self.datetime_done:
            self.datetime_done = None
        super().save(*args, **kwargs)

    @property
    def priority_color(self):
        """Get the color code for the task priority"""
        return PRIORITY_COLORS.get(self.priority, '#6B7280')  # Default gray


# Context choices for task ordering
ORDER_CONTEXT_CHOICES = [
    ('all_tasks', 'All Tasks'),
    ('by_project', 'By Project'),
    ('today', 'Today'),
    ('by_date', 'By Date'),
]


class TaskOrder(models.Model):
    """Model to store custom task ordering for different contexts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_orders')
    context = models.CharField(max_length=20, choices=ORDER_CONTEXT_CHOICES)
    # Reference ID: project_id for by_project, date string (YYYY-MM-DD) for by_date, null for all_tasks/today
    reference = models.CharField(max_length=100, blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='order_positions')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'context', 'reference', 'task']
        ordering = ['position']
        indexes = [
            models.Index(fields=['user', 'context', 'reference', 'position']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.context} - {self.reference} - Task: {self.task.title} (pos: {self.position})"