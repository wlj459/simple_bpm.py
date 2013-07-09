from django.test import TestCase

from bpm.engine.kernel import sandbox
from bpm.engine.kernel import hg_importer
from bpm.log.models import Record
from bpm.log import tasks as bpm_log_tasks_module
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
from bpm.engine.kernel import BaseComponent
print(BaseComponent)
""")
        import my_module
        self.assertEqual(1, Record.objects.count())
        record = Record.objects.all()[0]
        # self.assertEqual('my_module', record.logger) TODO: fix the logger name
        self.assertIn('BaseComponent', record.message)