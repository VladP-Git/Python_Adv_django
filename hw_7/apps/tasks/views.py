from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import SubTask, Task
from .serializers import (
    SubTaskCreateSerializer,
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)


# ==========================================
# ПАГИНАТОР ДЛЯ ПОДЗАДАЧ
# ==========================================
class SubTaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


# ==========================================
# ЗАДАНИЕ 1: Generic Views для Задач (Tasks)
# ==========================================
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return TaskDetailSerializer


# ==========================================
# ЗАДАНИЕ 2: Generic Views для Подзадач (SubTasks)
# ==========================================
class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    pagination_class = SubTaskPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return SubTaskSerializer


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SubTaskCreateSerializer
        return SubTaskSerializer


# ==========================================
# Агрегирующий эндпоинт статистики задач (без изменений)
# ==========================================
@api_view(['GET'])
def get_tasks_statistics(request):
    total_tasks = Task.objects.count()

    status_counts_qs = Task.objects.values('status').annotate(count=Count('id'))
    tasks_by_status = {item['status']: item['count'] for item in status_counts_qs}

    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now()
    ).exclude(status='Done').count()

    statistics_data = {
        'total_tasks': total_tasks,
        'tasks_by_status': tasks_by_status,
        'overdue_tasks': overdue_tasks,
    }
    return Response(statistics_data, status=status.HTTP_200_OK)
