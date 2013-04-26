from django.conf import settings
from django.dispatch import receiver

from . import signals, states, tasks
from .models import Task


@receiver(signals.task_pending, sender=Task)
def task_pending_handler(sender, instance, **kwargs):
    tasks.initiate.apply_async(args=(instance.id,))


@receiver(signals.task_ready, sender=Task)
def task_ready_handler(sender, instance, **kwargs):
    tasks.schedule.apply_async(args=(instance.id,))


@receiver(signals.task_success, sender=Task)
def task_success_handler(sender, instance, **kwargs):
    handle_callback(instance)


@receiver(signals.task_acknowledge, sender=tasks.acknowledge)
def task_acknowledge_handler(sender, instance, **kwargs):
    handle_callback(instance)


def handle_callback(instance):
    parent = instance.parent
    if parent and not parent.state in (states.SUSPENDED,
                                       states.REVOKED) and \
            not parent.transit(states.READY):
        countdown = getattr(settings, 'ACKNOWLEDGE_COUNTDOWN', 30)
        tasks.acknowledge.apply_async(args=(instance.id,), countdown=countdown)
