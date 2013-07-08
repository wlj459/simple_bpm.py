import logging
import sys

from django.conf import settings
import mercurial.hg
import mercurial.ui
import mercurial.error
import imp

# signature: source_code, path => module
# will be implemented using RestrictedPython
compile_hook = None
# signature: compiled_code, module.__dict__ => void
exec_hook = None

LOGGER = logging.getLogger(__name__)
MERCURIAL_SYS_PATH = '__MERCURIAL__'


def setUp():
    assert compile_hook
    assert exec_hook
    if MERCURIAL_SYS_PATH not in sys.path:
        sys.path.append(MERCURIAL_SYS_PATH)
        sys.path_hooks.append(path_hook)

def tearDown():
    pass # TODO: unregister from sys.path and clear sys.modules


def path_hook(path):
    if MERCURIAL_SYS_PATH == path:
        return Finder()
    else:
        raise ImportError()


class Finder(object):
    def find_module(self, fullname, path=None):
        # print('find_module', fullname, path)
        repo_name = fullname.partition('.')[0]
        try:
            repo = mercurial.hg.repository(mercurial.ui.ui(), '%s/%s/' % (settings.REPO_ROOT, repo_name))
            LOGGER.info('import %s is found as hg repo' % repo_name)
            return Loader(repo)
        except mercurial.error.RepoError:
            LOGGER.debug('import %s not found as hg repo' % repo_name)
            return None


class Loader(object):
    def __init__(self, repo):
        self.repo = repo
        self.revision = repo['tip']

    def load_module(self, fullname):
        # print('load_module', fullname)
        is_package = self.is_package(fullname)
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = 'somewhere from __MERCURIAL__' # TODO describe exact location
        mod.__loader__ = self
        if is_package:
            mod.__path__ = [MERCURIAL_SYS_PATH]
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        compiled_code = self.get_code(fullname)
        exec_hook(compiled_code, mod.__dict__)
        return mod

    def get_code(self, fullname):
        return compile_hook(self.get_source(fullname), sys.modules[fullname].__file__)

    def is_package(self, fullname):
        return self._get_source(fullname)[0]

    def get_source(self, fullname):
        return self._get_source(fullname)[1]

    def _get_source(self, fullname):
        try:
            try:
                return True, self.get_data('%s/__init__.py' % fullname.replace('.', '/'))
            except IOError:
                pass
            try:
                return False, self.get_data('%s.py' % fullname.replace('.', '/'))
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

