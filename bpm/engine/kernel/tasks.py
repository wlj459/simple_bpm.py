import json
import celery
import cPickle as pickle
import stackless

from . import execution, signals, states
from .models import Task
from .serialization import Serialization


@celery.task(ignore_result=True)
def acknowledge(task_id):

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        if not task.ack:
            signals.task_acknowledge.send(sender=acknowledge, instance=task)


@celery.task(ignore_result=True)
def schedule(task_id):

    try:
        task = Task.objects.get(pk=task_id, state=states.READY)
    except Task.DoesNotExist:
        pass
    else:
        if task.transit(states.RUNNING):
            executor = execution.TaskExecutor(task)
            if executor.execute():
                locals().update(executor.locals())
                cls = locals()[task.name.split('.')[-1]]

                with Serialization(executor.locals().values()):
                    backend = pickle.loads(str(task.archive))
                    backend._resume()

                    stackless.schedule()
                    while backend._schedule():
                        stackless.schedule()

                    task.transit(states.BLOCKED, archive=pickle.dumps(backend))
                backend._destroy()


@celery.task(ignore_result=True)
def initiate(task_id):

    try:
        task = Task.objects.get(pk=task_id, state=states.PENDING)
    except Task.DoesNotExist:
        pass
    else:
        executor = execution.TaskExecutor(task)
        if executor.execute():
            locals().update(executor.locals())
            cls = locals()[task.name.split('.')[-1]]

            backend = cls(task.pk, task.name)

            args = []
            if task.args:
                args = json.loads(task.args)

            kwargs = {}
            if task.kwargs:
                kwargs = json.loads(task.kwargs)

            backend._initiate(*args, **kwargs)
            with Serialization(executor.locals().values()):
                task.transit(states.READY, archive=pickle.dumps(backend))
            backend._destroy()


@celery.task(ignore_result=True)
def transit(task_id, to_state):

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        Task.objects.transit(task, to_state)
