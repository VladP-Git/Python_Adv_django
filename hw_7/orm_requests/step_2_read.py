from django.utils import timezone
from bootstrap import setup_django

setup_django()
from apps.tasks.models import Task, SubTask

print("=== ШАГ 2: ЧТЕНИЕ ЗАПИСЕЙ ===")
# 1. Tasks со статусом "New"
for t in Task.objects.filter(status="New"):
    print(f"Новая задача: {t.title}")

# 2. SubTasks со статусом "Done", но просроченные
for st in SubTask.objects.filter(status="Done", deadline__lt=timezone.now()):
    print(f"Просроченная выполненная подзадача: {st.title}")
