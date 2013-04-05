import cPickle
import stackless

from .base import BaseTask
from .models import Process, Task, Defination


def join(*handlers):
    for handler in handlers:
        handler.wait()


class TaskHandler(object):

    def __init__(self, cls, target, predecessors):
        if not self in cls._handlers:
            print "#" * 40
            print "Create handler for task %s" % target
            print "#" * 40
            self.blocked = False
            self.cls = cls
            self.target = target
            self.predecessors = predecessors

            self.cls.add_handler(self)

            task = Task(process=Process.objects.get(pk=cls.process_id))
            try:
                task.save()
            except:
                pass
            else:
                print "#" * 40
                print "Create task %d" % task.id
                print "#" * 40
                self.task_id = task.id

    def __call__(self, *args, **kwargs):
        self.cls.add_tasklet(stackless.tasklet(self.handle)(*args, **kwargs))
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

        Task.objects.filter(pk=self.task_id).update(
            args=cPickle.dumps(cleaned_args),
            kwargs=cPickle.dumps(cleaned_kwargs),
        )

        print
        print '#' * 40
        print 'Call %s: args=%s, kwargs=%s, task_id: %d' % (self.target, cleaned_args, cleaned_kwargs, self.task_id)
        print '#' * 40
        print

    def instance(self):
        try:
            task = Task.objects.get(pk=self.task_id)
        except Task.DoesNotExist:
            pass
        else:
            return task

    def read(self):
        task = self.wait()
        if task.result:
            return cPickle.loads(task.result)

    def wait(self):
        task = self.instance()
        while not task.is_complete:
            # do something
            print "#" * 40
            print "Task %d blocked" % self.task_id
            print "#" * 40
            self.blocked = True
            stackless.schedule()
            task = self.instance()

        Task.objects.filter(pk=self.task_id).update(is_confirmed=True)
        self.blocked = False
        return task


class BaseProcess(BaseTask):

    def __init__(self, defination_id, *args, **kwargs):
        super(BaseProcess, self).__init__(namespace='', *args, **kwargs)

        self._handlers = []
        self._tasklets = []

        process = Process(defination=Defination.objects.get(pk=defination_id))
        try:
            process.save()
        except:
            pass
        else:
            self.process_id = process.id

    def add_handler(self, handler):
        if not handler in self._handlers:
            self._handlers.append(handler)

    def add_tasklet(self, tasklet):
        if not tasklet in self._tasklets:
            self._tasklets.append(tasklet)

    def can_continue(self):
        count = 0
        for handler in self._handlers:
            if handler.blocked:
                count += 1
        run_count = 0
        for tasklet in self._tasklets:
            if tasklet.alive:
                run_count += 1
        print "#" * 40
        print "run_count: %d, handlers: %d, blocked_handlers: %d" % (run_count, len(self._handlers), count)
        print "#" * 40
        return run_count - 1 > count

    def is_complete(self):
        run_count = 0
        for tasklet in self._tasklets:
            if tasklet.alive:
                run_count += 1

        if run_count:
            return False
        else:
            x = 0
            for handler in self._handlers:
                if handler.instance().is_complete:
                    x += 1

            if len(self._handlers) <= x:
                return True

    def initiate(self, *args, **kwargs):
        self.add_tasklet(stackless.tasklet(self.start)(*args, **kwargs))

    def instance(self):
        try:
            process = Process.objects.get(pk=self.process_id)
        except Process.DoesNotExist:
            pass
        else:
            return process

    def resume(self):
        for t in self._tasklets:
            if not t.alive:
                self._tasklets.remove(t)

        for t in self._tasklets:
            try:
                t.insert()
            except:
                pass

    def start(self):
        raise NotImplementedError

    def tasklet(self, target, predecessors=[]):
        print "#" * 40
        print "Create tasklet for %s" % target
        print "#" * 40
        return TaskHandler(self, target, predecessors)

    def test(self):
        pass
