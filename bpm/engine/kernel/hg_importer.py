import logging
import sys

from django.conf import settings
import mercurial.hg
import mercurial.ui
import mercurial.error
import imp
import contextlib

# signature: source_code, path => module
compile_hook = None
# signature: compiled_code, module.__dict__ => void
exec_hook = None

LOGGER = logging.getLogger(__name__)
MERCURIAL_SYS_PATH = '__MERCURIAL__'
current_finder = None

@contextlib.contextmanager
def enter_context():
    try:
        enter()
        yield
    finally:
        exit()

def enter():
    global current_finder
    assert current_finder is None
    current_finder = HgFinder() # TODO: adding versioning to finder
    assert compile_hook
    assert exec_hook
    if MERCURIAL_SYS_PATH not in sys.path:
        sys.path.append(MERCURIAL_SYS_PATH)
        sys.path_hooks.append(path_hook)

def exit():
    global current_finder
    sys.path.remove(MERCURIAL_SYS_PATH)
    sys.path_hooks.remove(path_hook)
    if MERCURIAL_SYS_PATH in sys.path_importer_cache:
        del sys.path_importer_cache[MERCURIAL_SYS_PATH]
    try:
        current_finder.unload()
    finally:
        current_finder = None

def path_hook(path):
    if MERCURIAL_SYS_PATH == path:
        return current_finder
    else:
        raise ImportError()


class HgFinder(object):
    def __init__(self):
        self.loader_stack = []
        self.loaded_modules = {}

    def find_module(self, fullname, path=None):
        LOGGER.debug('find_module: %s %s' % (fullname, path))
        if fullname.endswith('.'):
            return None
        repo_name = fullname.partition('.')[0]
        if self.loader_stack:
            current_loader = self.loader_stack[-1]
            if current_loader.can_load(fullname):
                return current_loader
        try:
            repo = mercurial.hg.repository(mercurial.ui.ui(), '%s/%s/' % (settings.REPO_ROOT, repo_name))
            loader = HgLoader(self, repo)
            if loader.can_load(fullname):
                LOGGER.debug('%s is found as hg repo' % repo_name)
                return loader
            else:
                LOGGER.debug('%s not found in hg repo %s' % (fullname, repo_name))
                return None
        except mercurial.error.RepoError:
            LOGGER.debug('%s not found as hg repo' % repo_name)
            return None

    def push_loader(self, loader):
        self.loader_stack.append(loader)

    def pop_loader(self):
        return self.loader_stack.pop()

    def add_loaded_module(self, mod):
        self.loaded_modules[mod.__name__] = mod

    def unload(self):
        LOGGER.debug('unload %s' % self.loaded_modules)
        for module_name in self.loaded_modules:
            if module_name in sys.modules:
                del sys.modules[module_name]


class HgLoader(object):
    def __init__(self, finder, repo):
        self.finder = finder
        self.repo = repo
        self.revision = repo['tip']

    def load_module(self, fullname):
        LOGGER.debug('load_module: %s' % fullname)
        is_package, source_code, module_file = self._get_source(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = module_file
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
        self.finder.add_loaded_module(mod)
        LOGGER.debug('loaded %s' % mod)
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