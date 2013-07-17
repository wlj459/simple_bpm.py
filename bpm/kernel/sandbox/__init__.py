import os
import contextlib
import importlib

import RestrictedPython
import RestrictedPython.Guards
import logging
import sys

from . import hg_importer
from bpm.logging import get_logger as bpm_get_logger

LOGGER = logging.getLogger(__name__)

@contextlib.contextmanager
def enter_context():
    try:
        enter()
        yield
    finally:
        exit()


def enter():
    hg_importer.compile_hook = restricted_compile
    hg_importer.exec_hook = restricted_exec
    hg_importer.enter()


def exit():
    hg_importer.exit()
    hg_importer.compile_hook = None
    hg_importer.exec_hook = None


def load_task_class(task_name):
    task_module_name, _, task_class_name = task_name.rpartition('.')
    task_module = importlib.import_module(task_module_name)
    task_class = getattr(task_module, task_class_name)
    return task_class


def restricted_compile(source_code, path):
    return RestrictedPython.compile_restricted(source_code, path, 'exec')


def restricted_import(*args, **kwargs):
    return __import__(*args, **kwargs) # can not pass __import__ directly to restricted mode execution


def restricted_exec(compiled_code, exec_locals):
    exec_globals = dict(__builtins__=RestrictedPython.Guards.safe_builtins)
    exec_globals['__builtins__']['__import__'] = restricted_import
    exec_globals['_getattr_'] = getattr
    exec_globals['_getitem_'] = default_guarded_getitem
    exec_globals['_write_'] = default_guarded_write
    exec_globals['_apply_'] = default_guarded_apply
    exec_globals['_print_'] = PrintHandler
    exec_globals['_getiter_'] = default_guarded_getiter
    exec_globals['__name__'] = exec_locals['__name__']
    orig_logger_name = os.environ.get('BPM_LOGGER_NAME')
    orig_logger_revision = os.environ.get('BPM_LOGGER_REVISION')
    os.environ['BPM_LOGGER_NAME'] = exec_locals['__name__']
    os.environ['BPM_LOGGER_REVISION'] = 'tip'
    try:
        exec (compiled_code, exec_globals, exec_locals)
    finally:
        exec_globals.update(exec_locals) # IMPORTANT!!! pickle.dumps will save the execution context
        if orig_logger_name and orig_logger_revision:
            os.environ['BPM_LOGGER_NAME'] = orig_logger_name
            os.environ['BPM_LOGGER_REVISION'] = orig_logger_revision


def default_guarded_apply(func, *args, **kwargs):
    return func(*args, **kwargs)


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