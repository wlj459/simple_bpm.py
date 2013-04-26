import json
import celery
import cPickle as pickle
import stackless

from . import signals, states
from .execution import ExecutionManager
from .models import Task


@celery.task(ignore_result=True)
def acknowledge(task_id):

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        if not task._ack:
            signals.task_acknowledge.send(sender=acknowledge, task_id=task_id)


@celery.task(ignore_result=True)
def schedule(task_id):

    try:
        task = Task.objects.get(pk=task_id, state=states.READY)
    except Task.DoesNotExist:
        pass
    else:
        if task.transit(states.RUNNING):
            execution = ExecutionManager(task_id)
            if execution.succeeded:
                definition = execution[task.name]
                globals()[task.name] = definition

                backend = pickle.loads(str(task.archive))
                backend.resume()

                stackless.schedule()
                while backend.schedule():
                    stackless.schedule()

                Task.objects.filter(pk=task.pk).update(archive=pickle.dumps(backend))
                backend.destroy()


@celery.task(ignore_result=True)
def initiate(task_id):

    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        pass
    else:
        execution = ExecutionManager(task_id)
        if execution.succeeded:
            definition = execution[task.name]
            globals()[task.name] = definition

            backend = definition(task_id)

            args = []
            if task.args:
                args = json.loads(task.args)

            kwargs = {}
            if task.kwargs:
                kwargs = json.loads(task.kwargs)

            backend.initiate(*args, **kwargs)
            task.transit(states.READY, archive=pickle.dumps(backend))
            backend.destroy()
