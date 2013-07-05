import functools
import json

from django.test import TestCase

from bpm.engine.kernel.models import Task

from bpm.engine.kernel import tasks as kernel_tasks_module
from bpm.engine.kernel import execution
from bpm.log import tasks as log_tasks_module


class InMemoryJobQueue(object):
    def __init__(self):
        self.jobs = []

    def enqueue(self, job):
        self.jobs.append(job)


    def execute(self):
        while self.jobs:
            current_jobs = list(self.jobs)
            self.jobs = []
            for job in current_jobs:
                job()

    @classmethod
    def mock_celery_task(cls, module):
        in_memory_job_queue = cls()

        def mocked_apply_async(func, args, countdown=None):
            in_memory_job_queue.enqueue(functools.partial(func, *args))

        for member_name in dir(module):
            member = getattr(module, member_name)
            if hasattr(member, 'apply_async'):
                member.apply_async = functools.partial(mocked_apply_async, func=member)
        return in_memory_job_queue


class InMemoryRepository(object):
    class Lookup(object):
        def __init__(self, repo, segments=()):
            self.repo = repo
            self.segments = list(segments)

        def __getitem__(self, segment):
            return InMemoryRepository.Lookup(self.repo, self.segments + [segment])

        def data(self):
            return self.repo.data('.'.join(self.segments))

        def set_data(self, data):
            return self.repo.set_data('.'.join(self.segments), data)

    def __init__(self):
        self.data_dict = {}


    def __getitem__(self, segment):
        return InMemoryRepository.Lookup(self, [segment])

    def data(self, path):
        return self.data_dict[path]

    def set_data(self, path, data):
        self.data_dict[path] = data

    @classmethod
    def mock_hg(cls, module):
        in_memory_repo = cls()

        def mocked_repository(ui, path='', create=False):
            return in_memory_repo

        module.repository = mocked_repository
        return in_memory_repo


def mocked_log(args, retry=None):
    created, name, revision, level, module, lineno, function, message = args
    print('%s %s' % (created, message))


log_tasks_module.log.apply_async = mocked_log


class BasicComponentTest(TestCase):
    def test(self):
        in_memory_repository = InMemoryRepository.mock_hg(execution.hg)
        in_memory_repository.set_data('tip.test/__init__.py', """
from bpm.engine.kernel import BaseComponent
from bpm.log import get_logger
from bpm.engine.kernel import internal_import

logger = get_logger()

class BasicComponent(BaseComponent):

    def start(self, name):
        logger.debug('Component start')
        self.task_id = name
        self.set_default_scheduler(self.on_schedule)

    def on_schedule(self):
        logger.debug('Component on_schedule')
        if self.schedule_count >= 3:
            self.complete('task done: %s' % self.task_id)
        """)
        in_memory_job_queue = InMemoryJobQueue.mock_celery_task(kernel_tasks_module)
        task = Task.objects.start('test.BasicComponent', args=['abcd'])
        in_memory_job_queue.execute()
        task = Task.objects.get(id=task.id)
        self.assertEqual('task done: abcd', json.loads(task.data))


class BasicProcessTest(TestCase):
    def test(self):
        in_memory_repository = InMemoryRepository.mock_hg(execution.hg)
        in_memory_repository.set_data('tip.test/__init__.py', """
from bpm.engine.kernel import BaseComponent
from bpm.engine.kernel import BaseProcess
from bpm.log import get_logger
from bpm.engine.kernel import internal_import

logger = get_logger()

class BasicComponent(BaseComponent):

    def start(self, name):
        logger.debug('Component start')
        self.task_id = name
        self.set_default_scheduler(self.on_schedule)

    def on_schedule(self):
        logger.debug('Component on_schedule')
        if self.schedule_count >= 3:
            self.complete('task done: %s' % self.task_id)

class BasicProcess(BaseProcess):

    def start(self, name):
        rval = self.tasklet(BasicComponent)(name).read()
        self.complete(rval)
        """)
        in_memory_job_queue = InMemoryJobQueue.mock_celery_task(kernel_tasks_module)
        task = Task.objects.start('test.BasicProcess', args=['abcd'])
        in_memory_job_queue.execute()
        task = Task.objects.get(id=task.id)
        self.assertEqual('task done: abcd', json.loads(task.data))