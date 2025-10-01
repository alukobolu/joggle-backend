from rest_framework import serializers
from .models import Project, Task, TaskOrder, PRIORITY_CHOICES, PRIORITY_COLORS
import uuid


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'color_code', 'user', 
            'created_at', 'updated_at', 'is_default', 'task_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert UUID to string for JSON serialization"""
        data = super().to_representation(instance)
        if 'id' in data:
            data['id'] = str(data['id'])
        if 'user' in data:
            data['user'] = str(data['user'])
        return data
    
    def get_task_count(self, obj):
        """Get the count of tasks in this project"""
        return obj.tasks.count()
    
    def create(self, validated_data):
        """Create a new project for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    priority_color = serializers.ReadOnlyField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_color = serializers.CharField(source='project.color_code', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'priority_color',
            'deadline', 'suggested_todo_datetime', 'is_done', 'datetime_done',
            'project', 'project_name', 'project_color', 'user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'datetime_done', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert UUID to string for JSON serialization"""
        data = super().to_representation(instance)
        if 'id' in data:
            data['id'] = str(data['id'])
        if 'project' in data:
            data['project'] = str(data['project'])
        if 'user' in data:
            data['user'] = str(data['user'])
        return data
    
    def create(self, validated_data):
        """Create a new task for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks with simplified fields"""
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'deadline', 
            'suggested_todo_datetime', 'project'
        ]
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        """Convert UUID to string for JSON serialization"""
        data = super().to_representation(instance)
        if 'id' in data:
            data['id'] = str(data['id'])
        if 'project' in data:
            data['project'] = str(data['project'])
        return data
    
    def create(self, validated_data):
        """Create a new task for the authenticated user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'deadline', 
            'suggested_todo_datetime', 'is_done', 'project'
        ]


class ProjectTaskSerializer(serializers.ModelSerializer):
    """Serializer for projects with their tasks"""
    tasks = TaskSerializer(many=True, read_only=True)
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'color_code', 
            'created_at', 'updated_at', 'is_default', 
            'tasks', 'task_count'
        ]
    
    def to_representation(self, instance):
        """Convert UUID to string for JSON serialization"""
        # Import here to avoid circular imports
        from .views import update_expired_suggested_todo_datetime
        
        # Update expired suggested_todo_datetime for project tasks
        tasks_list = list(instance.tasks.all())
        update_expired_suggested_todo_datetime(tasks_list)
        
        data = super().to_representation(instance)
        if 'id' in data:
            data['id'] = str(data['id'])
        return data
    
    def get_task_count(self, obj):
        """Get the count of tasks in this project"""
        return obj.tasks.count()


class TaskOrderSerializer(serializers.ModelSerializer):
    """Serializer for TaskOrder model"""
    task_id = serializers.CharField(source='task.id', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskOrder
        fields = ['id', 'context', 'reference', 'task', 'task_id', 'task_title', 'position', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert UUID to string for JSON serialization"""
        data = super().to_representation(instance)
        if 'task' in data:
            data['task'] = str(data['task'])
        if 'task_id' in data:
            data['task_id'] = str(data['task_id'])
        return data


class ReorderTasksSerializer(serializers.Serializer):
    """Serializer for reordering tasks"""
    context = serializers.ChoiceField(choices=['all_tasks', 'by_project', 'today', 'by_date'])
    reference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    task_ids = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
        help_text="List of task IDs in the desired order"
    )
