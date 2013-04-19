import stackless

from ..models import Task


class BaseTask(object):

    def __init__(self, task_id):
        self._tasklets = []

        self.task_id = task_id

    def add_handler(self, handler):
        if not handler in self._handlers:
            self._handlers.append(handler)

    def add_tasklet(self, tasklet):
        if not tasklet in self._tasklets:
            self._tasklets.append(tasklet)

    def destroy(self):
        map(lambda x: x.kill(), self._tasklets)

    def initiate(self, *args, **kwargs):
        self.add_tasklet(stackless.tasklet(self.start)(*args, **kwargs))

    def instance(self):
        try:
            return Task.objects.get(pk=self.task_id)
        except Task.DoesNotExist:
            pass

    def is_complete(self):
        raise NotImplementedError

    def resume(self):
        for t in self._tasklets:
            if not t.alive:
                self._tasklets.remove(t)

        for t in self._tasklets:
            try:
                t.insert()
            except:
                pass

    def schedule(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError