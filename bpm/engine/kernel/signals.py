from django.dispatch import Signal

task_confirmed = Signal(providing_args=['instance'])

pre_callback = Signal(providing_args=['instance'])
post_callback = Signal(providing_args=['instance'])

pre_errback = Signal(providing_args=['instance'])
post_errback = Signal(providing_args=['instance'])