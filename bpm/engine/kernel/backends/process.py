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
    def model_object(self):
        try:
            return Task.objects.get(identifier_code=self.identifier_code,
                                    token_code=self.token_code)
        except Task.DoesNotExist:
            pass

    def join(self):
        model_object = self.model_object()
        while not model_object or model_object.state not in states.ARCHIVE_STATES:
            stackless.schedule()
            model_object = self.model_object()

        return model_object

    def read(self):
        model_object = self.join()
        if model_object.data:
            return json.loads(model_object.data)


class BaseProcess(BaseTaskBackend):
    def __init__(self, *args, **kwargs):
        super(BaseProcess, self).__init__(*args, **kwargs)

        self.count = 0
        self._handler_registry = {}

    def _schedule(self):
        archived_handler_count = 0
        blocked_handler_count = 0
        for handler, name in self._handler_registry.iteritems():
            model_object = handler.model_object()
            if model_object is not None:
                if model_object.state in states.ARCHIVE_STATES:
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
        for tasklet, name in self._tasklet_registry.iteritems():
            if tasklet.alive:
                alive_tasklet_count += 1

        if not alive_tasklet_count and \
                not blocked_handler_count and \
                archived_handler_count == len(self._handler_registry):
            self.complete()

    def complete(self, *args, **kwargs):
        model_object = self._model_object()
        if model_object is not None:
            cleaned_args, cleaned_kwargs = clean(*args, **kwargs)
            model_object.complete(*cleaned_args, **cleaned_kwargs)

    def tasklet(self, task, predecessors=None):
        assert issubclass(task, BaseTaskBackend)
        if predecessors is None:
            predecessors = []
        return TaskHandler(self, '%s.%s' % (task.__module__, task.__name__), predecessors)    # here task is a class inherited from BaskTask


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
