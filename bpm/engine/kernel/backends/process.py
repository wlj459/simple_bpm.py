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
    def __init__(self, process, name, predecessors=None):
        self.process = process
        self.task_name = name

        if predecessors is None:
            predecessors = []
        self.predecessors = predecessors

        self.identifier_code = generate_salt()
        self.token_code = generate_salt()
        self.process._register(self, self.task_name, obj_type='handler')

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
            task = Task(name=self.task_name,
                        parent=parent,
                        identifier_code=self.identifier_code,
                        token_code=self.token_code,
                        args=json.dumps(cleaned_args),
                        kwargs=json.dumps(cleaned_kwargs),
                        ttl=parent.ttl + 1)
            task.save()

    @transaction.commit_on_success()    # 需要在一个事务中完成，否则可能出现幻读
    def instance(self):
        try:
            return Task.objects.get(identifier_code=self.identifier_code,
                                    token_code=self.token_code)
        except Task.DoesNotExist:
            pass

    def join(self):
        task = self.instance()
        if task:
            while task.state == states.BLOCKED:
                stackless.schedule()
                task = self.instance()
        else:
            stackless.schedule()

        return task

    def read(self):
        task = self.join()
        if task.data:
            return json.loads(task.data)


class BaseProcess(BaseTaskBackend):
    def __init__(self, *args, **kwargs):
        super(BaseProcess, self).__init__(*args, **kwargs)

        self.count = 0
        self._handler_registry = {}

    def _schedule(self):
        alive_tasklet_count = 0
        for tasklet, name in self._tasklet_registry.iteritems():
            if tasklet.alive:
                if name != self._task_name:
                    alive_tasklet_count += 1

        blocked_handler_count = 0
        archived_handler_count = 0
        for handler, name in self._handler_registry.iteritems():
            instance = handler.instance()
            if not instance or instance.state == states.BLOCKED:
                blocked_handler_count += 1
            if instance and instance.state in states.ARCHIVE_STATES:
                archived_handler_count += 1

        if alive_tasklet_count > blocked_handler_count:
            return True

        if not alive_tasklet_count and not blocked_handler_count and archived_handler_count == len(self._handler_registry):
            Task.objects.transit(Task.objects.get(pk=self._task_id), states.SUCCESS)

    def tasklet(self, task, predecessors=[]):
        return TaskHandler(self, task, predecessors)    # here task is a class inherited from BaskTask


def join(*handlers):
    for handler in handlers:
        handler.blocked = True

    for handler in handlers:
        handler.join()
