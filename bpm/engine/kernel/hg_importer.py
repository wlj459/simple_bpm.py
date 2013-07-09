import logging
import sys

from django.conf import settings
import mercurial.hg
import mercurial.ui
import mercurial.error
import imp
import contextlib

# signature: source_code, path => module
# will be implemented using RestrictedPython
compile_hook = None
# signature: compiled_code, module.__dict__ => void
exec_hook = None

LOGGER = logging.getLogger(__name__)
MERCURIAL_SYS_PATH = '__MERCURIAL__'

@contextlib.contextmanager
def enter_context():
    try:
        enter()
        yield
    finally:
        exit()

def enter():
    assert compile_hook
    assert exec_hook
    if MERCURIAL_SYS_PATH not in sys.path:
        sys.path.append(MERCURIAL_SYS_PATH)
        sys.path_hooks.append(path_hook)

def exit():
    pass # TODO: unregister from sys.path and clear sys.modules


def path_hook(path):
    if MERCURIAL_SYS_PATH == path:
        return HgFinder()
    else:
        raise ImportError()


class HgFinder(object):
    def __init__(self):
        self.loader_stack = []

    def find_module(self, fullname, path=None):
        print('find_module', fullname, path)
        repo_name = fullname.partition('.')[0]
        if self.loader_stack:
            current_loader = self.loader_stack[-1]
            if current_loader.can_load(fullname):
                return current_loader
        try:
            repo = mercurial.hg.repository(mercurial.ui.ui(), '%s/%s/' % (settings.REPO_ROOT, repo_name))
            LOGGER.info('import %s is found as hg repo' % repo_name)
            return HgLoader(self, repo)
        except mercurial.error.RepoError:
            LOGGER.debug('import %s not found as hg repo' % repo_name)
            return None

    def push_loader(self, loader):
        self.loader_stack.append(loader)

    def pop_loader(self):
        return self.loader_stack.pop()


class HgLoader(object):
    def __init__(self, finder, repo):
        self.finder = finder
        self.repo = repo
        self.revision = repo['tip']

    def load_module(self, fullname):
        print('load_module', fullname)
        is_package, source_code, module_file = self._get_source(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = module_file
        mod.__loader__ = self
        if is_package:
            mod.__path__ = [MERCURIAL_SYS_PATH]
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        compiled_code = self.get_code(fullname)
        try:
            self.finder.push_loader(SubModuleLoader(self, fullname))
            exec_hook(compiled_code, mod.__dict__)
        finally:
            self.finder.pop_loader()
        return mod

    def get_code(self, fullname):
        return compile_hook(self.get_source(fullname), sys.modules[fullname].__file__)

    def is_package(self, fullname):
        return self._get_source(fullname)[0]

    def get_source(self, fullname):
        return self._get_source(fullname)[1]

    def can_load(self, fullname):
        try:
            self._get_source(fullname)
            return True
        except ImportError:
            return False

    def _get_source(self, fullname):
        try:
            try:
                module_file = '%s/__init__.py' % fullname.replace('.', '/')
                return True, self.get_data(module_file), module_file
            except IOError:
                pass
            try:
                module_file = '%s.py' % fullname.replace('.', '/')
                return False, self.get_data(module_file), module_file
            except IOError as e:
                raise ImportError('adapted from IOError: %s' % e)
        except ImportError:
            raise
        except:
            LOGGER.exception('is_package failed')
            raise ImportError('adapted from: %s' % sys.exc_info()[1])

    def get_data(self, path):
        try:
            return self.revision[path].data()
        except mercurial.error.ManifestLookupError as e:
            raise IOError('adapted from ManifestLookupError: %s' % e)


class SubModuleLoader(object):
    def __init__(self, loader, parent):
        self.loader = loader
        self.parent = parent


    def load_module(self, fullname):
        return self.loader.load_module('%s.%s' % (self.parent, fullname))

    def get_code(self, fullname):
        return self.loader.get_code('%s.%s' % (self.parent, fullname))

    def is_package(self, fullname):
        return self.loader.is_package('%s.%s' % (self.parent, fullname))

    def get_source(self, fullname):
        return self.loader.get_source('%s.%s' % (self.parent, fullname))

    def can_load(self, fullname):
        return self.loader.can_load('%s.%s' % (self.parent, fullname))

    def get_data(self, path):
        return self.loader.get_data(path)