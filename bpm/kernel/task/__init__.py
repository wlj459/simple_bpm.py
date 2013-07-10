"""
bpm.kernel.task
===============
"""
import stackless

from django.db import transaction

from bpm.kernel.models import Task


class AbstractBaseTask(object):
    def __init__(self, task_id, task_name):
        self._tasklet_registry = {}
        self._task_id = task_id
        self._task_name = task_name

    def _destroy(self):
        map(lambda tasklet: tasklet.kill(), self._tasklet_registry)

    def _initiate(self, *args, **kwargs):
        try:
            task = Task.objects.get(pk=self._task_id)
        except Task.DoesNotExist:
            pass    # TODO
        else:
            self._register(stackless.tasklet(self.start)(*args, **kwargs),
                           task.name)

    @transaction.commit_on_success()  # Important !
    def _model_object(self):
        try:
            return Task.objects.get(pk=self._task_id)
        except Task.DoesNotExist:
            pass

    def _register(self, obj, task_name, obj_type='tasklet'):
        """
        这个_register 主要是用来处理 tasklet和handler的注册的，因为行为类似, 所以一个方法来实现
        对于tasklet的注册, obj_type="tasklet"
        对于handler的注册， obj_type="handler"
        """
        registry = getattr(self, '_%s_registry' % obj_type)
        if isinstance(registry, dict):
            registry[obj] = task_name       # 将tasklet作为key(保证唯一性)

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
