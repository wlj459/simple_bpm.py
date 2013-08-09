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

    #matt: 也就是使用set_default_scheduler
    * 如果是长任务，而且是否结束是基于轮询问的：
        在start方法内调用set_scheduler设置轮询的间隔。实现on_schedule方法，实现轮询的逻辑并在结束的时候调用complete结束轮询。

    #matt:
    * 如果是长任务，而且结束与否是基于外部回调的：（#matt: 也就是外部回调complete的api或者transition-to-ready的api）
        1) 如果外部回调会直接调用complete api并提供return_code等返回值，则不需要使用set_scheduler,也就无需实现on_schedule方法。
        2) 如果外部回调不能提供return_code等返回值，则调用transition-to-ready api,  让任务自己再被唤醒去查询结果，
           则在start方法内调用set_null_scheduler，设置轮询间隔为-1, 并实现on_schedule方法，
           去访问外部资源获取return_code，然后调用complete结束。
           这个case可以参考ijobs adapter组件的实现，其需要自己去ijobs系统取执行结果.
    """

    def __init__(self, *args, **kwargs):
        super(AbstractComponent, self).__init__(*args, **kwargs)
        self.schedule_count = 1
        self.active = True

    @abstractmethod
    def start(self):
        """
        组件被引擎调用的入口点。在此处去调用外部服务。

        * 如果外部服务是短任务，则直接在此等待外部服务返回，然后调用 :py:meth:`complete` 。
        * 如果外部服务是长任务，则不应该长时间block本方法的执行，应该调用 :py:meth:`set_scheduler` 让引擎来调度组件的on_schedule再次执行。

        start方法要么调用 :py:meth:`complete` ，要么调用 :py:meth:`set_scheduler` 。

        :return: 无返回值
        """
        raise NotImplementedError

    def __guarded_setattr__(self, key, value):
        if not key.startswith('_'):
            setattr(self, key, value)
        else:
            raise AttributeError, 'can not set _'

    def get_task_id(self):
        return self._task_id

    def set_default_scheduler(self, on_schedule):
        """
        把组件设置为基于轮询的，轮询间隔为默认的算法生成，间隔随着调用轮询次数上升而变大

        :return: 无返回值
        """
        self.set_scheduler(on_schedule, DefaultIntervalGenerator())

    def set_null_scheduler(self, on_schedule):
        self.set_scheduler(on_schedule, NullIntervalGenerator())

    def set_scheduler(self, on_schedule, interval):
        """
        把组件设置为基于轮询的，轮询间隔为固定的时间
        #matt: 实现原理，定期功能使用的是celery的倒计时任务transit_lazy
        #matt: 它在一定时间后将查询逻辑(on_schedule)置为READY，然后自己先变成成BLOCKED等待被complete
        #matt: 在一定时间后，自己被设置为READY并开始执行
        #matt: 如果on_schedule还是没有complete，则会继续下去

        :param interval: 生成一组间隔时间的（伪）生成器实例
        :return: 无返回值
        """
        assert isinstance(on_schedule, types.MethodType)
        assert self is getattr(on_schedule, 'im_self')

        self._interval = interval
        self.on_schedule = on_schedule
        self._schedule()

    #matt: 初始化后，引擎就会自动执行start，此处主要用于部署on_schedule
    def _schedule(self):
        if self.active and hasattr(self, '_interval'):
            print 'component schedule'
            try:
                task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance
            except Task.DoesNotExist:
                pass  # TODO
            else:
                #matt: 新建一个非task的额外的tasklet, 用于轮询
                self._register(stackless.tasklet(self.on_schedule)(),
                               task.name)

                # 如果有countdown，则准备下次定时轮询
                # 如果没有countdown(比如等待外部回调api的)，则直接返回False,进入BLOCKED状态
                countdown = self._interval.next()
                if countdown is not None:
                    MIN_INTERVAL = getattr(settings, 'COMPONENT_MIN_INTERVAL', DEFAULT_MIN_INTERVAL)
                    MAX_INTERVAL = getattr(settings, 'COMPONENT_MAX_INTERVAL', DEFAULT_MAX_INTERVAL)

                    if countdown < MIN_INTERVAL:
                        countdown = MIN_INTERVAL
                    elif countdown > MAX_INTERVAL:
                        countdown = MAX_INTERVAL

                    task.transit_lazy(states.READY, countdown=countdown)
                    self.schedule_count += 1

        return False


    def complete(self, data=None, ex_data=None, return_code=0):
        """
        把组件的状态置为已完成，并设置返回值。虽然本调用后面的语句仍然会被执行，但是不推荐这么做。
        调用的时机可以是 :py:meth:start 也可以是 :py:meth:on_schedule 。
        组件必须显式地调用complete，与过程不同

        :param data: 组件的返回值。调用者如果用read()方法等待，则会获得该值
        :type data: str
        :param ex_data: 组件的其他返回。用于调试
        :type ex_data: str
        :param return_code: 0表示正常，非0表示异常。异常情况由引擎接管，决定是否调用后面的任务
        :type return_code: int
        :return: 无返回值
        """
        self.active = False
        task = self._model_object()
        if task is not None:
            task.complete(data, ex_data, return_code)


class DefaultIntervalGenerator(object):

    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count ** 2


class NullIntervalGenerator(object):

    def __init__(self):
        self.count = 0

    #matt 此处没有返回。。。return None
    def next(self):
        self.count += 1

DEFAULT_MIN_INTERVAL = 10
DEFAULT_MAX_INTERVAL = 3600