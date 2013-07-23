# -*- coding: utf-8 -*-
"""
bpm.kernel.backends.process
===========================
"""
import json
import stackless

from django.db import transaction

from bpm.kernel import signals, states
from bpm.kernel.models import Task
from bpm.kernel.backends import AbstractBaseTaskBackend
from bpm.utils import random
from abc import abstractmethod


class TaskHandler(object):
    """
    过程利用TaskHandler的实例来等待子任务的执行并获得返回值
    """
    def __init__(self, process, name, predecessors=None):
        self.process = process
        self.task_name = name

        if predecessors is None:
            predecessors = []
        self.predecessors = predecessors

        self.identifier_code = random.randstr()
        self.token_code = random.randstr()
        self.process._register(self, self.task_name, obj_type='handler')

    def __call__(self, *args, **kwargs):
        """
        设置子任务的执行参数。参数可以是TaskHandler类型的，引擎会在执行的时候取得TaskHandler的值再作为参数使用。
        """
        self.process._register(stackless.tasklet(self._handle)(*args, **kwargs),
                               self.task_name)
        return self

    def _handle(self, *args, **kwargs):
        if self.predecessors:
            join(*self.predecessors)

        cleaned_args, cleaned_kwargs = clean(*args, **kwargs)

        try:
            parent = Task.objects.get(pk=self.process._task_id)
        except Task.DoesNotExist:
            pass
        else:
            task = Task(name=self.task_name,
                        parent=parent,
                        identifier_code=self.identifier_code,
                        token_code=self.token_code,
                        args=json.dumps(cleaned_args),
                        kwargs=json.dumps(cleaned_kwargs),
                        ttl=parent.ttl + 1)
            task.save()

    @transaction.commit_on_success()  # Important !
    def _model_object(self):
        try:
            return Task.objects.get(identifier_code=self.identifier_code,
                                    token_code=self.token_code)
        except Task.DoesNotExist:
            pass

    def join(self):
        """
        等待子任务执行完成
        """
        task = self._model_object()
        while not task or task.state not in states.ARCHIVE_STATES:
            stackless.schedule()
            task = self._model_object()

        return task

    def read(self):
        """
        等待子任务执行完成，并获取返回值
        """
        task = self.join()
        if task.data:
            return json.loads(task.data)


class AbstractProcess(AbstractBaseTaskBackend):
    """
    过程类需要继承此类
    """
    def __init__(self, *args, **kwargs):
        super(AbstractProcess, self).__init__(*args, **kwargs)

        self.count = 0
        self._handler_registry = {}

    @abstractmethod
    def start(self):
        """
        | 过程的定义实现在这个方法内。一般情况下本方法会执行很快，只是设置需要执行的子任务。
        | 当需要等待子任务返回值以决定后续流程的情况，本方法会分成很多时间片，执行很长时间。流程的推进是有引擎来调度的。
        | start通过 :py:meth:`tasklet` 方法定义过程的子任务。所以start方法执行完了，过程真正的执行才刚刚开始。
        | 过程会在start函数结束，而且所有产生的子任务执行结束之后才结束。
        | 过程可以有返回值，通过 :py:meth:`complete` 设置，如果没有设置默认为空。

        :return: 无返回值

        **多个子任务并行执行**:

                .. sourcecode:: python

                    self.tasklet('package.example.Component1')()
                    self.tasklet('package.example.Component2')()
                    self.tasklet('package.example.Component3')()

        **多个子任务串行执行**:

                .. sourcecode:: python

                    self.tasklet('package.example.Component1')() \\
                        .tasklet('package.example.Component2')() \\
                        .tasklet('package.example.Component3')()

        **子任务按照逻辑执行**:

                .. sourcecode:: python

                    if self.tasklet('package.example.Component1')().read() > 100:
                        self.tasklet('package.example.Component2')()
                    else:
                        self.tasklet('package.example.Component3')()
        """
        raise NotImplementedError

    def _register(self, obj, task_name, obj_type=None):
        """
        register
        """
        if obj_type:
            getattr(self, '_%s_registry' % obj_type)[obj] = task_name
        else:
            super(AbstractProcess, self)._register(obj, task_name)

    def _schedule(self):
        """
        schedule
        """
        archived_handler_count = 0
        blocked_handler_count = 0
        for handler, name in self._handler_registry.iteritems():
            task = handler._model_object()
            if task is not None:
                if task.state in states.ARCHIVE_STATES:
                    archived_handler_count += 1
            else:
                blocked_handler_count += 1

        if hasattr(self, 'archived_handler_count'):
            if archived_handler_count != self.archived_handler_count:
                self.archived_handler_count = archived_handler_count
                return True
        else:
            setattr(self, 'archived_handler_count', 0)
            return True

        alive_tasklet_count = 0
        for tasklet, name in self._registry.iteritems():
            if tasklet.alive:
                alive_tasklet_count += 1

        if not alive_tasklet_count and \
                not blocked_handler_count and \
                archived_handler_count == len(self._handler_registry):
            self.complete()

    def tasklet(self, task, predecessors=None):
        """
        在 :py:meth:`start` 中调用本方法产生子任务。注意本方法的返回值还需要再经过一次调用才真正完成了创建子任务的工作。

        .. sourcecode:: python

                    self.tasklet("package.example.Component1")("arg1", arg2="some-value")

        如果没有设置 predecessors 则立即执行，否则等待所有前置条件满足之后再执行。

        :param task: 子任务的Python类名
        :param predecessors: 子任务执行所依赖的其他任务，只有在这些任务执行完之后才会执行本子任务
        :return: 子任务的Handler，可以用来获取返回值 :py:meth:`bpm.kernel.backends.process.TaskHandler.read`。或者用来等待任务执行结束 :py:meth:`bpm.kernel.backends.process.TaskHandler.join`
        :rtype: :py:class:`bpm.kernel.backends.process.TaskHandler`
        """
        assert issubclass(task, AbstractBaseTaskBackend)
        if predecessors is None:
            predecessors = []
        return TaskHandler(self, '%s.%s' % (task.__module__, task.__name__), predecessors)    # here backends is a class inherited from BaskTask

    def complete(self, data=None, ex_data=None, return_code=0):
        """
        把过程的状态设置为已结束，并提供返回值。虽然本调用后面的语句仍然会被执行，但是不推荐这么做。
        如果不显式调用complete，引擎会在所有子任务执行完成后自动调用complete，返回值为空。

        :param data: 过程的返回值。调用者如果用read()方法等待，则会获得该值
        :type data: str
        :param ex_data: 过程的其他返回。用于调试
        :type ex_data: str
        :param return_code: 0表示正常，非0表示异常。异常情况由引擎接管，决定是否调用后面的任务
        :type return_code: int
        :return: 无返回值
        """
        (data, ex_data, return_code), _ = clean(data, ex_data, return_code)
        task = self._model_object()
        if task is not None:
            task.complete(data, ex_data, return_code)


def clean(*args, **kwargs):

    cleaned_args = []
    for arg in args:
        if isinstance(arg, TaskHandler):
            arg = arg.read()
        cleaned_args.append(arg)

    cleaned_kwargs = {}
    for k, v in kwargs.iteritems():
        if isinstance(v, TaskHandler):
            v = v.read()
        cleaned_kwargs[k] = v

    return cleaned_args, cleaned_kwargs


def join(*handlers):
    for handler in handlers:
        handler.join()