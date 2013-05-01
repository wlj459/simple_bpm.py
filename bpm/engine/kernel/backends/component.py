# coding=utf-8
"""
bpm.engine.kernel.backends.process
==================================
"""
import json
import stackless

from .. import signals, states
from django.db import transaction
from ..models import Task
from .base import BaseTaskBackend
from ..utils import generate_salt


class BaseComponent(BaseTaskBackend):
    """
        组件类需要继承此类
        并实现 start 方法
        如果组件调用的接口是异步的，建议使用辅助方法进行同步化
        辅助方法会提供多种轮询算法，特别对于审批、定时之类的耗时比较长的任务比较适用
    """

    def __init__(self, *args, **kwargs):
        super(BaseComponent, self).__init__(*args, **kwargs)
        self.result = None
        self.task = None
        self.countdown = 0
        self.schedule_count = 1
        self.callback_flag = False

    def start(self, *args, **kwargs):
        """
        start方法需要组件开发者实现, 如cc接口调用， 如果没有设置self.enable_schedule=True，
        则返回的值会直接作为组件的结果进行 callback(celery task)
        """
        raise NotImplementedError

    def scheduler(self, algorithm=None,*args, **kwargs):
        """
            组件开发者如果需要对异步接口进行同步的话，可以使用该方法，
            这个方法会调用用户传递的一个处理方法来进行

            e.g:
            def on_schedule():
                result = async__peek()
                if result['return'] == 0:
                    self.callback(result)
                elif result['return'] = 3:
                    self.errback(result)

            def start():
                # do something
                self.sid = async_api_call()
                self.algorithm_init(init_countdown=10)
                self.algorithm = simple_schedule_algorithm
                scheduler()
        """

        # delay
        #
        if algorithm is None:
            self.algorithm = self.simple_schedule_algorithm
        else:
            self.algorithm = algorithm
        self._schedule()

    def algorithm_init(self, init_countdown=0, step=0, count=1):
        self.countdown = init_countdown
        self.step = step
        self.schedule_count = count

    def _schedule(self, *args, **kwargs):
        return False
        if self.callback_flag:
            return False

        try:
            task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance
        except Task.DoesNotExist:
            pass  # TODO
        else:
            self.algorithm()
            self._register(stackless.tasklet(self.on_schedule)(*args, **kwargs),
                           task.name)
            task.transit_lazy(states.READY, countdown=self.countdown)
            self.schedule_count += 1

        return False

    def callback(self, data):
        """success的通知"""
        print "CALLBACK"
        self.callback_flag = True
        try:
            task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance, 免得每次这样搞

        except Task.DoesNotExist:
            pass  # TODO
        else:
            task.callback(data)

    def errback(self, ex_data):
        """error时的通知"""
        self.callback_flag = True
        try:
            task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance, 免得每次这样搞
        except Task.DoesNotExist:
            pass  # TODO
        else:
            task.errback(ex_data)

    def on_schedule(self):
        raise NotImplementedError

    def simple_schedule_algorithm(self):
        """使用固定的countdown"""
        pass

    def multiplication_algorithm(self):
        """等值倍增"""
        self.countdown *= self.schedule_count

    def step_increment_algorithm(self):
        """步进递增"""
        self.countdown += self.step

    def fibonacci_algorithm(self, num=None):
        """just for fun, no used"""
        if num is None: num = self.schedule_count
        if num <= 2:
            f = 1
        else:
            f = self.fibonacci_algorithm(num-1) + self.fibonacci_algorithm(num - 2)
        self.countdown = f
        return f

