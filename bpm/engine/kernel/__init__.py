from django.db.models.signals import post_save
from django.dispatch import receiver

from . import signals, tasks
from .models import Task


@receiver(signals.post_callback, sender=Task)
def task_post_callback_handler(sender, instance, **kwargs):
    tasks.callback.apply_async(args=(instance.pk,))


@receiver(signals.post_errback, sender=Task)
def task_post_errback_handler(sender, instance, **kwargs):
    tasks.errback.apply_async(args=(instance.pk,))


@receiver(post_save, sender=Task)
def task_post_save_handler(sender, instance, **kwargs):
    tasks.start.apply_async(args=(instance.pk,))
