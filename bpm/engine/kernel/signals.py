from django.dispatch import Signal

task_ready = Signal(providing_args=['instance', 'countdown'])
task_running = Signal(providing_args=['instance', 'countdown'])
task_blocked = Signal(providing_args=['instance', 'countdown'])
task_suspended = Signal(providing_args=['instance', 'countdown'])
task_success = Signal(providing_args=['instance', 'countdown'])
task_failure = Signal(providing_args=['instance', 'countdown'])
task_revoked = Signal(providing_args=['instance', 'countdown'])

task_acknowledge = Signal(providing_args=['instance'])
