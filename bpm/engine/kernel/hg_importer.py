import logging
import sys

from django.conf import settings
import mercurial.hg
import mercurial.ui
import mercurial.error

# signature: path, source_code => module
# will be implemented using RestrictedPython
load_module_hook = None

LOGGER = logging.getLogger(__name__)
MERCURIAL_SYS_PATH = '__MERCURIAL__'


def setUp():
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
        try:
            repo = mercurial.hg.repository(mercurial.ui.ui(), '%s/%s/' % (settings.REPO_ROOT, fullname))
            LOGGER.info('import %s is found as hg repo' % fullname)
            return Loader(repo)
        except mercurial.error.RepoError:
            LOGGER.debug('import %s not found as hg repo' % fullname)
            return None


class Loader(object):
    def __init__(self, repo):
        self.repo = repo

    def load_module(self, fullname):
        source_code = self.repo['tip']['%s/__init__.py' % fullname].data()
        if load_module_hook:
            return load_module_hook(fullname, source_code)
        else:
            LOGGER.error('missing load_module_hook')
            return None