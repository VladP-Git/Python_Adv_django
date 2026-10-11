from datetime import timedelta
# Импортируем F класс для работы с полями на уровне базы данных
from django.db.models import F
from bootstrap import setup_django

setup_django()
from apps.tasks.models import Task, SubTask

print("=== ШАГ 3: ИЗМЕНЕНИЕ ЗАПИСЕЙ ===")

# 1. Изменяем статус "Prepare presentation" на "In progress"
Task.objects.filter(title="Prepare presentation").update(status="In progress")

# 2. ИСПРАВЛЕНО: Изменяем срок выполнения для "Gather information" на два дня назад ОТ ДАТЫ В ЗАДАЧЕ
SubTask.objects.filter(title="Gather information").update(deadline=F('deadline') - timedelta(days=2))

# 3. Изменяем описание для "Create slides"
SubTask.objects.filter(title="Create slides").update(description="Create and format presentation slides")

print("✅ Все изменения (включая относительный сдвиг дедлайна через F-класс) успешно внесены!")
