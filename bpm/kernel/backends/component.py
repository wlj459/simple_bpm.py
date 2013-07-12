# -*- coding: utf-8 -*-
"""
bpm.kernel.backends.component
=============================
"""
import stackless
import types

from django.conf import settings

from bpm.kernel import signals, states
from bpm.kernel.models import Task
from bpm.kernel.backends import AbstractBaseTaskBackend


class AbstractComponent(AbstractBaseTaskBackend):
    """
        组件类需要继承此类
        并实现 start 方法
        如果组件调用的接口是异步的，建议使用辅助方法进行同步化
        辅助方法会提供多种轮询算法，特别对于审批、定时之类的耗时比较长的任务比较适用
    """

    def __init__(self, *args, **kwargs):
        super(AbstractComponent, self).__init__(*args, **kwargs)
        self.schedule_count = 1
        self.completed = False

    def __guarded_setattr__(self, key, value):
        if not key.startswith('_'):
            setattr(self, key, value)
        else:
            raise AttributeError, 'can not set _'

    def set_default_scheduler(self, on_schedule):
        assert isinstance(on_schedule, types.MethodType)
        assert self is getattr(on_schedule, 'im_self')

        self._interval = DefaultIntervalGenerator()
        self.on_schedule = on_schedule
        self._schedule()

    def set_scheduler(self, on_schedule, interval):
        assert isinstance(on_schedule, types.MethodType)
        assert self is getattr(on_schedule, 'im_self')

        self._interval = interval
        self.on_schedule = on_schedule
        self._schedule()

    def _schedule(self):
        if not self.completed and hasattr(self, '_interval'):
            print 'component schedule'
            try:
                task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance
            except Task.DoesNotExist:
                pass  # TODO
            else:
                self._register(stackless.tasklet(self.on_schedule)(),
                               task.name)

                MIN_INTERVAL = getattr(settings, 'COMPONENT_MIN_INTERVAL', DEFAULT_MIN_INTERVAL)
                MAX_INTERVAL = getattr(settings, 'COMPONENT_MAX_INTERVAL', DEFAULT_MAX_INTERVAL)

                countdown = self._interval.next()
                if countdown < MIN_INTERVAL:
                    countdown = MIN_INTERVAL
                elif countdown > MAX_INTERVAL:
                    countdown = MAX_INTERVAL

                task.transit_lazy(states.READY, countdown=countdown)
                self.schedule_count += 1

        return False

    def complete(self, *args, **kwargs):
        self.completed = True
        task = self._model_object()
        if task is not None:
            task.complete(*args, **kwargs)


class DefaultIntervalGenerator(object):

    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count ** 2

DEFAULT_MIN_INTERVAL = 10
DEFAULT_MAX_INTERVAL = 3600