"""
bpm.engine.kernel.backends.base
===============================

Task backend base class.
"""
import stackless

from ..models import Task


class BaseTaskBackend(object):

    def __init__(self, task_id):
        self._tasklet_registry = {}
        self._task_id = task_id

    def _destroy(self):
        map(lambda tasklet: tasklet.kill(), self._tasklet_registry)

    def _initiate(self, *args, **kwargs):
        try:
            task = Task.objects.get(pk=self._task_id)
        except Task.DoesNotExist:
            pass
        else:
            self._register(stackless.tasklet(self.start)(*args, **kwargs),
                          task.name)

    def _register(self, obj, task_name, obj_type='tasklet'):
        registry = getattr(self, '_%s_registry' % obj_type)
        if isinstance(registry, dict):
            registry[obj] = task_name

    def _resume(self):
        for tasklet in self._tasklet_registry:
            if tasklet.alive:
                try:
                    tasklet.insert()
                except:
                    pass

    def _schedule(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError