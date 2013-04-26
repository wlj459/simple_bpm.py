from django.dispatch import Signal

pre_exec = Signal(providing_args=['task_id', 'namespace'])

task_pending = Signal(providing_args=['task_id'])
task_ready = Signal(providing_args=['task_id'])
task_running = Signal(providing_args=['task_id'])
task_blocked = Signal(providing_args=['task_id'])
task_suspended = Signal(providing_args=['task_id'])
task_success = Signal(providing_args=['task_id'])
task_failure = Signal(providing_args=['task_id'])
task_revoked = Signal(providing_args=['task_id'])

task_acknowledge = Signal(providing_args=['task_id'])
