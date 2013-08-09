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
    '''
    #matt: 当前任务完成后要去唤醒BLOCKED中的父任务
    '''
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        if not task.ack: #matt: 如果没有ack，继续再唤醒一次
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
                #matt: 将自己注册表里的所有tasklet插入stackless队列
                backend._resume()

                #matt: 让stackless开始执行队列中的所有tasklet
                stackless.schedule()
                #matt: 执行到不能被_schedule为止，
                #matt: 理论上最多执行两次，第一次schedule自己和子任务，第二次schedule子任务
                #matt: 如果没有子任务则只有一次
                #matt: 对于组件，此处必定返回false, 也就是只执行一次
                while backend._schedule():
                    stackless.schedule()

                #matt: 在schedule后 process将自己进入BLOCKED状态，等待子task唤醒自己
                task.transit(states.BLOCKED, snapshot=pickle.dumps(backend))
                #matt: 去除内存中的微线程, 因为如果不kill掉，下一次从pickle的任务恢复时，
                #matt: 会创建新的任务，从而造成stackless里有重复tasklet
                backend._destroy()


@celery.task(ignore_result=True)
def initiate(task_id):
    #matt: 在保存任务后，创建任务实例，并置为READY状态
    #matt: 如果没有初始化，那么schedule时还要争对PENDING状态再加逻辑
    #matt: 为了让已经比较复杂的schedule逻辑尽可能简练，在这里将PENDING状态处理好，让schedule方法只管调度
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
