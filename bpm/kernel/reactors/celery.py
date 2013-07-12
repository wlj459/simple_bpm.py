# -*- coding: utf-8 -*-
"""
bpm.kernel.reactors.celery
==========================

此模块定义了所需的 celery signal 的 handlers
"""
from __future__ import absolute_import

from celery import signals

from bpm.kernel.models import Task


@signals.task_sent.connect
def task_sent(*args, **kwargs):
    pass


@signals.task_prerun.connect
def task_prerun(*args, **kwargs):
    pass


@signals.task_postrun.connect
def task_postrun(*args, **kwargs):
    pass


@signals.task_success.connect
def task_success(*args, **kwargs):
    pass


@signals.task_failure.connect
def task_failure(**kwargs):
    """
    Celery 任务执行失败时的处理函数。
    """
    if 'args' in kwargs and kwargs['args']:
        try:
            task = Task.objects.get(pk=kwargs['args'][0])
        except Task.DoesNotExist:
            # TODO
            print 'Task Does Not Exist'
            pass
        except:
            # TODO
            import traceback
            print traceback.print_exc()
        else:
            task.complete(data=unicode(kwargs['exception']),
                          ex_data=unicode(kwargs['einfo'].traceback),
                          return_code=1)


@signals.task_revoked.connect
def task_revoked(*args, **kwargs):
    pass
