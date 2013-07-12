"""
bpm.logging
===========
"""
from __future__ import absolute_import

import logging
import os
import sys

from django.utils.timezone import now

from bpm.logging.tasks import log

_logger = logging.getLogger(__name__)

#################################################################################
# Miscellaneous module data
#################################################################################

_level_names = {
    logging.NOTSET: 'NOTSET',
    logging.DEBUG: 'DEBUG',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARNING',
    logging.ERROR: 'ERROR',
    logging.CRITICAL: 'CRITICAL',
}


def get_logger():
    return Logger(os.environ.get('BPM_LOGGER_NAME'),
                  os.environ.get('BPM_LOGGER_REVISION'))


def get_level_name(level):
    return _level_names.get(level, "Level %s" % level)

#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
#
if hasattr(sys, 'frozen'):  # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)


# next bit filched from 1.5.2's inspect.py
def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
# done filching


class LogRecord(object):

    def __init__(self, name, revision, level, module,
                 lineno, function, message, args):
        """
        Initialize a logging record with interesting information.
        """
        self.created = now()
        self.name = name
        self.revision = revision
        self.level = level
        self.module = module
        self.lineno = lineno
        self.function = function
        self.message = message
        if args and len(args) == 1 and isinstance(args[0], dict) and args[0]:
            args = args[0]
        self.args = args

    def __iter__(self):
        return iter((
            self.created,
            self.name,
            self.revision,
            self.level,
            self.module,
            self.lineno,
            self.function,
            self.message
        ))

    def get_message(self):
        """
        Return the message for this LogRecord.

        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        message = self.message
        if self.args:
            message = message % self.args
        return message


class Logger(object):

    def __init__(self, name=None, revision=None):
        self.name = name
        self.revision = revision

    def _handle(self, record):
        pass
        print '_handle'
        try:
            log.apply_async(args=tuple(record), retry=False)
        except:
            import traceback
            traceback.print_exc()
            _logger.info(record.get_message())

    def _log(self, level, message, args):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the reactors of this logger to handle the record.
        """
        if _srcfile:
            #IronPython doesn't track Python frames, so findCaller throws an
            #exception on some versions of IronPython. We trap it here so that
            #IronPython can use logging.
            try:
                mod, lno, func = self.find_caller()
            except ValueError:
                mod, lno, func = "(unknown module)", 0, "(unknown function)"
        else:
            mod, lno, func = "(unknown module)", 0, "(unknown function)"
        self._handle(self.make_record(level, mod, lno, func, message, args))

    def log(self, level, message, *args):
        if not isinstance(level, int):
            _level = logging.NOTSET

            if isinstance(level, basestring):
                level = level.lower().strip()

                if level in ('debug', 'info', 'warning', 'error', 'critical'):
                    _level = {
                        'debug': logging.DEBUG,
                        'info': logging.INFO,
                        'warning': logging.WARNING,
                        'error': logging.ERROR,
                        'critical': logging.CRITICAL,
                    }[level]

            level = _level

        self._log(level, message, args)

    def debug(self, message, *args):
        self.log(logging.DEBUG, message, *args)

    def info(self, message, *args):
        self.log(logging.INFO, message, *args)

    def warning(self, message, *args):
        self.log(logging.WARNING, message, *args)

    def error(self, message, *args):
        self.log(logging.ERROR, message, *args)

    def critical(self, message, *args):
        self.log(logging.CRITICAL, message, *args)

    def find_caller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown module)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv

    def make_record(self, level, module, lineno, function, message, args):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        return LogRecord(self.name, self.revision, level, module,
                         lineno, function, message, args)