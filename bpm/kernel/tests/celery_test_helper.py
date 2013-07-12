import functools
import contextlib


class DelayedJobQueue(object):
    def __init__(self):
        self.jobs = []

    def enqueue(self, job):
        self.jobs.append(job)


    def execute_delayed_jobs(self):
        while self.jobs:
            current_jobs = list(self.jobs)
            self.jobs = []
            for job in current_jobs:
                job()


class ImmediateJobQueue(object):
    def enqueue(self, job):
        job() # execute immediately


@contextlib.contextmanager
def mock_celery_task(job_queue, module):
    def mocked_apply_async(func, args, countdown=None, retry=None):
        job_queue.enqueue(functools.partial(func, *args))

    original_states = {}
    try:
        for member_name in dir(module):
            member = getattr(module, member_name)
            if hasattr(member, 'apply_async'):
                original_states[member] = member.apply_async
                member.apply_async = functools.partial(mocked_apply_async, func=member)
        yield
    finally:
        for member, orig_apply_async in original_states.items():
            member.apply_async = orig_apply_async
