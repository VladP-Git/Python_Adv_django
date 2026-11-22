from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Task


@receiver(pre_save, sender=Task)
def track_task_status_change(sender, instance, **kwargs):
    """Запоминаем предыдущий статус задачи перед сохранением в БД."""
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            instance._old_status = old_task.status
        except Task.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Task)
def notify_owner_on_status_change(sender, instance, created, **kwargs):
    """Отправляет Email-уведомление владельцу при смене статуса или закрытии задачи."""
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status

    # Защита от повторной отправки при сохранении без изменения статуса
    if old_status is None or old_status == new_status:
        return

    if not instance.owner or not instance.owner.email:
        return

    if new_status == 'Done':
        subject = f"Task closed: {instance.title}"
        message = (
            f"Hello, {instance.owner.username}!\n\n"
            f"Your task '{instance.title}' has been marked as '{new_status}' and closed.\n"
            f"Previous status: {old_status}."
        )
    else:
        subject = f"Task status updated: {instance.title}"
        message = (
            f"Hello, {instance.owner.username}!\n\n"
            f"The status of your task '{instance.title}' has changed: {old_status} -> {new_status}.\n"
            f"Current deadline: {instance.deadline}."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.owner.email],
        fail_silently=False,
    )

    instance._old_status = new_status
