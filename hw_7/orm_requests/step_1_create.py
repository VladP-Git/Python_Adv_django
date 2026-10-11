from datetime import timedelta
from django.utils import timezone
from bootstrap import setup_django

setup_django()
from apps.tasks.models import Task, SubTask

print("=== ШАГ 1: СОЗДАНИЕ ЗАПИСЕЙ ===")
today = timezone.now()

task, created = Task.objects.get_or_create(
    title="Prepare presentation",
    defaults={
        "description": "Prepare materials and slides for the presentation",
        "status": "New",
        "deadline": today + timedelta(days=3)
    }
)
SubTask.objects.get_or_create(
    title="Gather information", task=task,
    defaults={"description": "Find necessary information for the presentation", "status": "New", "deadline": today + timedelta(days=2)}
)
SubTask.objects.get_or_create(
    title="Create slides", task=task,
    defaults={"description": "Create presentation slides", "status": "New", "deadline": today + timedelta(days=1)}
)
print("✅ Задача и подзадачи успешно созданы!")
