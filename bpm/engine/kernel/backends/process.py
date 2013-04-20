"""
bpm.engine.kernel.backends.process
==================================
"""
import json
import stackless

from .. import signals, states
from ..models import Task
from .base import BaseTaskBackend


class TaskHandler(object):

    PROCESS_CACHE_KEY = '_process'

    def __init__(self, process, task_name, predecessors=[]):
        self.blocked = False
        self.process = process
        self.task_name = task_name
        self.predecessors = predecessors

        self.process._register(self, task_name, obj_type='handler')
        self.process_id = self.process._task_id

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

        task = Task(name=self.task_name,
                    parent=self.parent(),
                    ttl=self.parent().ttl)
        task.save()

        setattr(self, 'task_id', task.id)

    def instance(self):
        try:
            return Task.objects.get(pk=getattr(self, 'task_id'))
        except Task.DoesNotExist:
            pass

    def join(self):
        task = self.instance()
        while not task.state in states.READY_STATES:
            self.blocked = True
            stackless.schedule()
            task = self.instance()

        self.blocked = False
        signals.task_confirmed.send(sender=self.__class__, instance=task)
        return task

    def parent(self):
        if hasattr(self, self.PROCESS_CACHE_KEY):
            return getattr(self, self.PROCESS_CACHE_KEY)
        else:
            try:
                task = Task.objects.get(pk=self.process_id)
            except Task.DoesNotExist:
                pass
            else:
                setattr(self, self.PROCESS_CACHE_KEY, task)
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
        for tasklet in self._tasklet_registry:
            if tasklet.alive:
                alive_count += 1
        for handler in self._handler_registry:
            if handler.blocked:
                block_count += 1

        return alive_count > block_count

    def tasklet(self, task_name, predecessors=[]):
        return TaskHandler(self, task_name, predecessors)


def join(*handlers):
    for handler in handlers:
        handler.blocked = True

    for handler in handlers:
        handler.join()
