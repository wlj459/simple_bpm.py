from django.dispatch import Signal

pre_exec = Signal(providing_args=['instance', 'namespace'])

task_pending = Signal(providing_args=['instance'])
task_ready = Signal(providing_args=['instance'])
task_running = Signal(providing_args=['instance'])
task_blocked = Signal(providing_args=['instance'])
task_suspended = Signal(providing_args=['instance'])
task_success = Signal(providing_args=['instance'])
task_failure = Signal(providing_args=['instance'])
task_revoked = Signal(providing_args=['instance'])

task_acknowledge = Signal(providing_args=['instance'])
