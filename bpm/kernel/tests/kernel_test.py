import json

from django.test import TestCase

from bpm.kernel.models import Task

from . import hg_test_helper
from .context_test_helper import apply_context
from .kernel_test_helper import mock_bpm_kernel


class KernelTest(TestCase):
    def setUp(self):
        super(KernelTest, self).setUp()
        self.repo = hg_test_helper.InMemoryRepository()
        apply_context(self, mock_bpm_kernel(self.repo))

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
        task = Task.objects.get(id=task.id)
        self.assertEqual('task done: abcd', json.loads(task.data))