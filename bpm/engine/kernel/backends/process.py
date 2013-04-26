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

    def __init__(self, process, task_name, predecessors=[]):
        self.process = process
        self.task_name = task_name
        self.predecessors = predecessors

        try:
            parent = Task.objects.get(pk=process._task_id)
        except Task.DoesNotExist:
            pass
        else:
            task = Task(name=task_name,
                        parent=parent,
                        ttl=parent.ttl + 1)
            task.save()
            self.task_id = task.id
            process._register(self, task_name, obj_type='handler')

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

        Task.objects.filter(pk=self.task_id)\
                    .update(args=json.dumps(cleaned_args),
                            kwargs=json.dumps(cleaned_kwargs))
        signals.task_ready.send(sender=self, instance=self.instance())

    def instance(self):
        try:
            return Task.objects.get(pk=self.task_id)
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
