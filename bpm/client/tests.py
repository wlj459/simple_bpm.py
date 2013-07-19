import contextlib
import socket

from django.test import TestCase

from django.core.wsgi import get_wsgi_application
from django.db import close_connection
from django.core import signals

from bpm.kernel.tests.context_test_helper import apply_context
import gevent
import gevent.monkey
import gevent.wsgi
from .client import *
from bpm.kernel.tests.kernel_test_helper import *


# easy_install https://gevent.googlecode.com/files/gevent-1.0rc2.tar.gz
@contextlib.contextmanager
def run_test_server():
    signals.request_finished.disconnect(close_connection) # share same connection for all requests

    def serve():
        application = get_wsgi_application()
        gevent.wsgi.WSGIServer(('', 8000), application).serve_forever()

    gevent.spawn(serve)
    gevent.monkey.patch_socket()
    try:
        yield
    finally:
        reload(socket)
        signals.request_finished.connect(close_connection)


class CreateTaskTest(TestCase):
    def setUp(self):
        super(CreateTaskTest, self).setUp()
        apply_context(self, run_test_server())
        self.repo = InMemoryRepository()
        apply_context(self, mock_bpm_kernel(self.repo))

    def test(self):
        self.repo.set_data('bpmtest|tip|bpmtest/__init__.py', """
from bpm.kernel import AbstractComponent
from bpm.logging import get_logger

logger = get_logger()

class EmptyComponent(AbstractComponent):
    def start(self):
        logger.debug('Component start')
        self.complete()
        """)
        self.assertEqual([], list_tasks('bpmtest.EmptyComponent'))
        create_task('bpmtest.EmptyComponent')
        self.assertEqual(1, len(list_tasks('bpmtest.EmptyComponent')))
