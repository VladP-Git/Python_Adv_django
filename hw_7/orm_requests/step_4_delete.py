from bootstrap import setup_django

setup_django()
from apps.tasks.models import Task

print("=== ШАГ 4: УДАЛЕНИЕ ЗАПИСЕЙ ===")
task = Task.objects.filter(title="Prepare presentation").first()
if task:
    # Удалит каскадом и подзадачи благодаря models.CASCADE
    task.delete()
    print("✅ Задача 'Prepare presentation' и её подзадачи удалены!")
else:
    print("❌ Задача не найдена.")
