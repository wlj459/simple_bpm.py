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

        self.identifier_code = random.randstr()
        self.token_code = random.randstr()
        self.process._register(self, self.task_name, obj_type='handler')

    def __call__(self, *args, **kwargs):
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
        task = self._model_object()
        while not task or task.state not in states.ARCHIVE_STATES:
            stackless.schedule()
            task = self._model_object()

        return task

    def read(self):
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

    def complete(self, *args, **kwargs):
        task = self._model_object()
        if task is not None:
            cleaned_args, cleaned_kwargs = clean(*args, **kwargs)
            task.complete(*cleaned_args, **cleaned_kwargs)

    def tasklet(self, task, predecessors=None):
        assert issubclass(task, AbstractBaseTaskBackend)
        if predecessors is None:
            predecessors = []
        return TaskHandler(self, '%s.%s' % (task.__module__, task.__name__), predecessors)    # here backends is a class inherited from BaskTask


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