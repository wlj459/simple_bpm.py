import contextlib
import socket

from django.test import TestCase

from django.core.wsgi import get_wsgi_application
import requests

from bpm.kernel.tests.context_test_helper import apply_context
import gevent
import gevent.monkey
import gevent.wsgi



# easy_install https://gevent.googlecode.com/files/gevent-1.0rc2.tar.gz
@contextlib.contextmanager
def run_test_server():
    def serve():
        application = get_wsgi_application()
        gevent.wsgi.WSGIServer(('', 8000), application).serve_forever()
    gevent.spawn(serve)
    gevent.monkey.patch_socket()
    try:
        yield
    finally:
        reload(socket)

class CreateTaskTest(TestCase):
    def setUp(self):
        super(CreateTaskTest, self).setUp()
        apply_context(self, run_test_server())

    def test(self):
        print(requests.get('http://127.0.0.1:8000/tasks/abc').content)
