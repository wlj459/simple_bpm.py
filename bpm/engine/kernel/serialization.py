import sys
import types

from .backends.base import BaseTaskBackend


class Serialization(object):

    def __init__(self, classes):
        self.classes = {}
        for cls in classes:
            if isinstance(cls, types.TypeType) and issubclass(cls, BaseTaskBackend):
                self.classes[cls] = cls.__module__

        self._target_modules = []

    def __enter__(self):
        modules = []
        for module_name in set(self.classes.values()):
            splits = module_name.split('.')
            for i in range(len(splits)):
                if i:
                    modules.append('.'.join(splits[:-i]))
                else:
                    modules.append('.'.join(splits[:]))

        for module_name in set(modules):
            if not module_name in sys.modules:
                self._target_modules.append(module_name)

        for cls, module_name in self.classes.iteritems():
            attr = cls.__name__
            obj = cls
            splits = module_name.split('.')
            for i in range(len(splits)):
                if i:
                    module_name = '.'.join(splits[:-i])
                else:
                    module_name = '.'.join(splits[:])

                mod = sys.modules.setdefault(module_name, types.ModuleType(module_name))
                mod.__dict__.setdefault(attr, obj)

                attr = splits[-i - 1]
                obj = mod

    def __exit__(self, exc_type, exc_val, exc_tb):
        for module_name in self._target_modules:
            del sys.modules[module_name]