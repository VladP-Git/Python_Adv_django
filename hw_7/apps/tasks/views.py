from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsOwnerOrReadOnly
from .models import Category, SubTask, Task
from .serializers import (
    CategoryCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    TaskSerializer,
)
from .registration import UserRegistrationSerializer


def set_auth_cookies(response, access_token, refresh_token):
    """Вспомогательная функция для установки httpOnly cookies."""
    access_max_age = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    refresh_max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        max_age=access_max_age,
        httponly=True,
        samesite='Lax',
        secure=not settings.DEBUG,  # True на продакшене (HTTPS), False локально (HTTP)
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        max_age=refresh_max_age,
        httponly=True,
        samesite='Lax',
        secure=not settings.DEBUG,
    )


# ==========================================
# ЗАДАНИЕ 1: Регистрация пользователя
# ==========================================
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# ==========================================
# ЗАДАНИЕ 2: Вход в аккаунт и обновление токена через cookies
# ==========================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Необходимо указать username и password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Неверный логин или пароль."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "message": "Вход выполнен успешно.",
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "access": str(access),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK
        )
        set_auth_cookies(response, access, refresh)
        return response


class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Ищем refresh токен в cookies или в теле запроса
        raw_refresh = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        if not raw_refresh:
            return Response(
                {"error": "Refresh токен не найден."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            old_refresh = RefreshToken(raw_refresh)
            user_id = old_refresh.payload.get('user_id')
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.get(pk=user_id)

            # Если включена ротация и blacklist — аннулируем старый refresh и выпускаем новую пару
            if settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION', False):
                old_refresh.blacklist()

            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            response = Response(
                {
                    "message": "Токен успешно обновлён.",
                    "access": str(new_access),
                    "refresh": str(new_refresh),
                },
                status=status.HTTP_200_OK
            )
            set_auth_cookies(response, new_access, new_refresh)
            return response

        except (TokenError, Exception):
            return Response(
                {"error": "Недействительный или просроченный refresh токен."},
                status=status.HTTP_401_UNAUTHORIZED
            )


# ==========================================
# ЗАДАНИЕ 3: Выход из аккаунта (Blacklist + удаление cookies)
# ==========================================
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_refresh = request.COOKIES.get('refresh_token') or request.data.get('refresh')

        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except TokenError:
                pass  # Токен уже в blacklist или истёк

        response = Response(
            {"message": "Выход из аккаунта выполнен успешно."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return TaskDetailSerializer

class UserTasksListView(generics.ListAPIView):
    """Получение списка задач, принадлежащих текущему авторизованному пользователю."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return SubTaskSerializer


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

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
