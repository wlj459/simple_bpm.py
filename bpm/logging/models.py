"""
bpm.logging.models
==================
"""
from __future__ import absolute_import

import logging

from django.db import models


class Record(models.Model):

    logger = models.SlugField(
        max_length=32,
    )
    revision = models.SlugField(
        max_length=32,
    )
    level = models.PositiveIntegerField(
        choices=(
            (logging.NOTSET, 'NOTSET'),
            (logging.DEBUG, 'DEBUG'),
            (logging.INFO, 'INFO'),
            (logging.WARNING, 'WARNING'),
            (logging.ERROR, 'ERROR'),
            (logging.CRITICAL, 'CRITICAL'),
        )
    )
    date_created = models.DateTimeField()
    module = models.CharField(
        max_length=256,
    )
    function = models.CharField(
        max_length=256,
    )
    lineno = models.IntegerField()
    message = models.TextField()