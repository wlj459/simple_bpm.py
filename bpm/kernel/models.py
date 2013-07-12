# -*- coding: utf-8 -*-
"""
bpm.kernel.models
=================
"""

import json

from django.db import models, transaction

from bpm.kernel import signals, states
from bpm.utils import random


class TaskManager(models.Manager):

    def retry(self, instance, args=None, kwargs=None):
        assert isinstance(instance, self.model)
        assert instance.identifier_code
        assert instance.token_code

        if instance.state == states.FAILURE:
            identifier_code = instance.identifier_code
            token_code = instance.token_code

            if args is None:
                args = instance.args
            else:
                args = json.dumps(args)

            if kwargs is None:
                kwargs = instance.kwargs
            else:
                kwargs = json.dumps(kwargs)

            with transaction.commit_on_success():
                Task.objects.filter(pk=instance.pk)\
                            .update(token_code=None)
                task = Task(name=instance.name,
                            parent=instance.parent,
                            args=args,
                            kwargs=kwargs,
                            identifier_code=identifier_code,
                            token_code=token_code).save()

            return locals().get('task')

    def start(self, name, args=None, kwargs=None):
        if args is None:
            args = []
        else:
            assert isinstance(args, (list, tuple))

        if kwargs is None:
            kwargs = {}
        else:
            assert isinstance(kwargs, dict)

        task = Task(name=name,
                    args=json.dumps(args),
                    kwargs=json.dumps(kwargs))
        task.save()

        return task

    def transit(self, instance, to_state, **kwargs):
        assert isinstance(instance, self.model)

        appointment_flag = 0  # 没有处理预约
        if instance.appointment:
            if states.can_transit(instance.state, instance.appointment):
                appointment_flag = 1  # 处理了预约但未设置为预约状态
                if states.State(to_state) < states.State(instance.appointment):
                    appointment_flag = 2  # 设置为预约状态
                    to_state = instance.appointment

        if states.can_transit(instance.state, to_state):
            kwargs.update({
                'check_code': random.randstr(),
                'state': to_state,
            })
            if appointment_flag:  # 一旦处理了预约，就将其置空
                kwargs['appointment'] = ''
            if to_state in states.ARCHIVE_STATES:
                kwargs['snapshot'] = ''

            rows = self.model.objects.filter(
                pk=instance.pk,
                check_code=instance.check_code
            ).update(**kwargs)

            if rows:
                for k, v in kwargs.iteritems():
                    setattr(instance, k, v)

                state_change_signal = getattr(signals,
                                              'task_' + to_state.lower())

                if state_change_signal:
                    state_change_signal.send(sender=instance.__class__,
                                             instance=instance)

                if appointment_flag != 2:
                    return True

        return False


class Task(models.Model):

    name = models.CharField(
        max_length=100,
    )
    parent = models.ForeignKey(
        'self',
        related_name='sub_tasks',
        null=True,
        blank=True,
    )

    # inputs and outputs
    args = models.TextField(
        blank=True,
    )
    kwargs = models.TextField(
        blank=True,
    )

    data = models.TextField()
    ex_data = models.TextField()
    return_code = models.IntegerField(
        blank=True,
        null=True,
    )

    state = models.CharField(
        max_length=16,
        choices=zip(states.ALL_STATES, states.ALL_STATES),
        default=states.PENDING,
    )
    appointment = models.CharField(
        max_length=16,
        choices=zip(states.APPOINTMENT_STATES, states.APPOINTMENT_STATES),
        default='',
        blank=True,
    )

    identifier_code = models.SlugField(
        max_length=6,
        null=True,
    )
    token_code = models.SlugField(
        max_length=6,
        null=True,
    )
    snapshot = models.TextField()
    ack = models.PositiveSmallIntegerField(
        default=0,
    )
    check_code = models.SlugField(
        max_length=6,
        default=random.randstr(),
    )
    ttl = models.PositiveSmallIntegerField(
        default=0,
    )

    objects = TaskManager()

    class Meta:
        unique_together = ('identifier_code', 'token_code')

    def __unicode__(self):
        return unicode("[#%d] %s" % (
            self.id,
            self.name
        ))

    def appoint(self, to_state):
        if to_state in states.APPOINTMENT_STATES:
            return self.transit(to_state, appointment=True)

    def complete(self, data=None, ex_data=None, return_code=0):
        if self.state in (states.PENDING, states.RUNNING):
            kwargs = {
                'return_code': return_code,
            }

            if data is not None:
                kwargs['data'] = json.dumps(data)
            if ex_data is not None:
                kwargs['ex_data'] = json.dumps(ex_data)

            if return_code:
                to_state = states.FAILURE
            else:
                to_state = states.SUCCESS

            self.transit(to_state, **kwargs)

    def transit(self, to_state, appointment=False, **kwargs):
        if appointment:
            rows = self.__class__.objects.filter(pk=self.pk,
                                                 check_code=self.check_code)\
                                         .update(appointment=to_state)

            return True if rows else False
        else:
            return self.__class__.objects.transit(self, to_state, **kwargs)

    def transit_lazy(self, to_state, countdown=10):
        signals.lazy_transit.send(sender=self.__class__,
                                  task_id=self.pk,
                                  to_state=to_state,
                                  countdown=countdown)