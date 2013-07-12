"""
bpm.utils.collections
=====================

An extension of built-in collections module.
"""
from __future__ import absolute_import

import collections as builtin_collections

for name in dir(builtin_collections):
    if not name.startswith('_'):
        locals()[name] = getattr(builtin_collections, name)


class ConstantDict(dict):
    """ConstantDict is a subclass of :class:`dict`, implementing __setitem__
    method to avoid item assignment::

    >>> d = ConstantDict({'key': 'value'})
    >>> d['key'] = 'value'
    Traceback (most recent call last):
        ...
    TypeError: 'ConstantDict' object does not support item assignment
    """

    def __setitem__(self, key, value):
        raise TypeError("'%s' object does not support item assignment"
                        % self.__class__.__name__)