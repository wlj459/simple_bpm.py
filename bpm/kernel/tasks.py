# -*- coding: utf-8 -*-
"""
bpm.kernel.tasks
================

此模块定义了所有 bpm.kernel 模块的 celery 任务
"""
import celery
import cPickle as pickle
import json
import stackless
import importlib
import logging

from . import signals, states, sandbox
from .models import Task

LOGGER = logging.getLogger(__name__)

@celery.task(ignore_result=True)
def acknowledge(task_id):

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        if not task.ack:
            signal.task_acknowledge.send(sender=acknowledge, instance=task)


@celery.task(ignore_result=True)
def schedule(task_id):

    try:
        task = Task.objects.get(pk=task_id, state=states.READY)
    except Task.DoesNotExist:
        pass
    else:
        if task.transit(states.RUNNING):
            with sandbox.enter_context():
                backend = pickle.loads(str(task.snapshot))
                backend._resume()

                stackless.schedule()
                while backend._schedule():
                    stackless.schedule()

                task.transit(states.BLOCKED, snapshot=pickle.dumps(backend))
                backend._destroy()


@celery.task(ignore_result=True)
def initiate(task_id):
    try:
        task = Task.objects.get(pk=task_id, state=states.PENDING)
    except Task.DoesNotExist:
        pass
    else:
        with sandbox.enter_context():
            cls = sandbox.load_task_class(task.name)
            backend = cls(task.pk, task.name)

            args = []
            if task.args:
                args = json.loads(task.args)

            kwargs = {}
            if task.kwargs:
                kwargs = json.loads(task.kwargs)

            backend._initiate(*args, **kwargs)
            task.transit(states.READY, snapshot=pickle.dumps(backend))
            backend._destroy()


@celery.task(ignore_result=True)
def transit(task_id, to_state):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        Task.objects.transit(task, to_state)
