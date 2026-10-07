from django.db import models

class Category(models.Model):
    # Добавляем unique=True, так как в задании требуется уникальность по полю 'name'
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    class Meta:
        db_table = 'task_manager_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    # Добавляем unique=True для уникальности по полю 'title'
    title = models.CharField(max_length=200, unique=True, verbose_name="Название задачи")
    description = models.TextField(blank=True, verbose_name="Описание задачи")
    categories = models.ManyToManyField(Category, related_name='tasks', verbose_name="Категории")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New', verbose_name="Статус")
    deadline = models.DateTimeField(verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'task_manager_task'
        ordering = ['-created_at']  # Сортировка по убыванию даты создания
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title


class SubTask(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    # Добавляем unique=True для уникальности по полю 'title'
    title = models.CharField(max_length=200, unique=True, verbose_name="Название подзадачи")
    description = models.TextField(blank=True, verbose_name="Описание подзадачи")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks', verbose_name="Основная задача")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New', verbose_name="Статус")
    deadline = models.DateTimeField(verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'task_manager_subtask'
        ordering = ['-created_at']  # Сортировка по убыванию даты создания
        verbose_name = 'SubTask'
        verbose_name_plural = 'SubTasks'

    def __str__(self):
        return self.title
