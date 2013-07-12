# -*- coding: utf-8 -*-
"""
bpm.kernel.reactors.django
==========================

Built-in signal reactors.
"""
from __future__ import absolute_import

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from bpm.kernel import signals, states, tasks
from bpm.kernel.models import Task


@receiver(signals.lazy_transit, sender=Task)
def lazy_transit_handler(sender, task_id, to_state, countdown, **kwargs):
    tasks.transit.apply_async(args=(task_id, to_state),
                              countdown=countdown)


@receiver(post_save, sender=Task)
def task_post_save_handler(sender, instance, created, **kwargs):
    if created:
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
    if parent and not parent.state == states.SUSPENDED and \
            not parent.state in states.ARCHIVE_STATES and \
            not parent.transit(states.READY):
        countdown = getattr(settings, 'ACKNOWLEDGE_COUNTDOWN', 30)
        tasks.acknowledge.apply_async(args=(instance.id,), countdown=countdown)