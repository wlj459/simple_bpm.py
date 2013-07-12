import os
import contextlib

from django.test import TestCase
from django.conf import settings

from bpm.kernel.sandbox import hg_importer
from .context_test_helper import apply_context


def simple_compile_hook(source_code, path):
# without using RestrictedPython, so we can focus on the hg_importer logic
    return compile(source_code, path, 'exec', dont_inherit=True)


def simple_exec_hook(compiled_code, module_dict):
    exec (compiled_code, {}, module_dict)


@contextlib.contextmanager
def setup_simple_hg_importer_hooks():
    orig_compile_hook = hg_importer.compile_hook
    orig_exec_hook = hg_importer.exec_hook
    try:
        hg_importer.compile_hook = simple_compile_hook
        hg_importer.exec_hook = simple_exec_hook
        yield
    finally:
        hg_importer.compile_hook = orig_compile_hook
        hg_importer.exec_hook = orig_exec_hook


@contextlib.contextmanager
def mock_repo_root(new_repo_root):
    try:
        orig_repo_root = settings.REPO_ROOT
        settings.REPO_ROOT = new_repo_root
        yield
    finally:
        settings.REPO_ROOT = orig_repo_root


class HgImporterTest(TestCase):
    def setUp(self):
        super(HgImporterTest, self).setUp()
        apply_context(self, mock_repo_root(os.path.join(os.path.dirname(__file__), 'hg_importer_test_repo_root')))
        apply_context(self, setup_simple_hg_importer_hooks())
        apply_context(self, hg_importer.enter_context())


    def test_simple_package(self):
        import simple_package

        self.assertTrue(hasattr(simple_package, '__path__'))
        self.assertEqual('simple_package', simple_package.__name__)
        self.assertEqual('simple_package', simple_package.__package__)
        self.assertEqual('world', simple_package.hello)

    def test_simple_module(self):
        import simple_package.simple_module

        self.assertFalse(hasattr(simple_package.simple_module, '__path__'))
        self.assertEqual('simple_package.simple_module', simple_package.simple_module.__name__)
        self.assertEqual('simple_package', simple_package.simple_module.__package__)
        self.assertEqual('world', simple_package.simple_module.hello)

    def test_package_import_module(self):
        import complex_package

        self.assertEqual('world', complex_package.hello)
        self.assertEqual('world', complex_package.sub_package.hello)