"""
bpm.utils.random
================

An extension of built-in random module.
"""
from __future__ import absolute_import

import random as builtin_random

for name in dir(builtin_random):
    if not name.startswith('_'):
        locals()[name] = getattr(builtin_random, name)


def randstr(length=6):
    """
    >>> randstr() == randstr()
    False

    >>> len(randstr(8))
    8
    """
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([builtin_random.choice(ALPHABET) for _ in range(length)])
