from django.contrib import admin
from .models import Category, Task, SubTask


# ЗАДАНИЕ 3: Кастомный action для Подзадач
@admin.action(description="Перевести выбранные подзадачи в статус Done")
def set_subtasks_done(modeladmin, request, queryset):
    updated_count = queryset.update(status='Done')
    modeladmin.message_user(
        request,
        f"Статус 'Done' успешно установлен для {updated_count} подзадач(и)."
    )


# ЗАДАНИЕ 1: Настройка инлайн-форм для Задач
class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1  # Количество пустых форм для новых подзадач на странице задачи
    fields = ('title', 'description', 'status', 'deadline')

# Регистрация моделей в админ-панели
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # ЗАДАНИЕ 2: Выводим метод short_title вместо полного поля title
    list_display = ('id', 'short_title', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)

    # Подключаем инлайн-форму подзадач (Задание 1)
    inlines = [SubTaskInline]

    # Сокращение названия в списке до 10 символов (Задание 2)
    @admin.display(ordering='title', description='Название задачи')
    def short_title(self, obj):
        if len(obj.title) > 10:
            return f"{obj.title[:10]}..."
        return obj.title


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'task', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'task')
    search_fields = ('title', 'description')

    # Регистрируем action перевода в статус Done (Задание 3)
    actions = [set_subtasks_done]
