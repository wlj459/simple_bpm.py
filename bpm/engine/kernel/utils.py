import random
import sys
import types


class PickleHelper(object):

    def __init__(self, cls):
        self.cls = cls

        cls_module = getattr(cls, '__module__', '')
        cls_name = getattr(cls, '__name__')
        self.abspath = '.'.join(
            [cls_module, cls_name] if cls_module else [cls_name])

        self._original_modules = {}
        self._target_modules = {}

    def __enter__(self):
        paths = self.abspath.split('.')
        targets = map(lambda i: ('.'.join(paths[:-i - 1]),
                                 paths[-i - 1]),
                      range(len(paths) - 1))

        obj = self.cls
        for module_name, obj_name in targets:
            if module_name in sys.modules:
                self._original_modules[module_name] = sys.modules[module_name]

            module = types.ModuleType(module_name)
            setattr(module, obj_name, obj)

            sys.modules[module_name] = module
            self._target_modules[module_name] = module

            obj = module

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k, v in self._target_modules.iteritems():
            if v == sys.modules.get(k):
                del sys.modules[k]

        for k, v in self._original_modules.iteritems():
            sys.modules[k] = v


def generate_salt(length=6):
    """
    >>> generate_salt() == generate_salt()
    False

    >>> len(generate_salt(8))
    8
    """
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(ALPHABET) for _ in range(length)])