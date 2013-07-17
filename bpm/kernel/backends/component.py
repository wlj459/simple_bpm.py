# -*- coding: utf-8 -*-
import stackless
import types

from django.conf import settings

from bpm.kernel import signals, states
from bpm.kernel.models import Task
from bpm.kernel.backends import AbstractBaseTaskBackend
from abc import abstractmethod


class AbstractComponent(AbstractBaseTaskBackend):
    """
    组件类需要继承此类，并实现start方法。

    * 如果是短任务：
        在start方法内调用complete结束任务
    * 如果是长任务，而且是否结束是基于轮询问的：
        在start方法内调用set_scheduler设置轮询的间隔。实现on_schedule方法，实现轮询的逻辑并在结束的时候调用complete结束轮询。
    * 如果是长任务，而且结束与否是基于外部回调的：
        在start方法内调用set_scheduler，设置轮询间隔为-1。如果外部回调会提供return_code等返回值，则无需实现on_schedule方法。
        如果外部回调无法提供return_code等返回值，则需要实现on_schedule方法，去访问外部资源获取return_code，然后调用complete结束。
    """

    def __init__(self, *args, **kwargs):
        super(AbstractComponent, self).__init__(*args, **kwargs)
        self.schedule_count = 1
        self.completed = False

    @abstractmethod
    def start(self):
        """
        组件被引擎调用的入口点。在此处去调用外部服务。

        * 如果外部服务是短任务，则直接在此等待外部服务返回，然后调用 :py:meth:`complete` 。
        * 如果外部服务是长任务，则不应该长时间block本方法的执行，应该调用 :py:meth:`set_scheduler` 让引擎来调度组件的on_schedule再次执行。

        start方法要么调用 :py:meth:`complete` ，要么调用 :py:meth:`set_scheduler` 。

        :return 无返回值
        """
        raise NotImplementedError

    def __guarded_setattr__(self, key, value):
        if not key.startswith('_'):
            setattr(self, key, value)
        else:
            raise AttributeError, 'can not set _'

    def set_default_scheduler(self, on_schedule):
        """
        把组件设置为基于轮询的，轮询间隔为默认的算法生成，间隔随着调用轮询次数上升而变大
        :return 无返回值
        """
        assert isinstance(on_schedule, types.MethodType)
        assert self is getattr(on_schedule, 'im_self')

        self._interval = DefaultIntervalGenerator()
        self.on_schedule = on_schedule
        self._schedule()

    def set_scheduler(self, on_schedule, interval):
        """
        把组件设置为基于轮询的，轮询间隔为固定的时间
        :param interval: 间隔时间，单位为秒
        :return 无返回值
        """
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

    def complete(self, data=None, ex_data=None, return_code=0):
        """
        结束组件的执行。调用的时机可以是 :py:meth:start 也可以是 :py:meth:on_schedule

        :param data: 组件的返回值。调用者如果用read()方法等待，则会获得该值
        :param ex_data: 组件的其他返回。用于调试
        :param return_code: 0表示正常，非0表示异常。异常情况由引擎接管
        :return 无返回值
        """
        self.completed = True
        task = self._model_object()
        if task is not None:
            task.complete(data, ex_data, return_code)


class DefaultIntervalGenerator(object):

    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count ** 2

DEFAULT_MIN_INTERVAL = 10
DEFAULT_MAX_INTERVAL = 3600