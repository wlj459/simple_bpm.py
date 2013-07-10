"""
bpm.kernel.signals
==================

Built-in task signals.

Signals
-------
"""
from django.dispatch import Signal

lazy_transit = Signal(providing_args=['task_id', 'to_state', 'countdown'])

task_ready = Signal(providing_args=['instance'])
task_running = Signal(providing_args=['instance'])
task_blocked = Signal(providing_args=['instance'])
task_suspended = Signal(providing_args=['instance'])
task_success = Signal(providing_args=['instance'])
task_failure = Signal(providing_args=['instance'])
task_revoked = Signal(providing_args=['instance'])

task_acknowledge = Signal(providing_args=['instance'])