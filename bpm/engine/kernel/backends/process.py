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


class TaskHandler(object):
    """
        task是在handler方法被执行的时候才会进行创建
        目前看这种方式似乎是安全的
        TODO: review
    """
    def __init__(self, process, task_name, predecessors=[]):

        self.process = process
        self.task_name = task_name
        self.predecessors = predecessors
        self.identifier_code = generate_salt()
        self.token_code = generate_salt()
        process._register(self, self.task_name, obj_type='handler')


    def __call__(self, *args, **kwargs):
        self.process._register(stackless.tasklet(self.handle)(*args, **kwargs),
                               self.task_name)
        return self

    def handle(self, *args, **kwargs):
        if self.predecessors:
            join(*self.predecessors)

        cleaned_args = []
        for arg in args:
            if isinstance(arg, self.__class__):
                arg = arg.read()
            cleaned_args.append(arg)

        cleaned_kwargs = {}
        for k, v in kwargs.iteritems():
            if isinstance(v, self.__class__):
                v = v.read()
            cleaned_kwargs[k] = v

        try:
            parent = Task.objects.get(pk=self.process._task_id)
        except Task.DoesNotExist:
            pass
        else:
            try:
                task = Task(name=self.task_name,
                            parent=parent,
                            identifier_code=self.identifier_code,
                            token_code=self.token_code,
                            args=json.dumps(cleaned_args),
                            kwargs=json.dumps(cleaned_kwargs),
                            ttl=parent.ttl + 1)
                task.save()
            except Exception, e:
                task = Task(name=self.task_name,
                            parent=parent,
                            identifier_code=self.identifier_code,
                            token_code=self.token_code,
                            ex_data=str(e),
                            state=states.FAILURE,
                            ttl=parent.ttl + 1)
                task.save()     # TODO: 需要svein实现post_save中的处理逻辑，如果创建出来的任务状态是FAILURE,就不执行了

    @transaction.commit_on_success()    # 需要在一个事务中完成，否则可能出现幻读
    def instance(self):
        try:
            return Task.objects.get(identifier_code=self.identifier_code, token_code=self.token_code)
        except Task.DoesNotExist:
            pass

    def join(self):
        task = self.instance()
        while task.state == states.BLOCKED:
            stackless.schedule()
            task = self.instance()

        return task

    def read(self):
        task = self.join()
        if task.data:
            return json.loads(task.data)


class BaseProcess(BaseTaskBackend):
    def __init__(self, *args, **kwargs):
        super(BaseProcess, self).__init__(*args, **kwargs)

        self._handler_registry = {}

    def _schedule(self):
        alive_count = block_count = 0
        for tasklet, task_name in self._tasklet_registry.items():  # TODO: 这里有问题，process本身的主tasklet不计算在内
            if tasklet.alive:
                alive_count += 1
        for handler, task_name in self._handler_registry.items():
            task = handler.instance()
            if task.state == states.BLOCKED:
                block_count += 1

        # TODO: review this code
        return alive_count - 1 > block_count

        # def tasklet(self, task_name, predecessors=[]):

    #     return TaskHandler(self, task_name, predecessors)
    def tasklet(self, task, predecessors=None):
        if not predecessors: predecessors = []
        if issubclass(task, BaseTaskBackend):
            return TaskHandler(self, "%s.%s" % (task.__module__, task.__name__), predecessors)    # here task is a class inherited from BaskTask
        elif isinstance(task, basestring):
            return TaskHandler(self, task, predecessors)
        else:
            pass  # TODO something


def join(*handlers):
    for handler in handlers:
        handler.blocked = True

    for handler in handlers:
        handler.join()
