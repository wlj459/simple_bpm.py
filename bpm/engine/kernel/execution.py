# -*- coding: utf-8 -*-

import imp
import os
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import full_write_guard, safe_builtins
from django.conf import settings
from mercurial import hg, ui
from mercurial.error import RepoError, RepoLookupError, ManifestLookupError

from . import features
from .log import BPMLogger

_ERR_MSG0 = 'No module named {!r}'
_ERR_MSG1 = 'cannot import name {!r}'

default_guarded_getattr = getattr  # No restrictions.


def default_guarded_getiter(obj):
    return list(obj)


def default_guarded_getitem(ob, index):
    # No restrictions.
    return ob[index]


def default_guarded_write(obj):
    if type(obj) in (dict, list) or hasattr(obj, '_guarded_writes'):
        return obj
    return WriteGuardWrapper(obj)


def _path_split(name):
    splits = name.split('.')
    modules = []
    for i, module_name in enumerate(splits):
        modules.append('.'.join(splits[:i + 1]))
    return modules
    # return zip(modules, map(lambda x: '/'.join(x.split('.') + ['__init__.py']), modules))


def _guess_path(module_name):
    splits = module_name.split('.')
    return ('/'.join(splits + ['__init__.py']), '/'.join(splits) + '.py')


def _call_with_frames_removed(f, *args, **kwargs):
    return f(*args, **kwargs)


def _find_module(name, package=None):
    pass


def _mercurial_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[_mercurial_import] %s' % line

    from bpm.engine.kernel import modules
    parent = name.rpartition('.')[0]
    if parent:
        if parent not in modules:
            _call_with_frames_removed(_mercurial_import, parent)
        if name in modules:
            return modules[name]

    loader = _find_module(name)
    if loader is None:
        raise ImportError(_ERR_MSG0.format(name))
    elif not name in modules:
        loader.load_module(name)
    module = modules[name]

    if parent:
        parent_module = modules[parent]
        setattr(parent_module, name.rpartition('.')[2], module)
    return module


def mercurial_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[mercurial_import] %s' % line

    # 首先尝试获取仓库，如果仓库不存在，则模块一定不存在
    repo_name = name.split('.')[0]
    print '[mercurial_import] try get repo %s' % repo_name
    try:
        repo = hg.repository(ui.ui(), '%s/%s/' % (settings.REPO_ROOT, repo_name))
    except RepoError:
        raise ImportError(_ERR_MSG0.format(repo_name))

    from bpm.engine.kernel import modules

    for module_name in _path_split(name):
        print '[mercurial_import] try import module %s' % module_name
        # 尝试从缓存获取
        if module_name in modules:
            print '[mercurial_import] get module %s from cache' % module_name
            continue

        # 找到仓库后，尝试一级一级加载模块
        revision = 'tip'  # TODO
        for path in _guess_path(module_name):
            print '[mercurial_import] try load module %s from %s' % (module_name, path)
            try:
                fctx = repo[revision][path]
            except RepoLookupError:
                # TODO: 做一些错误记录
                pass
            except ManifestLookupError:
                pass
            else:
                print '[mercurial_import] load module %s from %s' % (module_name, path)
                executor = BaseExecutor(module_name, fctx.data())
                if executor.execute():
                    module = imp.new_module(module_name)
                    print executor.locals()
                    for k, v in executor.locals().iteritems():
                        setattr(module, k, v)
                    modules.setdefault(module_name, module)
                    break
        else:
            raise ImportError(_ERR_MSG0.format(module_name))

    # print _globals[_CACHE_KEY]
    # 返回最后一个载入的模块
    print 'return %s' % name
    return modules[name]


# def internal_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
#     _globals = {} if _globals is None else _globals
#     _locals = {} if _locals is None else _locals
#     fromlist = [] if fromlist is None else fromlist
#
#     if fromlist:
#         line = 'from %s import %s' % (name, ', '.join(fromlist))
#     else:
#         line = 'import %s' % name
#
#     print '[internal_import] %s' % line
#
#     module = types.ModuleType(name)
#     for definition_name in fromlist:
#         try:
#             definition = Definition.objects.get(
#                 module=name,
#                 name=definition_name)
#         except Definition.DoesNotExist:
#             pass
#         else:
#             executor = _Executor(definition)
#             if executor.execute():
#                 locals().update(executor.locals())
#                 setattr(module, definition.name, locals()[definition.name])
#                 continue
#
#         raise ImportError("cannot import name %s" % definition_name)
#
#     return module


