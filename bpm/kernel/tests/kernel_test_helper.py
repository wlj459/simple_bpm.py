import contextlib

from . import celery_test_helper
from bpm.kernel import tasks as kernel_tasks_module

from bpm.kernel.models import Task

from .hg_test_helper import InMemoryRepository
from .hg_test_helper import mock_hg
from bpm.kernel.sandbox import hg_importer
from bpm.logging import tasks as log_tasks_module

__all__ = ['InMemoryRepository', 'mock_bpm_kernel']


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


@contextlib.contextmanager
def mock_bpm_kernel(repo):
    with mock_log():
        with mock_hg(repo, hg_importer.mercurial.hg):
            job_queue = celery_test_helper.DelayedJobQueue()
            with celery_test_helper.mock_celery_task(job_queue, kernel_tasks_module):
                orig_start = Task.objects.start

                def mocked_start(*args, **kwargs):
                    try:
                        return orig_start(*args, **kwargs)
                    finally:
                        job_queue.execute_delayed_jobs()

                Task.objects.start = mocked_start
                try:
                    yield
                finally:
                    Task.objects.start = orig_start