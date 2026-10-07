from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings


class ProjectFile(models.Model):
    title = models.CharField(max_length=120, verbose_name="Название файла")
    file = models.FileField(upload_to='проекты/', verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Файл проекта"
        verbose_name_plural = "Файлы проектов"
        ordering = ['-created_at']  # От последнего к первому

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    files = models.ManyToManyField(ProjectFile, related_name='projects', blank=True, verbose_name="Файлы")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-title']  # По названию в порядке убывания
        unique_together = ('title', 'description')  # Уникальность по названию и описанию

    def __str__(self):
        return self.title

    @property
    def count_of_files(self):
        """Возвращает количество файлов для конкретного объекта Project"""
        return self.files.count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Имя тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'Новая'),
        ('In progress', 'В процессе'),
        ('Pending', 'Ожидание'),
        ('Blocked', 'Заблокирована'),
        ('Done', 'Выполнено'),
    ]

    PRIORITY_CHOICES = [
        ('Низкий', 'Низкий'),
        ('Средний', 'Средний'),
        ('Высокий', 'Высокий'),
        ('Очень высокий', 'Очень высокий'),
    ]

    title = models.CharField(
        max_length=200,
        unique=True,
        validators=[MinLengthValidator(10, message="Минимальная длина названия — 10 символов.")],
        verbose_name="Название задачи"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='New', verbose_name="Статус")
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='Средний', verbose_name="Приоритет")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name="Проект")
    tags = models.ManyToManyField(Tag, related_name='tasks', blank=True, verbose_name="Теги")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks',
                                 verbose_name="Исполнитель")

    due_date = models.DateTimeField(verbose_name="Срок выполнения (due date)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата удаления")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['due_date', 'assignee']  # Сортировка по дедлайну (от дальней к ближней) и исполнителю
        unique_together = ('title', 'project')
        # Оборачиваем в список (добавляем квадратные скобки)
        # constraints = [
        #     models.UniqueConstraint(fields=['title'], name='unique_title')
        # ]

    def __str__(self):
        return self.title



