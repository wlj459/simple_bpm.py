"""
bpm.utils.random
================
"""
from __future__ import absolute_import

import random


def salt(length=6):
    """
    >>> salt() == salt()
    False

    >>> len(salt(8))
    8
    """
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(ALPHABET) for _ in range(length)])