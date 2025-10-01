from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Case, When
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from .models import Project, Task, TaskOrder
from .serializers import (
    ProjectSerializer, TaskSerializer, TaskCreateSerializer, 
    TaskUpdateSerializer, ProjectTaskSerializer, TaskOrderSerializer,
    ReorderTasksSerializer
)


def update_expired_suggested_todo_datetime(tasks):
    """Update suggested_todo_datetime to today for tasks where it has passed"""
    today = timezone.now().date()
    tasks_to_update = []
    
    for task in tasks:
        if (task.suggested_todo_datetime and 
            task.suggested_todo_datetime.date() < today and 
            not task.is_done):
            task.suggested_todo_datetime = timezone.now().replace(
                hour=task.suggested_todo_datetime.hour,
                minute=task.suggested_todo_datetime.minute,
                second=0,
                microsecond=0
            )
            tasks_to_update.append(task)
    
    # Bulk update tasks with new suggested_todo_datetime
    if tasks_to_update:
        Task.objects.bulk_update(
            tasks_to_update, 
            ['suggested_todo_datetime'], 
            batch_size=100
        )
    
    return tasks


def apply_custom_ordering(tasks, user, context, reference=None):
    """
    Apply custom ordering to tasks based on TaskOrder model.
    
    This function checks if a custom order exists for the given context:
    - If custom order EXISTS: Returns tasks sorted by user's custom positions
    - If custom order DOES NOT EXIST: Returns tasks in default order (most recent first)
    
    Args:
        tasks: QuerySet of Task objects
        user: User object who owns the tasks
        context: Context type ('all_tasks', 'by_project', 'today', 'by_date')
        reference: Optional reference (project_id for by_project, date for by_date)
    
    Returns:
        QuerySet of tasks with custom ordering applied (if exists) or default ordering
    """
    # Normalize reference to empty string if None
    reference = reference or ''
    
    # Check if custom ordering exists for this context
    order_qs = TaskOrder.objects.filter(
        user=user,
        context=context,
        reference=reference
    ).select_related('task')
    
    # NO CUSTOM ORDER: Return tasks in default order (most recent first)
    if not order_qs.exists():
        return tasks.order_by('-created_at')
    
    # CUSTOM ORDER EXISTS: Apply user's custom ordering
    # Create a mapping of task_id to position
    order_map = {str(order.task.id): order.position for order in order_qs}
    
    # Get task IDs that are in the current queryset
    task_ids = [str(task.id) for task in tasks]
    
    # Filter order_map to only include tasks in the current queryset
    relevant_order_map = {tid: pos for tid, pos in order_map.items() if tid in task_ids}
    
    # If there are no relevant orders (all ordered tasks were deleted), return default order
    if not relevant_order_map:
        return tasks.order_by('-created_at')
    
    # Create Case/When for database-level ordering
    # Tasks with custom order come first (sorted by position: 0, 1, 2, ...)
    # Tasks without custom order come last (sorted by created_at desc)
    preserved_order = Case(
        *[When(id=uuid.UUID(tid), then=pos) for tid, pos in relevant_order_map.items()],
        default=999999  # High number to push unordered tasks to the end
    )
    
    # Apply ordering: custom position first, then creation date for ties
    ordered_tasks = tasks.order_by(preserved_order, '-created_at')
    
    return ordered_tasks


