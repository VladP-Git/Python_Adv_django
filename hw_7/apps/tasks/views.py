from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Category, SubTask, Task
from .serializers import (
    CategoryCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)

# ==========================================
# ModelViewSet для Категорий
# ==========================================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        tasks_count = category.tasks.count()
        return Response(
            {
                'id': category.id,
                'category': category.name,
                'tasks_count': tasks_count,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================
# Generic Views для Задач (Tasks)
# ==========================================
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return TaskDetailSerializer


# ==========================================
# Generic Views для Подзадач (SubTasks)
# ==========================================
class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SubTaskCreateSerializer
        return SubTaskSerializer


# ==========================================
# Агрегирующий эндпоинт статистики задач
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
