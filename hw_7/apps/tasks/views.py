from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
# Импортируем новые сериализаторы и модель SubTask
from .models import Task, SubTask
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
)


# Эндпоинт для создания задачи
@api_view(['POST'])
def create_task(request):
    # Используем TaskCreateSerializer с валидацией дедлайна (Задание 4)
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Эндпоинты для списка задач и одной задачи по ID
@api_view(['GET'])
def get_tasks(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Используем TaskDetailSerializer со вложенными подзадачами (Задание 3)
    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Агрегирующий эндпоинт статистики задач
@api_view(['GET'])
def get_tasks_statistics(request):
    total_tasks = Task.objects.count()

    # Группировка и подсчет задач по каждому статусу
    status_counts_qs = Task.objects.values('status').annotate(count=Count('id'))
    tasks_by_status = {item['status']: item['count'] for item in status_counts_qs}

    # Подсчет просроченных задач (дедлайн прошел, а статус еще не 'Done')
    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now()
    ).exclude(status='Done').count()

    statistics_data = {
        'total_tasks': total_tasks,
        'tasks_by_status': tasks_by_status,
        'overdue_tasks': overdue_tasks,
    }
    return Response(statistics_data, status=status.HTTP_200_OK)


# ЗАДАНИЕ 5: Классы представлений (APIView) для SubTasks
class SubTaskListCreateView(APIView):
    """Получение списка всех подзадач и создание новой подзадачи."""

    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    """Получение, полное/частичное обновление и удаление конкретной подзадачи по ID."""

    def get(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subtask = get_object_or_404(SubTask, pk=pk)
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)