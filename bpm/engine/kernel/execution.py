from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins

from .models import Definition


class Executor(object):

    def __init__(self, task):
        self.task = task
        self.__namespace = dict(__builtins__=safe_builtins)
        self.__succeeded = False

    def __execute(self, source):
        self.__namespace['_getattr_'] = getattr
        self.__namespace['_getitem_'] = lambda obj, key: obj[key]
        self.__namespace['_write_'] = setattr
        try:
            exec compile_restricted(source, '<string>', 'exec') in self.__namespace
        except:
            # signals.exec_exception.send(sender=self)
            self.__succeeded = False
        else:
            self.__succeeded = True

        return self.__succeeded

    def execute(self):
        try:
            definition = Definition.objects.get(name=self.task.name)
        except Definition.DoesNotExist:
            self.__succeeded = False
            return False
        else:
            return self.__execute(definition.text)

    def get_definition(self):
        if self.__succeeded:
            return self.__namespace[self.task.name]
