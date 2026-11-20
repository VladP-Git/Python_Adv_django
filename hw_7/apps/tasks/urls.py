from django.urls import path
from . import views

urlpatterns = [
    # Маршруты для задач (Generic Views)
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail-update-delete'),
    path('tasks/statistics/', views.get_tasks_statistics, name='task-statistics'),

    # Маршруты для подзадач (Generic Views)
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask-detail-update-delete'),
]
