# -*- coding: utf-8 -*-
"""
bpm.kernel.reactors.django
==========================

Built-in signal reactors.
#matt:
django signal的响应器，响应一般是插入一条任务到celery队列
用到signal是因为包与包之间的依赖，会造成重复引用，因此使用独立的signal处理, 解开耦合
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


#matt: 任务保存后即开始initiate初始化
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


#matt: success先来调用本方法，如果有父任务，则去唤醒父任务，如果没有唤醒，则通过acknowledge后续继续唤醒
#matt: 所以可以说，success是第一次去唤醒父任务， 而acknowledge则是用于后续的唤醒父任务
def handle_callback(instance):
    parent = instance.parent
    if parent and not parent.state == states.SUSPENDED and \
            not parent.state in states.ARCHIVE_STATES and \
            not parent.transit(states.READY):
        countdown = getattr(settings, 'ACKNOWLEDGE_COUNTDOWN', 30)
        tasks.acknowledge.apply_async(args=(instance.id,), countdown=countdown)