import os
import imp

from django.test import TestCase
from django.conf import settings

from bpm.engine.kernel import hg_importer


def simple_load_module_hook(path, source_code):
# without using RestrictedPython, so we can focus on the hg_importer logic
    compiled_code = compile(source_code, path, 'exec')
    exec_locals = {}
    exec_globals = dict(__builtins__)
    exec (compiled_code, exec_globals, exec_locals)
    module = imp.new_module(path)
    module.__dict__.update(exec_locals)
    return module


class ImportHookTest(TestCase):
    def setUp(self):
        super(ImportHookTest, self).setUp()
        hg_importer.setUp()
        self.OLD_REPO_ROOT = settings.REPO_ROOT
        settings.REPO_ROOT = os.path.join(os.path.dirname(__file__), 'hg_importer_test_repo_root')
        self.old_load_module_hook = hg_importer.load_module_hook
        hg_importer.load_module_hook = simple_load_module_hook

    def tearDown(self):
        super(ImportHookTest, self).tearDown()
        settings.REPO_ROOT = self.OLD_REPO_ROOT
        hg_importer.load_module_hook = self.old_load_module_hook
        hg_importer.tearDown()


    def test_simple_package(self):
        import simple_package

        self.assertEqual('world', simple_package.hello)