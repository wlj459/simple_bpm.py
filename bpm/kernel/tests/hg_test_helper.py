import os.path
import contextlib

import mercurial.error


class InMemoryRepository(object):

    def __init__(self):
        self.data_dict = {}

    def __getitem__(self, repo_name):
        for key in self.data_dict:
            if key.startswith('%s|' % repo_name):
                return LookupEntry(self, [repo_name])
        raise mercurial.error.RepoError('not found')

    def data(self, path):
        if path in self.data_dict:
            return self.data_dict[path]
        else:
            raise mercurial.error.ManifestLookupError(path, '', '')

    def set_data(self, path, data):
        self.data_dict[path] = data


class LookupEntry(object):
    def __init__(self, repo, segments=()):
        self.repo = repo
        self.segments = list(segments)

    def __getitem__(self, segment):
        return LookupEntry(self.repo, self.segments + [segment])

    def data(self):
        return self.repo.data('|'.join(self.segments))

    def set_data(self, data):
        return self.repo.set_data('|'.join(self.segments), data)


@contextlib.contextmanager
def mock_hg(in_memory_repo, module):
    def mocked_repository(ui, path='', create=False):
        repo_name = os.path.basename(os.path.normpath(path))
        return in_memory_repo[repo_name]

    orig_repository = module.repository
    try:
        module.repository = mocked_repository
        yield
    finally:
        module.repository = orig_repository