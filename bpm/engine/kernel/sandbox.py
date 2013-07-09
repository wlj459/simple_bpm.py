import os
import contextlib

import RestrictedPython
import RestrictedPython.Guards

from . import hg_importer
from bpm.log import get_logger as bpm_get_logger


@contextlib.contextmanager
def enter_context():
    try:
        enter()
        yield
    finally:
        exit()


def enter():
    hg_importer.compile_hook = restricted_compile
    hg_importer.exec_hook = RestrictedExecutor()
    hg_importer.enter()


def exit():
    hg_importer.exit()
    hg_importer.compile_hook = None
    hg_importer.exec_hook = None


def restricted_compile(source_code, path):
    return RestrictedPython.compile_restricted(source_code, path, 'exec')


class RestrictedExecutor(object):
    def __init__(self):
        self.__globals = dict(__builtins__=RestrictedPython.Guards.safe_builtins)
        self.__globals['_getattr_'] = getattr
        self.__globals['_getitem_'] = default_guarded_getitem
        self.__globals['_write_'] = default_guarded_write
        self.__globals['_print_'] = PrintHandler
        self.__globals['_getiter_'] = default_guarded_getiter


    def __call__(self, compiled_code, exec_locals):
        # TODO maintain a stack
        os.environ.setdefault('BPM_LOGGER_NAME', exec_locals['__name__'])
        os.environ.setdefault('BPM_LOGGER_REVISION', 'tip')
        exec (compiled_code, self.__globals, exec_locals)


def default_guarded_getitem(ob, index):
    # No restrictions.
    return ob[index]


def default_guarded_write(obj):
    if type(obj) in (dict, list) or hasattr(obj, '_guarded_writes'):
        return obj
    return WriteGuardWrapper(obj)


def default_guarded_getiter(obj):
    return list(obj)


class PrintHandler(object):
    def __init__(self):
        self.loggers = {}
        self.current_line = []

    def write(self, text):
        if '\n' == text:
            self.get_logger(
                os.environ.get('BPM_LOGGER_NAME'),
                os.environ.get('BPM_LOGGER_REVISION')).info(
                ''.join(self.current_line))
            self.current_line = []
        else:
            self.current_line.append(text)

    def get_logger(self, logger_name, logger_revision):
        logger_key = (logger_name, logger_revision)
        if logger_key not in self.loggers:
            self.loggers[logger_key] = bpm_get_logger()
        return self.loggers[logger_key]

class WriteGuardWrapper(object):
    def __init__(self, obj):
        self.__dict__['obj'] = obj

    def __len__(self):
        # Required for slices with negative bounds.
        return len(self.obj)

    def __write_guard__(self, method_name, message, *args):
        try:
            method = getattr(self.obj, method_name)
        except AttributeError:
            raise TypeError(message)
        method(*args)

    def __setitem__(self, key, value):
        self.__write_guard__(
            '__guarded_setitem__',
            'object does not support item or slice assignment',
            key,
            value)

    def __delitem__(self, key):
        self.__write_guard__(
            '__guarded_delitem__',
            'object does not support item or slice assignment',
            key)

    def __setattr__(self, key, value):
        self.__write_guard__(
            '__guarded_setattr__',
            'attribute-less object (assign or del)',
            key,
            value)

    def __delattr__(self, item):
        self.__write_guard__(
            '__guarded_delattr__',
            'attribute-less object (assign or del)',
            item)