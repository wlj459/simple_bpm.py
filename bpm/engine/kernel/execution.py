import types
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import full_write_guard, safe_builtins

from .models import Definition
from .utils import generate_salt

default_guarded_getattr = getattr  # No restrictions.


def default_guarded_getitem(ob, index):
    # No restrictions.
    return ob[index]


def default_guarded_write(ob):
    return ob


def db_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[db_import] %s' % line

    module = types.ModuleType(name)
    for definition_name in fromlist:
        try:
            definition = Definition.objects.get(name=definition_name)
        except Definition.DoesNotExist:
            pass
        else:
            executor = _Executor(definition)
            if executor.execute():
                locals().update(executor.locals())
                setattr(module, definition.name, locals()[definition.name])
                continue

        raise ImportError("cannot import name %s" % definition_name)

    return module


def file_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if fromlist:
        line = 'from %s import %s' % (name, ', '.join(fromlist))
    else:
        line = 'import %s' % name

    print '[file_import] %s' % line

    return __import__(name, _globals, _locals, fromlist, level)


def default_guarded_import(name, _globals=None, _locals=None, fromlist=None, level=-1):
    _globals = {} if _globals is None else _globals
    _locals = {} if _locals is None else _locals
    fromlist = [] if fromlist is None else fromlist

    if name == '__feature__' and 'backend_import' in fromlist:
        _globals['__import_flag__'] = True
        mod = types.ModuleType(name)
        setattr(mod, 'backend_import', None)
        return mod

    __import_flag__ = _globals.setdefault('__import_flag__', False)
    if __import_flag__:
        return db_import(name, _globals, _locals, fromlist, level)
    else:
        return file_import(name, _globals, _locals, fromlist, level)

class _Executor(object):

    def __init__(self, definition):
        self.definition = definition
        self.module_name = 'bpm.test'
        self.__globals = dict(__builtins__=safe_builtins)
        self.__locals = {}
        self.__succeeded = False

    def execute(self):
        self.__globals['__builtins__']['__import__'] = default_guarded_import
        self.__globals['__name__'] = self.module_name

        self.__globals['_getattr_'] = default_guarded_getattr
        self.__globals['_getitem_'] = default_guarded_getitem
        self.__globals['_write_'] = default_guarded_write

        try:
            code = compile_restricted(self.definition.text, '<string>', 'exec')
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


class Executor(object):

    def __init__(self, task, *args, **kwargs):
        self.task = task

    def execute(self):
        try:
            definition = Definition.objects.get(name=self.task.name)
        except Definition.DoesNotExist:
            return False
        else:
            self.executor = _Executor(definition)
            return self.executor.execute()

    def locals(self):
        if hasattr(self, 'executor'):
            return self.executor.locals()
