from django.utils import timezone
from rest_framework import serializers
from .models import Category, Task, SubTask


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']


# Базовый сериализатор для отображения подзадач (используется во вложенности и вьюхах)
class SubTaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

class SubTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # Явно переопределяем поле created_at как доступное только для чтения
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дата дедлайна не может быть в прошлом.")
        return value


class CategoryCreateSerializer(serializers.ModelSerializer):
    # Отключаем встроенный UniqueValidator DRF, чтобы проверка сработала внутри create/update
    name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = Category
        fields = ['id', 'name']

    def create(self, validated_data):
        name = validated_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        # Исключаем саму обновляемую запись (exclude pk), чтобы можно было сохранить её без изменения имени
        if Category.objects.filter(name__iexact=name).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"name": "Категория с таким названием уже существует."})
        instance.name = name
        instance.save()
        return instance


class TaskDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # Вкладываем SubTaskSerializer по имени обратной связи related_name='subtasks'
    subtasks = SubTaskSerializer(many=True, read_only=True)
    # Вкладываем сериализатор категорий
    categories = CategoryCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'categories', 'status', 'deadline', 'created_at', 'subtasks', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

# Валидация данных в сериализаторах
class TaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'categories', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дата дедлайна не может быть в прошлом.")
        return value
