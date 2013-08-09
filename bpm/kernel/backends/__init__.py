# -*- coding: utf-8 -*-
"""
bpm.kernel.backends
===================
"""
import stackless

from abc import ABCMeta, abstractmethod
from django.db import transaction

from bpm.kernel.models import Task


class AbstractBaseTaskBackend(object):
    '''
    #matt: 基类里主要实现当前task对stackless微线程的操作
    #matt: 关键点：registry, 用于注册当前task下的所有微线程
    '''
    __metaclass__ = ABCMeta

    def __init__(self, task_id, task_name):
        self._task_id = task_id
        self._task_name = task_name

        self._registry = {}

    def _destroy(self):
        """
        destroy
        #matt: 根据自己的注册表，杀死所有微线程
        """
        map(lambda tasklet: tasklet.kill(), self._registry)

    def _initiate(self, *args, **kwargs):
        """
        #matt: 将自己的start方法加入注册表
        """
        task = self._model_object()
        if task:
            self._register(stackless.tasklet(self.start)(*args, **kwargs),
                           task.name)  #? matt: 这里有start和on_schedule都会被注册，为什么值都是task.name
        else:
            raise Exception  # TODO

    #matt:
    # commit_on_success会在方法进入时启动事务，并在方法结束时commit，
    # 这样可以保证取到的是数据库的最新记录（在一次transaction内部，不管外部怎么改变记录，查询记录时总是不变的)
    @transaction.commit_on_success()  # Important !
    def _model_object(self):
        """
        model_object
        #matt: 获取数据库里的对象记录
        """
        try:
            return Task.objects.get(pk=self._task_id)
        except Task.DoesNotExist:
            pass

    def _register(self, obj, task_name):
        """
        register
        #matt: 用来resume， initiate和kill
        """
        self._registry[obj] = task_name

    def _resume(self):
        """
        resume
        #matt: 将registry里的所有微线程插入等待队列，在stackless.schedule时全部执行
        """
        for tasklet in self._registry:
            if tasklet.alive:
                tasklet.insert()

    @abstractmethod
    def _schedule(self):
        """
        schedule
        #matt: 抽象方法： 在子类(process和component)中有不同的实现
        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        """
        start
        #matt: 抽象方法： 在子类(process和component)中有不同的实现
        """
        raise NotImplementedError
