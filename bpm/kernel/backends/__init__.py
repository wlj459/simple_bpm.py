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
    __metaclass__ = ABCMeta

    def __init__(self, task_id, task_name):
        self._task_id = task_id
        self._task_name = task_name

        self._registry = {}

    def _destroy(self):
        """
        destroy
        """
        map(lambda tasklet: tasklet.kill(), self._registry)

    def _initiate(self, *args, **kwargs):
        """
        initiate
        """
        task = self._model_object()
        if task:
            self._register(stackless.tasklet(self.start)(*args, **kwargs),
                           task.name)
        else:
            raise Exception  # TODO

    @transaction.commit_on_success()  # Important !
    def _model_object(self):
        """
        model_object
        """
        try:
            return Task.objects.get(pk=self._task_id)
        except Task.DoesNotExist:
            pass

    def _register(self, obj, task_name):
        """
        register
        """
        self._registry[obj] = task_name

    def _resume(self):
        """
        resume
        """
        for tasklet in self._registry:
            if tasklet.alive:
                tasklet.insert()

    @abstractmethod
    def _schedule(self):
        """
        schedule
        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        """
        start
        """
        raise NotImplementedError
