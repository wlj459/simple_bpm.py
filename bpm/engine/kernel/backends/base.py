# coding: utf-8

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
            pass    # TODO
        else:
            self._register(stackless.tasklet(self._start)(*args, **kwargs),
                           task.name)

    def _register(self, obj, task_name, obj_type='tasklet'):
        """
        这个_register 主要是用来处理 tasklet和handler的注册的，因为行为类似, 所以一个方法来实现
        对于tasklet的注册, obj_type="tasklet"
        对于handler的注册， obj_type="handler"
        """
        registry = getattr(self, '_%s_registry' % obj_type)
        if isinstance(registry, dict):
            registry[obj] = task_name       # 将tasklet作为key(保证唯一性)

    def _start(self, *args, **kwargs):
        self.start(*args, **kwargs)

    def _resume(self):
        for tasklet in self._tasklet_registry:  # 对于 _resume方法而言, 处理的就是 _tasklet_registry里面的东西
            if tasklet.alive:
                try:
                    tasklet.insert()
                except:
                    pass    # TODO

    def _schedule(self):
        raise NotImplementedError

    def start(self, *args, **kwargs):
        raise NotImplementedError