def original_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[original_import] %s' % line

    return __import__(name, _globals, _locals, fromlist)


def default_guarded_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[default_guarded_import] %s' % line

    __feature__ = _globals.setdefault('__feature__')
    if __feature__ and features.INTERNAL_IMPORT in __feature__:
        return mercurial_import(name, _globals, _locals, fromlist, level)
    else:
        mod = original_import(name, _globals, _locals, fromlist, level)

        for obj_name in fromlist:
            obj = getattr(mod, obj_name)
            if isinstance(obj, features._Feature):
                if __feature__:
                    _globals['__feature__'] = __feature__ + obj
                else:
                    _globals['__feature__'] = obj

        return mod


class _Executor(object):

    def __init__(self, definition):
        self.definition = definition
        self.module_name = str(definition.module)

    def execute(self):
        self.executor = BaseExecutor(self.module_name, self.definition.deploy.text)
        return self.executor.execute()

    def locals(self):
        if hasattr(self, 'executor'):
            return self.executor.locals()


class BaseExecutor(object):

    def __init__(self, module_name, src):
        self.module_name = module_name
        self.src = src
        self.__globals = dict(__builtins__=safe_builtins)
        self.__locals = {}
        self.__succeeded = False

        os.environ.setdefault('BPM_LOGGER_NAME', module_name)
        os.environ.setdefault('BPM_LOGGER_REVISION', 'tip')

    def execute(self):
        self.__globals['__builtins__']['__import__'] = default_guarded_import
        self.__globals['__name__'] = self.module_name

        self.__globals['_getattr_'] = default_guarded_getattr
        self.__globals['_getitem_'] = default_guarded_getitem
        self.__globals['_write_'] = default_guarded_write
        self.__globals['_print_'] = BPMLogger
        self.__globals['_getiter_'] = default_guarded_getiter

        try:
            code = compile_restricted(
                self.src,
                'mercurial: {!r}'.format(self.module_name),
                'exec')
        except:
            # signals.exec_exception.send(sender=self)
            import traceback
            traceback.print_exc()
        else:
            try:
                exec(code, self.__globals, self.__locals)
                self.__globals.update(self.__locals)
            except:
                import traceback
                traceback.print_exc()
            else:
                self.__succeeded = True

        return self.__succeeded

    def locals(self):
        if self.__succeeded:
            return self.__locals


# class Executor(object):
#
#     def __init__(self, task, *args, **kwargs):
#         self.task = task
#
#         splits = self.task.name.split('.')
#         self.module_name = '.'.join(splits[:-1])
#         self.object_name = splits[-1]
#
#     def execute(self):
#         try:
#             definition = Definition.objects.get(
#                 module=self.module_name,
#                 name=self.object_name)
#         except Definition.DoesNotExist:
#             return False
#         else:
#             self.executor = _Executor(definition)
#             return self.executor.execute()
#
#     def locals(self):
#         if hasattr(self, 'executor'):
#             return self.executor.locals()


class TaskExecutor(object):

    def __init__(self, task, revision='tip'):
        self.task = task
        self.revision = revision

        splits = str(self.task.name).split('.')
        self.repo_name = splits[0]
        self.module_name = '.'.join(splits[:-1])
        self.definition_name = splits[-1]

    def execute(self):
        try:
            repo = hg.repository(ui.ui(), '%s/%s/' % (settings.REPO_ROOT, self.repo_name))
        except RepoError:
            # TODO: 错误处理
            print 'Repository {!r} not found.'.format(self.repo_name)
            return False

        for module_name in _path_split(self.module_name):
            for path in _guess_path(module_name):
                try:
                    fctx = repo[self.revision][path]
                except RepoLookupError:
                    # TODO: 做一些错误记录
                    print 'RepoLookupError'
                    pass
                except ManifestLookupError:
                    print 'ManifestLookupError'
                    pass
                else:
                    executor = BaseExecutor(module_name, fctx.data())
                    if executor.execute():
                        break
            else:
                print 3
                return False

        for path in _guess_path(self.module_name):
            try:
                fctx = repo[self.revision][path]
            except RepoLookupError:
                print 'RepoLookupError'
            except ManifestLookupError:
                print 'ManifestLookupError'
            else:
                self.executor = BaseExecutor(self.module_name, fctx.data())
                return self.executor.execute()
        print 6
        return False

    def locals(self):
        if hasattr(self, 'executor'):
            return self.executor.locals()


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
