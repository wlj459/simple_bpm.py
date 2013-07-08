import os

from django.test import TestCase
from django.conf import settings

from bpm.engine.kernel import hg_importer


def simple_compile_hook(source_code, path):
# without using RestrictedPython, so we can focus on the hg_importer logic
    return compile(source_code, path, 'exec', dont_inherit=True)


def simple_exec_hook(compiled_code, module_dict):
    exec (compiled_code, {}, module_dict)


class ImportHookTest(TestCase):
    def setUp(self):
        super(ImportHookTest, self).setUp()
        self.OLD_REPO_ROOT = settings.REPO_ROOT
        settings.REPO_ROOT = os.path.join(os.path.dirname(__file__), 'hg_importer_test_repo_root')
        self.old_compile_hook = hg_importer.compile_hook
        hg_importer.compile_hook = simple_compile_hook
        self.old_exec_hook = hg_importer.exec_hook
        hg_importer.exec_hook = simple_exec_hook
        hg_importer.setUp()

    def tearDown(self):
        super(ImportHookTest, self).tearDown()
        hg_importer.tearDown()
        settings.REPO_ROOT = self.OLD_REPO_ROOT
        hg_importer.compile_hook = self.old_compile_hook
        hg_importer.exec_hook = self.old_exec_hook


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