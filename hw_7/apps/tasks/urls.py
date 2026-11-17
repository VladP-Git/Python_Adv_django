from django.urls import path
from . import views

urlpatterns = [
    path('tasks/create/', views.create_task, name='task-create'),
    path('tasks/', views.get_tasks, name='task-list'),
    path('tasks/<int:pk>/', views.get_task_detail, name='task-detail'),
    path('tasks/statistics/', views.get_tasks_statistics, name='task-statistics'),
]
