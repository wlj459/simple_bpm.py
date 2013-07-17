import json
import contextlib

from django.test import TestCase

from bpm.kernel.models import Task

from bpm.kernel import tasks as kernel_tasks_module
from bpm.kernel.sandbox import hg_importer
from bpm.logging import tasks as log_tasks_module
from . import hg_test_helper
from . import celery_test_helper
from .context_test_helper import apply_context


@contextlib.contextmanager
def mock_log():
    def mocked_log(args, retry=None):
        created, name, revision, level, module, lineno, function, message = args
        print('%s %s' % (created, message))

    orig_apply_async = log_tasks_module.log.apply_async
    try:
        log_tasks_module.log.apply_async = mocked_log
        yield
    finally:
        log_tasks_module.log.apply_async = orig_apply_async


class KernelTest(TestCase):
    def setUp(self):
        super(KernelTest, self).setUp()
        apply_context(self, mock_log())
        self.repo = hg_test_helper.InMemoryRepository()
        apply_context(self, hg_test_helper.mock_hg(self.repo, hg_importer.mercurial.hg))
        self.job_queue = celery_test_helper.DelayedJobQueue()
        apply_context(self, celery_test_helper.mock_celery_task(self.job_queue, kernel_tasks_module))

    def test_component(self):
        self.repo.set_data('test_component|tip|test_component/__init__.py', """
from bpm.kernel.backends.component import AbstractComponent
from bpm.logging import get_logger

logger = get_logger()

class BasicComponent(AbstractComponent):
    def start(self, name):
        logger.debug('Component start')
        self.task_id = name
        self.set_default_scheduler(self.on_schedule)

    def on_schedule(self):
        logger.debug('Component on_schedule')
        if self.schedule_count >= 3:
            self.complete(**{"data":'task done: %s' % self.task_id})
        """)
        task = Task.objects.start('test_component.BasicComponent', args=['abcd'])
        print(self.job_queue.jobs)
        self.job_queue.execute_delayed_jobs()
        task = Task.objects.get(id=task.id)
        self.assertEqual('task done: abcd', json.loads(task.data))


    def test_process(self):
        self.repo.set_data('test_process|tip|test_process/__init__.py', """
from bpm.kernel.backends.component import AbstractComponent
from bpm.kernel.backends.process import AbstractProcess
from bpm.logging import get_logger

logger = get_logger()

class BasicComponent(AbstractComponent):

    def start(self, name):
        logger.debug('Component start')
        self.task_id = name
        self.set_default_scheduler(self.on_schedule)

    def on_schedule(self):
        logger.debug('Component on_schedule')
        if self.schedule_count >= 3:
            self.complete('task done: %s' % self.task_id)

class BasicProcess(AbstractProcess):

    def start(self, name):
        rval = self.tasklet(BasicComponent)(name).read()
        self.complete(rval)
        """)
        task = Task.objects.start('test_process.BasicProcess', args=['abcd'])
        self.job_queue.execute_delayed_jobs()
        task = Task.objects.get(id=task.id)
        self.assertEqual('task done: abcd', json.loads(task.data))