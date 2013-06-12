from celery import signals

from .models import Task


@signals.task_sent.connect
def task_sent(**kwargs):
    print 'task_sent'

@signals.task_prerun.connect
def task_prerun(*args, **kwargs):
    from bpm.engine.kernel import modules
    modules = {}

@signals.task_postrun.connect
def task_postrun(*args, **kwargs):
    print 'task_postrun'
    from bpm.engine.kernel import modules
    print modules

@signals.task_success.connect
def task_success(*args, **kwargs):
    print 'task_success'

@signals.task_failure.connect
def task_failure(**kwargs):
    print 'task_failure'
    if 'args' in kwargs and kwargs['args']:
        try:
            task = Task.objects.get(pk=kwargs['args'][0])
        except Task.DoesNotExist:
            # TODO
            print 'Task Does Not Exist'
            pass
        except:
            # TODO
            import traceback
            print traceback.print_exc()
        else:
            task.complete(data=unicode(kwargs['exception']),
                          ex_data=unicode(kwargs['einfo'].traceback),
                          return_code=1)

@signals.task_revoked.connect
def task_revoked(*args, **kwargs):
    print 'task_revoked'
