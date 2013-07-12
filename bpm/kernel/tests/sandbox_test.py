from django.test import TestCase

from bpm.kernel import sandbox
from bpm.kernel.sandbox import hg_importer
from bpm.logging.models import Record
from bpm.logging import tasks as bpm_log_tasks_module
from . import hg_test_helper
from . import celery_test_helper
from .context_test_helper import apply_context


class SandboxTest(TestCase):
    def setUp(self):
        super(SandboxTest, self).setUp()
        apply_context(self, sandbox.enter_context())
        self.repo = hg_test_helper.InMemoryRepository()
        apply_context(self, hg_test_helper.mock_hg(self.repo, hg_importer.mercurial.hg))
        job_queue = celery_test_helper.ImmediateJobQueue()
        apply_context(self, celery_test_helper.mock_celery_task(job_queue, bpm_log_tasks_module))

    def test_print(self):
        self.repo.set_data('my_module|tip|my_module/__init__.py', """
from bpm.kernel.backends.component import AbstractComponent
print(AbstractComponent)
""")
        import my_module
        self.assertEqual(1, Record.objects.count())
        record = Record.objects.all()[0]
        self.assertEqual('my_module', record.logger)
        self.assertIn('AbstractComponent', record.message)

    def test_logger_name(self):
        self.repo.set_data('my_module|tip|my_module/__init__.py', """
import sub_module
print('hello')
""")
        self.repo.set_data('my_module|tip|my_module/sub_module.py', '')
        import my_module
        self.assertEqual(1, Record.objects.count())
        record = Record.objects.all()[0]
        self.assertEqual('my_module', record.logger)
        self.assertEqual('hello', record.message)