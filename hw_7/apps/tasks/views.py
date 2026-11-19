from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task, SubTask
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    SubTaskSerializer,
    SubTaskCreateSerializer,
)


# ==========================================
# ПАГИНАТОР ДЛЯ ПОДЗАДАЧ (Задание 2)
# ==========================================
class SubTaskPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


# Эндпоинт для создания задачи
@api_view(['POST'])
def create_task(request):
    # Используем TaskCreateSerializer с валидацией дедлайна (Задание 4)
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# ЗАДАНИЕ 1: Получение списка задач с фильтром по дню недели
# ==========================================
# Эндпоинт для списка задач
@api_view(['GET'])
def get_tasks(request):
    tasks = Task.objects.all()
    weekday_param = request.query_params.get('weekday')

    if weekday_param:
        # В Django week_day: 1 = Воскресенье, 2 = Понедельник, ..., 7 = Суббота
        weekdays_map = {
            'воскресенье': 1, 'sunday': 1, '1': 1,
            'понедельник': 2, 'monday': 2, '2': 2,
            'вторник': 3, 'tuesday': 3, '3': 3,
            'среда': 4, 'wednesday': 4, '4': 4,
            'четверг': 5, 'thursday': 5, '5': 5,
            'пятница': 6, 'friday': 6, '6': 6,
            'суббота': 7, 'saturday': 7, '7': 7,
        }
        day_number = weekdays_map.get(weekday_param.strip().lower())
        if day_number:
            # Фильтруем по дню недели дедлайна (при необходимости замените на created_at__week_day)
            tasks = tasks.filter(deadline__week_day=day_number)
        else:
            return Response(
                {"error": f"Некорректный день недели: '{weekday_param}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Эндпоинт для одной задачи по ID
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



# ... остальные функции (create_task, get_task_detail, get_tasks_statistics) остаются без изменений ...

# Классы представлений (APIView) для SubTasks
# ==========================================
# ЗАДАНИЯ 2 и 3: Список подзадач с пагинацией и фильтрацией
# ==========================================
class SubTaskListCreateView(APIView):
    """Получение списка подзадач (с пагинацией и фильтрацией) и создание новой подзадачи."""

    def get(self, request):
        # Сортировка от последнего добавленного к первому (Задание 2)
        subtasks = SubTask.objects.all().order_by('-created_at')

        # Получаем параметры фильтрации из URL (Задание 3)
        task_title = request.query_params.get('task_title')
        subtask_status = request.query_params.get('status')

        # Если передано название главной задачи — фильтруем по нему
        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title)

        # Если передан статус подзадачи — фильтруем по нему
        if subtask_status:
            subtasks = subtasks.filter(status__iexact=subtask_status)

        # Применяем пагинацию (не более 5 объектов на страницу)
        paginator = SubTaskPagination()
        paginated_subtasks = paginator.paginate_queryset(subtasks, request, view=self)

        serializer = SubTaskSerializer(paginated_subtasks, many=True)
        return paginator.get_paginated_response(serializer.data)

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