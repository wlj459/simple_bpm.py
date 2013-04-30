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


    def init(self, defination_id, task_id):
        """组件和一个过程不同，不能直接执行，只能通过一个任务来启动"""
        if not task_id:
            return False, "need task_id"
        try:
            self.task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return False, "task instance not exist， task_id=%s" % task_id

    def start(self, *args, **kwargs):
        """
        start方法需要组件开发者实现, 如cc接口调用， 如果没有设置self.enable_schedule=True，
        则返回的值会直接作为组件的结果进行 callback(celery task)
        """
        raise NotImplementedError

    def scheduler(self, on_schedule_method, algorithm=None, *args, **kwargs):
        """
            组件开发者如果需要对异步接口进行同步的话，可以使用该方法，
            这个方法会调用用户传递的一个处理方法来进行

            e.g:
            def on_schedule():
                result = async__peek()
                if result['return'] == 0:
                    self.callback(result)
                elif result['return'] = 3:
                    self.err_back(result)

            def start():
                # do something
                self.sid = async_api_call()
                scheduler()
        """

    def _schedule(self, *args, **kwargs):
        try:
            task = Task.objects.get(pk=self._task_id)       # TODO: implement __instance
        except Task.DoesNotExist:
            pass
        else:
            self._register(stackless.tasklet(self.on_schedule)(*args, **kwargs),
                           task.name)
            task.transit(states.READY)
        return False

    def _callback(self):
        """任务完成的通知"""
        print "%s callback with result = %s" % (self.__class__, str(self.result))
        self.task.result = self.result
        callback.delay(self.task.id, self.result)

    def on_schedule(self):
        raise NotImplementedError