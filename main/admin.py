from django.contrib import admin
from .models import Project, Task, TaskOrder


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_code', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'user', 'priority', 'is_done', 'deadline', 'created_at']
    list_filter = ['is_done', 'priority', 'project', 'created_at']
    search_fields = ['title', 'description', 'user__email', 'project__name']
    readonly_fields = ['id', 'datetime_done', 'created_at', 'updated_at']


@admin.register(TaskOrder)
class TaskOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'context', 'reference', 'task', 'position', 'created_at']
    list_filter = ['context', 'created_at']
    search_fields = ['user__email', 'task__title', 'reference']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user', 'context', 'reference', 'position']