def create_or_update_task_order(user, context, reference, task_ids):
    """
    Create or update task order for a given context.
    task_ids should be a list of task IDs in the desired order.
    """
    reference = reference or ''
    
    # Delete existing orders for this context
    TaskOrder.objects.filter(
        user=user,
        context=context,
        reference=reference
    ).delete()
    
    # Create new orders
    orders_to_create = []
    for position, task_id in enumerate(task_ids):
        try:
            task_uuid = uuid.UUID(task_id)
            # Verify task belongs to user
            task = Task.objects.get(id=task_uuid, user=user)
            orders_to_create.append(
                TaskOrder(
                    user=user,
                    context=context,
                    reference=reference,
                    task=task,
                    position=position
                )
            )
        except (ValueError, TypeError, Task.DoesNotExist):
            # Skip invalid task IDs or tasks not belonging to user
            continue
    
    # Bulk create all orders
    if orders_to_create:
        TaskOrder.objects.bulk_create(orders_to_create)
    
    return len(orders_to_create)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    
    def get_queryset(self):
        """Return projects for the authenticated user, creating default project if none exist"""
        user_projects = Project.objects.filter(user=self.request.user)
        
        # If user has no projects, create a default personal project
        if not user_projects.exists():
            Project.objects.create(
                name='Personal',
                description='Your personal tasks and todos',
                color_code='#3B82F6',  # Blue color
                user=self.request.user,
                is_default=True
            )
            # Refresh the queryset to include the newly created project
            user_projects = Project.objects.filter(user=self.request.user)
        
        return user_projects
    
    def perform_create(self, serializer):
        """Create a project for the authenticated user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all tasks for a specific project"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        # Update expired suggested_todo_datetime for project tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_tasks(self, request):
        """Get all projects with their tasks, creating default project if none exist"""
        projects = self.get_queryset()  # This will automatically create default project if needed
        serializer = ProjectTaskSerializer(projects, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks"""
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    
    def get_queryset(self):
        """Return tasks for the authenticated user"""
        tasks = Task.objects.filter(user=self.request.user)
        # Update expired suggested_todo_datetime for all tasks
        update_expired_suggested_todo_datetime(list(tasks))
        return tasks
    
    def list(self, request, *args, **kwargs):
        """
        List all tasks with custom ordering applied.
        
        Query parameters:
        - is_done: Optional. Filter by completion status (true/false or 1/0)
        
        Custom ordering logic:
        - Checks if user has set a custom order for 'all_tasks' context
        - If YES: Returns tasks in user's custom order
        - If NO: Returns tasks in default order (most recent first)
        """
        tasks = self.get_queryset()
        
        # Filter by is_done if parameter is provided
        is_done_param = request.query_params.get('is_done')
        if is_done_param is not None:
            is_done_value = is_done_param.lower() in ['true', '1']
            tasks = tasks.filter(is_done=is_done_value)
        
        # Apply custom ordering for 'all_tasks' context
        # This function checks if custom order exists and applies it, or returns default order
        tasks = apply_custom_ordering(tasks, request.user, 'all_tasks')
        
        # Update expired suggested_todo_datetime for all tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Create a task for the authenticated user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get tasks for today with custom ordering applied.
        
        Query parameters:
        - is_done: Optional. Filter by completion status (true/false or 1/0)
        
        Custom ordering logic:
        - Checks if user has set a custom order for 'today' context
        - If YES: Returns tasks in user's custom order
        - If NO: Returns tasks in default order (most recent first)
        """
        today = timezone.now().date()
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        tasks = self.get_queryset().filter(
            Q(suggested_todo_datetime__date=today) |
            Q(deadline__date=today)
        ).distinct()
        
        # Filter by is_done if parameter is provided
        is_done_param = request.query_params.get('is_done')
        if is_done_param is not None:
            is_done_value = is_done_param.lower() in ['true', '1']
            tasks = tasks.filter(is_done=is_done_value)
        
        # Apply custom ordering for 'today' context
        # Checks if custom order exists, uses it; otherwise returns default order
        tasks = apply_custom_ordering(tasks, request.user, 'today')
        
        # Update expired suggested_todo_datetime for today's tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """
        Get tasks for a specific date with custom ordering applied.
        
        Query parameters:
        - date: Required. Date to filter tasks (YYYY-MM-DD format)
        - is_done: Optional. Filter by completion status (true/false or 1/0)
        
        Custom ordering logic:
        - Checks if user has set a custom order for 'by_date' context with this specific date
        - If YES: Returns tasks in user's custom order for this date
        - If NO: Returns tasks in default order (most recent first)
        """
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'Date parameter is required (YYYY-MM-DD format)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_of_day = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))
        
        tasks = self.get_queryset().filter(
            Q(suggested_todo_datetime__date=target_date) |
            Q(deadline__date=target_date) |
            Q(created_at__date=target_date)
        ).distinct()
        
        # Filter by is_done if parameter is provided
        is_done_param = request.query_params.get('is_done')
        if is_done_param is not None:
            is_done_value = is_done_param.lower() in ['true', '1']
            tasks = tasks.filter(is_done=is_done_value)
        
        # Apply custom ordering for 'by_date' context with date as reference
        # Checks if custom order exists for this specific date, uses it; otherwise returns default order
        tasks = apply_custom_ordering(tasks, request.user, 'by_date', date_str)
        
        # Update expired suggested_todo_datetime for date-specific tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        Get tasks for a specific project with custom ordering applied.
        
        Query parameters:
        - project_id: Required. UUID of the project to filter tasks
        - is_done: Optional. Filter by completion status (true/false or 1/0)
        
        Custom ordering logic:
        - Checks if user has set a custom order for 'by_project' context with this specific project
        - If YES: Returns tasks in user's custom order for this project
        - If NO: Returns tasks in default order (most recent first)
        """
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id parameter is required (UUID format)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convert string to UUID and get project
            project_uuid = uuid.UUID(project_id)
            project = Project.objects.get(id=project_uuid, user=request.user)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid UUID format for project_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        tasks = project.tasks.all()
        
        # Filter by is_done if parameter is provided
        is_done_param = request.query_params.get('is_done')
        if is_done_param is not None:
            is_done_value = is_done_param.lower() in ['true', '1']
            tasks = tasks.filter(is_done=is_done_value)
        
        # Apply custom ordering for 'by_project' context with project_id as reference
        # Checks if custom order exists for this specific project, uses it; otherwise returns default order
        tasks = apply_custom_ordering(tasks, request.user, 'by_project', project_id)
        
        # Update expired suggested_todo_datetime for project tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending (not done) tasks"""
        tasks = self.get_queryset().filter(is_done=False)
        
        # Update expired suggested_todo_datetime for pending tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed tasks"""
        tasks = self.get_queryset().filter(is_done=True)
        
        # Note: We don't update suggested_todo_datetime for completed tasks
        # as they're already done
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_done(self, request, pk=None):
        """Toggle the done status of a task"""
        task = self.get_object()
        task.is_done = not task.is_done
        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_deadlines(self, request):
        """Get tasks with upcoming deadlines (next 7 days)"""
        now = timezone.now()
        week_from_now = now + timedelta(days=7)
        
        tasks = self.get_queryset().filter(
            deadline__gte=now,
            deadline__lte=week_from_now,
            is_done=False
        ).order_by('deadline')
        
        # Update expired suggested_todo_datetime for upcoming deadline tasks
        tasks_list = list(tasks)
        update_expired_suggested_todo_datetime(tasks_list)
        
        serializer = TaskSerializer(tasks_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Reorder tasks for a specific context.
        
        Request body:
        {
            "context": "all_tasks|by_project|today|by_date",
            "reference": "optional reference (project_id for by_project, date for by_date)",
            "task_ids": ["task_id_1", "task_id_2", "task_id_3", ...]
        }
        """
        serializer = ReorderTasksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        context = serializer.validated_data['context']
        reference = serializer.validated_data.get('reference', '')
        task_ids = serializer.validated_data['task_ids']
        
        # Validate reference based on context
        if context == 'by_project':
            if not reference:
                return Response(
                    {'error': 'reference (project_id) is required for by_project context'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                # Verify project exists and belongs to user
                project_uuid = uuid.UUID(reference)
                Project.objects.get(id=project_uuid, user=request.user)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid UUID format for project_id'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Project.DoesNotExist:
                return Response(
                    {'error': 'Project not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif context == 'by_date':
            if not reference:
                return Response(
                    {'error': 'reference (date) is required for by_date context'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                datetime.strptime(reference, '%Y-%m-%d')
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create or update task order
        count = create_or_update_task_order(
            request.user,
            context,
            reference,
            task_ids
        )
        
        return Response({
            'message': 'Task order updated successfully',
            'context': context,
            'reference': reference,
            'tasks_ordered': count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_order(self, request):
        """
        Get the current task order for a specific context.
        
        Query parameters:
        - context: all_tasks|by_project|today|by_date
        - reference: optional reference (project_id for by_project, date for by_date)
        """
        context = request.query_params.get('context')
        if not context:
            return Response(
                {'error': 'context parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if context not in ['all_tasks', 'by_project', 'today', 'by_date']:
            return Response(
                {'error': 'Invalid context. Must be one of: all_tasks, by_project, today, by_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reference = request.query_params.get('reference', '')
        
        # Get task orders for this context
        orders = TaskOrder.objects.filter(
            user=request.user,
            context=context,
            reference=reference
        ).order_by('position')
        
        serializer = TaskOrderSerializer(orders, many=True)
        return Response({
            'context': context,
            'reference': reference,
            'orders': serializer.data
        })
