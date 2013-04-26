from django.conf import settings
from django.dispatch import receiver

from . import signals, states, tasks
from .models import Task


@receiver(signals.task_pending, sender=Task)
def task_pending_handler(sender, task_id, **kwargs):
    tasks.initiate.apply_async(args=(task_id,))


@receiver(signals.task_ready, sender=Task)
def task_ready_handler(sender, task_id, **kwargs):
    tasks.schedule.apply_async(args=(task_id,))


@receiver(signals.task_success, sender=Task)
def task_success_handler(sender, task_id, **kwargs):
    handle_callback(task_id)


@receiver(signals.task_acknowledge, sender=tasks.acknowledge)
def task_acknowledge_handler(sender, task_id, **kwargs):
    handle_callback(task_id)


def handle_callback(task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        if task.parent and not task.parent.transit(states.READY):
            countdown = getattr(settings, 'ACKNOWLEDGE_COUNTDOWN', 30)
            tasks.acknowledge.apply_async(args=(task_id,), countdown=countdown)
