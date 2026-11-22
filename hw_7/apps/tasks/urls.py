from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # Аутентификация и регистрация (ДЗ 20)
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/refresh/', views.CookieTokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    # Маршруты для задач (Generic Views)
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/my/', views.UserTasksListView.as_view(), name='user-tasks-list'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail-update-delete'),
    path('tasks/statistics/', views.get_tasks_statistics, name='task-statistics'),

    # Маршруты для подзадач (Generic Views)
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask-detail-update-delete'),

    # Маршруты роутера для категорий (ViewSet)
    path('', include(router.urls)),
]
